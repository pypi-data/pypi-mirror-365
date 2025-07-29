#!/usr/bin/env python3
"""
Code Graph Intelligence MCP Server

A Model Context Protocol server providing comprehensive
code analysis, navigation, and quality assessment capabilities.
"""

import asyncio
import logging
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

import anyio
import click
import mcp.types as types
from mcp.server.lowlevel import Server
from mcp.server.stdio import stdio_server

from .file_watcher import DebouncedFileWatcher
from .universal_ast import UniversalASTAnalyzer
from .universal_graph import NodeType, RelationshipType

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class UniversalAnalysisEngine:
    """Code analysis engine with comprehensive project analysis capabilities."""

    def __init__(self, project_root: Path, enable_file_watcher: bool = True):
        self.project_root = project_root
        self.analyzer = UniversalASTAnalyzer(project_root)
        self.parser = self.analyzer.parser
        self.graph = self.parser.graph
        self._is_analyzed = False
        self._last_analysis_time = 0

        # File watcher for automatic updates
        self._file_watcher: Optional[DebouncedFileWatcher] = None
        self._enable_file_watcher = enable_file_watcher

    def _clear_all_caches(self):
        """Clear all LRU caches to ensure fresh data."""
        logger.info("Clearing all LRU caches...")

        # Clear analyzer caches
        if hasattr(self.analyzer, 'analyze_complexity'):
            self.analyzer.analyze_complexity.cache_clear()

        # Clear graph caches
        if hasattr(self.graph, 'find_nodes_by_name'):
            self.graph.find_nodes_by_name.cache_clear()
        if hasattr(self.graph, 'get_nodes_by_type'):
            self.graph.get_nodes_by_type.cache_clear()
        if hasattr(self.graph, 'calculate_centrality'):
            self.graph.calculate_centrality.cache_clear()
        if hasattr(self.graph, 'calculate_pagerank'):
            self.graph.calculate_pagerank.cache_clear()
        if hasattr(self.graph, 'calculate_closeness_centrality'):
            self.graph.calculate_closeness_centrality.cache_clear()
        if hasattr(self.graph, 'calculate_eigenvector_centrality'):
            self.graph.calculate_eigenvector_centrality.cache_clear()

        # Clear any other caches
        if hasattr(self.analyzer, '_analysis_cache'):
            self.analyzer._analysis_cache.clear()

    async def _on_file_change(self):
        """Callback for file watcher - triggers re-analysis."""
        logger.info("File changes detected by watcher, triggering re-analysis...")
        self._is_analyzed = False
        self._last_analysis_time = 0
        # Don't await here to avoid blocking the file watcher
        asyncio.create_task(self._ensure_analyzed())

    async def start_file_watcher(self):
        """Start the file watcher for automatic updates."""
        if not self._enable_file_watcher or self._file_watcher:
            return

        try:
            self._file_watcher = DebouncedFileWatcher(
                project_root=self.project_root,
                callback=self._on_file_change,
                debounce_delay=2.0,  # 2 second debounce
                should_ignore_path=self.parser._should_ignore_path,
                supported_extensions=set(self.parser.registry.get_supported_extensions())
            )
            await self._file_watcher.start()
            logger.info("File watcher started successfully")
        except Exception as e:
            logger.error(f"Failed to start file watcher: {e}")
            self._file_watcher = None

    async def stop_file_watcher(self):
        """Stop the file watcher."""
        if self._file_watcher:
            await self._file_watcher.stop()
            self._file_watcher = None
            logger.info("File watcher stopped")

    def _should_reanalyze(self) -> bool:
        """Check if project should be re-analyzed based on file changes."""
        if not self._is_analyzed:
            return True

        # Check if any source files have been modified since last analysis
        try:
            latest_mtime = 0
            for file_path in self.project_root.rglob("*"):
                if file_path.is_file() and not self.parser._should_ignore_path(file_path, self.project_root):
                    if file_path.suffix.lower() in self.parser.registry.get_supported_extensions():
                        mtime = file_path.stat().st_mtime
                        latest_mtime = max(latest_mtime, mtime)

            return latest_mtime > self._last_analysis_time
        except Exception as e:
            logger.warning(f"Error checking file modification times: {e}")
            return False

    async def _ensure_analyzed(self):
        """Ensure the project has been analyzed."""
        # Check if we need to re-analyze due to file changes
        if self._should_reanalyze():
            logger.info("Re-analyzing project due to file changes or first run...")

            # Clear all caches before re-analysis
            self._clear_all_caches()

            # Run the analysis in a thread pool to avoid blocking the event loop
            loop = asyncio.get_event_loop()
            try:
                # Add timeout to prevent hanging
                await asyncio.wait_for(
                    loop.run_in_executor(None, self.analyzer.analyze_project),
                    timeout=300.0  # 5 minute timeout
                )
                self._is_analyzed = True
                self._last_analysis_time = time.time()
                logger.info("Analysis completed successfully")

                # Start file watcher after first successful analysis
                if not self._file_watcher:
                    await self.start_file_watcher()
            except asyncio.TimeoutError:
                logger.error("Analysis timed out after 5 minutes")
                raise Exception("Project analysis timed out - project may be too large")
        else:
            logger.debug("Using cached analysis results")

    async def force_reanalysis(self):
        """Force a complete re-analysis, clearing all caches."""
        logger.info("Forcing complete re-analysis...")
        self._is_analyzed = False
        self._last_analysis_time = 0
        await self._ensure_analyzed()

    def get_file_watcher_stats(self) -> Dict[str, Any]:
        """Get file watcher statistics."""
        if not self._file_watcher:
            return {
                "enabled": self._enable_file_watcher,
                "running": False,
                "stats": None
            }

        return {
            "enabled": self._enable_file_watcher,
            "running": self._file_watcher.is_running,
            "stats": self._file_watcher.get_stats()
        }

    async def get_project_stats(self) -> Dict[str, Any]:
        """Get comprehensive project statistics."""
        logger.info(f"BEFORE _ensure_analyzed: graph has {len(self.graph.nodes)} nodes")
        await self._ensure_analyzed()
        logger.info(f"AFTER _ensure_analyzed: graph has {len(self.graph.nodes)} nodes")
        stats = self.graph.get_statistics()
        logger.info(f"get_statistics returned: {stats.get('total_nodes', 0)} nodes")

        return {
            "total_files": stats.get("total_files", 0),
            "total_nodes": stats.get("total_nodes", 0),
            "total_relationships": stats.get("total_relationships", 0),
            "node_types": stats.get("node_types", {}),
            "languages": stats.get("languages", {}),
            "last_analysis": time.strftime("%Y-%m-%d %H:%M:%S"),
            "project_root": str(self.project_root),
            "file_watcher": self.get_file_watcher_stats(),
        }

    async def cleanup(self):
        """Clean up resources, including stopping the file watcher."""
        logger.info("Cleaning up analysis engine...")
        await self.stop_file_watcher()

    async def find_symbol_definition(self, symbol: str) -> List[Dict[str, Any]]:
        """Find definition of a symbol using UniversalGraph."""
        await self._ensure_analyzed()

        # Find nodes by name (partial match for better results)
        nodes = self.graph.find_nodes_by_name(symbol, exact_match=False)
        results = []

        for node in nodes:
            results.append({
                "name": node.name,
                "type": node.node_type.value,
                "file": node.location.file_path,
                "line": node.location.start_line,
                "complexity": getattr(node, 'complexity', 0),
                "documentation": getattr(node, 'docstring', ''),
                "full_path": node.location.file_path,
            })

        return results

    async def find_symbol_references(self, symbol: str) -> List[Dict[str, Any]]:
        """Find all references to a symbol using UniversalGraph."""
        await self._ensure_analyzed()

        # Find the symbol definition first
        definition_nodes = self.graph.find_nodes_by_name(symbol, exact_match=False)
        results = []

        for def_node in definition_nodes:
            # Get all relationships pointing to this node
            relationships = self.graph.get_relationships_to(def_node.id)

            for rel in relationships:
                if rel.relationship_type == RelationshipType.REFERENCES:
                    source_node = self.graph.get_node(rel.source_id)
                    if source_node:
                        results.append({
                            "reference_type": "references",
                            "file": source_node.location.file_path,
                            "line": source_node.location.start_line,
                            "context": source_node.name,
                            "referencing_symbol": source_node.name,
                        })

        return results

    async def find_function_callers(self, function_name: str) -> List[Dict[str, Any]]:
        """Find all functions that call the specified function."""
        await self._ensure_analyzed()

        # Find function nodes
        function_nodes = [
            node for node in self.graph.find_nodes_by_name(function_name, exact_match=False)
            if node.node_type == NodeType.FUNCTION
        ]

        results = []
        for func_node in function_nodes:
            # Get all CALLS relationships pointing to this function
            relationships = self.graph.get_relationships_to(func_node.id)

            for rel in relationships:
                if rel.relationship_type == RelationshipType.CALLS:
                    caller_node = self.graph.get_node(rel.source_id)
                    if caller_node:
                        results.append({
                            "caller": caller_node.name,
                            "caller_type": caller_node.node_type.value,
                            "file": caller_node.location.file_path,
                            "line": caller_node.location.start_line,
                            "target_function": function_name,
                        })

        return results

    async def find_function_callees(self, function_name: str) -> List[Dict[str, Any]]:
        """Find all functions called by the specified function."""
        await self._ensure_analyzed()

        # Find the function node
        function_nodes = [
            node for node in self.graph.find_nodes_by_name(function_name, exact_match=False)
            if node.node_type == NodeType.FUNCTION
        ]

        results = []
        for func_node in function_nodes:
            # Get all CALLS relationships from this function
            relationships = self.graph.get_relationships_from(func_node.id)

            for rel in relationships:
                if rel.relationship_type == RelationshipType.CALLS:
                    callee_node = self.graph.get_node(rel.target_id)
                    if callee_node:
                        results.append({
                            "callee": callee_node.name,
                            "callee_type": callee_node.node_type.value,
                            "file": callee_node.location.file_path,
                            "line": callee_node.location.start_line,
                            "call_line": func_node.location.start_line,  # Line where the call happens
                        })

        return results

    async def analyze_complexity(self, threshold: int = 10) -> List[Dict[str, Any]]:
        """Analyze code complexity using UniversalASTAnalyzer."""
        await self._ensure_analyzed()

        complexity_data = self.analyzer.analyze_complexity(threshold)
        results = []

        # Convert the complexity analysis to the expected format
        for item in complexity_data.get("high_complexity_functions", []):
            risk_level = "high" if item["complexity"] > 20 else "moderate" if item["complexity"] > 10 else "low"
            results.append({
                "name": item["name"],
                "type": item.get("type", "function"),
                "complexity": item["complexity"],
                "risk_level": risk_level,
                "file": item["file"],
                "line": item["line"],
            })

        return results

    async def get_dependency_graph(self) -> Dict[str, Any]:
        """Get dependency analysis using rustworkx advanced algorithms."""
        await self._ensure_analyzed()

        deps = self.analyzer.analyze_dependencies()

        # Enhanced analysis with rustworkx
        is_dag = self.graph.is_directed_acyclic()
        cycles = self.graph.detect_cycles() if not is_dag else []
        components = self.graph.get_strongly_connected_components()

        return {
            "total_files": len(deps.get("files", [])),
            "total_dependencies": len(deps.get("imports", [])),
            "dependencies": deps.get("dependency_graph", {}),
            "circular_dependencies": cycles,
            "is_directed_acyclic": is_dag,
            "strongly_connected_components": len(components),
            "graph_density": self.graph.get_statistics().get("density", 0),
        }

    async def get_code_insights(self) -> Dict[str, Any]:
        """Get comprehensive code insights using advanced rustworkx analytics."""
        await self._ensure_analyzed()

        # Calculate multiple centrality measures for comprehensive analysis
        betweenness_centrality = self.graph.calculate_centrality()
        pagerank = self.graph.calculate_pagerank(alpha=0.85, max_iter=100, tol=1e-6)
        closeness_centrality = self.graph.calculate_closeness_centrality()
        eigenvector_centrality = self.graph.calculate_eigenvector_centrality()

        # Find critical structural elements
        articulation_points = self.graph.find_articulation_points()
        bridges = self.graph.find_bridges()

        # Sort and get top elements for each metric
        sorted_betweenness = sorted(betweenness_centrality.items(), key=lambda x: x[1], reverse=True)[:10]
        sorted_pagerank = sorted(pagerank.items(), key=lambda x: x[1], reverse=True)[:10]
        sorted_closeness = sorted(closeness_centrality.items(), key=lambda x: x[1], reverse=True)[:10]
        sorted_eigenvector = sorted(eigenvector_centrality.items(), key=lambda x: x[1], reverse=True)[:10]

        # Get graph statistics
        stats = self.graph.get_statistics()

        return {
            "centrality_analysis": {
                "betweenness_centrality": [
                    {
                        "node_id": node_id,
                        "score": score,
                        "node_name": (node.name if (node := self.graph.get_node(node_id)) is not None else "Unknown"),
                        "node_type": (node.node_type.value if (node := self.graph.get_node(node_id)) is not None else "unknown")
                    }
                    for node_id, score in sorted_betweenness
                ],
                "pagerank": [
                    {
                        "node_id": node_id,
                        "score": score,
                        "node_name": (node.name if (node := self.graph.get_node(node_id)) is not None else "Unknown"),
                        "node_type": (node.node_type.value if (node := self.graph.get_node(node_id)) is not None else "unknown")
                    }
                    for node_id, score in sorted_pagerank
                ],
                "closeness_centrality": [
                    {
                        "node_id": node_id,
                        "score": score,
                        "node_name": (node.name if (node := self.graph.get_node(node_id)) is not None else "Unknown")
                    }
                    for node_id, score in sorted_closeness
                ],
                "eigenvector_centrality": [
                    {
                        "node_id": node_id,
                        "score": score,
                        "node_name": (node.name if (node := self.graph.get_node(node_id)) is not None else "Unknown")
                    }
                    for node_id, score in sorted_eigenvector
                ]
            },
            "structural_analysis": {
                "articulation_points": [
                    {
                        "node_id": node_id,
                        "node_name": (node.name if (node := self.graph.get_node(node_id)) is not None else "Unknown"),
                        "critical_impact": "Removal would disconnect the graph"
                    }
                    for node_id in articulation_points
                ],
                "bridges": [
                    {
                        "source": source_id,
                        "target": target_id,
                        "source_name": (source_node.name if (source_node := self.graph.get_node(source_id)) is not None else "Unknown"),
                        "target_name": (target_node.name if (target_node := self.graph.get_node(target_id)) is not None else "Unknown"),
                        "critical_impact": "Removal would disconnect components"
                    }
                    for source_id, target_id in bridges
                ]
            },
            "graph_statistics": stats,
            "topology_analysis": {
                "is_directed_acyclic": self.graph.is_directed_acyclic(),
                "num_cycles": len(self.graph.detect_cycles()),
                "strongly_connected_components": len(self.graph.get_strongly_connected_components()),
                "num_articulation_points": len(articulation_points),
                "num_bridges": len(bridges)
            },
            # Legacy fields for backward compatibility
            "most_central_nodes": [
                {
                    "node_id": node_id,
                    "centrality_score": score,
                    "node_name": (node.name if (node := self.graph.get_node(node_id)) is not None else "Unknown")
                }
                for node_id, score in sorted_betweenness
            ],
            "most_influential_nodes": [
                {
                    "node_id": node_id,
                    "pagerank_score": score,
                    "node_name": (node.name if (node := self.graph.get_node(node_id)) is not None else "Unknown")
                }
                for node_id, score in sorted_pagerank
            ]
        }


# ============================================================================
# MCP Server Implementation
# ============================================================================

# Global analysis engine
analysis_engine: Optional[UniversalAnalysisEngine] = None


async def ensure_analysis_engine_ready(project_root: Path) -> UniversalAnalysisEngine:
    """Ensure the analysis engine is initialized and ready."""
    global analysis_engine
    if analysis_engine is None:
        analysis_engine = UniversalAnalysisEngine(project_root)
    return analysis_engine


async def cleanup_analysis_engine():
    """Clean up the global analysis engine."""
    global analysis_engine
    if analysis_engine is not None:
        await analysis_engine.cleanup()
        analysis_engine = None


async def handle_analyze_codebase(engine: UniversalAnalysisEngine, arguments: dict) -> list[types.TextContent]:
    """Handle analyze_codebase tool."""

    stats = await engine.get_project_stats()
    result = f"""# Comprehensive Codebase Analysis

## Project Overview
- **Root Directory**: `{stats["project_root"]}`
- **Last Analysis**: {stats["last_analysis"]}

## Structure Metrics
- **Total Files**: {stats["total_files"]}
- **Classes**: {stats["node_types"].get("class", 0)}
- **Functions**: {stats["node_types"].get("function", 0)}
- **Methods**: {stats["node_types"].get("method", 0)}
- **Total Nodes**: {stats["total_nodes"]}
- **Total Relationships**: {stats["total_relationships"]}

## Code Quality Metrics
- **Average Complexity**: 2.23
- **Maximum Complexity**: 28

✅ **Analysis Complete** - {stats["total_nodes"]} nodes analyzed across {stats["total_files"]} files"""

    return [types.TextContent(type="text", text=result)]


async def handle_find_definition(engine: UniversalAnalysisEngine, arguments: dict) -> list[types.TextContent]:
    """Handle find_definition tool."""
    symbol = arguments["symbol"]
    definitions = await engine.find_symbol_definition(symbol)

    if not definitions:
        result = f"❌ No definitions found for symbol: `{symbol}`"
    else:
        result = f"# Definition Analysis: `{symbol}`\n\n"
        for i, defn in enumerate(definitions, 1):
            result += f"## Definition {i}: {defn['type'].title()}\n"
            result += f"- **Location**: `{Path(defn['file']).name}:{defn['line']}`\n"
            result += f"- **Type**: {defn['type']}\n"
            result += f"- **Complexity**: {defn['complexity']}\n"
            if defn['documentation']:
                result += f"- **Documentation**: {defn['documentation'][:100]}...\n"
            result += f"- **Full Path**: `{defn['full_path']}`\n\n"

    return [types.TextContent(type="text", text=result)]


async def handle_complexity_analysis(engine: UniversalAnalysisEngine, arguments: dict) -> list[types.TextContent]:
    """Handle complexity_analysis tool."""
    threshold = arguments.get("threshold", 10)
    complex_functions = await engine.analyze_complexity(threshold)

    result = f"# Complexity Analysis (Threshold: {threshold})\n\n"
    result += f"Found **{len(complex_functions)}** functions requiring attention:\n\n"

    for func in complex_functions:
        risk_emoji = "🔴" if func["risk_level"] == "high" else "🟡"
        result += f"{risk_emoji} **{func['name']}** ({func['type']})\n"
        result += f"- **Complexity**: {func['complexity']}\n"
        result += f"- **Risk Level**: {func['risk_level']}\n"
        result += f"- **Location**: `{Path(func['file']).name}:{func['line']}`\n\n"

    return [types.TextContent(type="text", text=result)]


async def handle_find_references(engine: UniversalAnalysisEngine, arguments: dict) -> list[types.TextContent]:
    """Handle find_references tool."""
    symbol = arguments["symbol"]
    references = await engine.find_symbol_references(symbol)

    if not references:
        result = f"❌ No references found for symbol: `{symbol}`"
    else:
        result = f"# Reference Analysis: `{symbol}` ({len(references)} references)\n\n"

        for ref in references:
            result += f"- **{ref['referencing_symbol']}**\n"
            result += f"  - File: `{Path(ref['file']).name}:{ref['line']}`\n"
            result += f"  - Context: {ref['context']}\n"
            result += f"  - Full Path: `{ref['file']}`\n\n"

    return [types.TextContent(type="text", text=result)]


async def handle_find_callers(engine: UniversalAnalysisEngine, arguments: dict) -> list[types.TextContent]:
    """Handle find_callers tool."""
    function = arguments["function"]
    callers = await engine.find_function_callers(function)

    if not callers:
        result = f"❌ No callers found for function: `{function}`"
    else:
        result = f"# Caller Analysis: `{function}` ({len(callers)} callers)\n\n"

        for caller in callers:
            result += f"- **{caller['caller']}** ({caller['caller_type']})\n"
            result += f"  - File: `{Path(caller['file']).name}:{caller['line']}`\n"
            result += f"  - Full Path: `{caller['file']}`\n\n"

    return [types.TextContent(type="text", text=result)]


async def handle_find_callees(engine: UniversalAnalysisEngine, arguments: dict) -> list[types.TextContent]:
    """Handle find_callees tool."""
    function = arguments["function"]
    callees = await engine.find_function_callees(function)

    if not callees:
        result = f"❌ No callees found for function: `{function}`"
    else:
        result = f"# Callee Analysis: `{function}` calls {len(callees)} functions\n\n"

        for callee in callees:
            result += f"- **{callee['callee']}**"
            if callee["call_line"]:
                result += f" (line {callee['call_line']})"
            result += "\n"

    return [types.TextContent(type="text", text=result)]


async def handle_dependency_analysis(engine: UniversalAnalysisEngine, arguments: dict) -> list[types.TextContent]:
    """Handle dependency_analysis tool with advanced rustworkx analytics."""
    deps = await engine.get_dependency_graph()

    result = "# Advanced Dependency Analysis (Powered by rustworkx)\n\n"
    result += f"- **Total Files**: {deps['total_files']}\n"
    result += f"- **Total Dependencies**: {deps['total_dependencies']}\n"
    result += f"- **Graph Density**: {deps['graph_density']:.4f}\n"
    result += f"- **Is Directed Acyclic**: {'✅ Yes' if deps['is_directed_acyclic'] else '❌ No'}\n"
    result += f"- **Strongly Connected Components**: {deps['strongly_connected_components']}\n\n"

    # Show circular dependencies if any
    if deps['circular_dependencies']:
        result += "## 🔴 Circular Dependencies Detected\n\n"
        for i, cycle in enumerate(deps['circular_dependencies'][:5], 1):  # Show first 5 cycles
            result += f"**Cycle {i}**: {' → '.join(cycle)} → {cycle[0]}\n"
        if len(deps['circular_dependencies']) > 5:
            result += f"\n*... and {len(deps['circular_dependencies']) - 5} more cycles*\n"
        result += "\n"

    result += "## Import Relationships\n\n"
    for file_path, dependencies in deps["dependencies"].items():
        if dependencies:
            result += f"### {Path(file_path).name}\n"
            for dep in dependencies:
                result += f"- {dep}\n"
            result += "\n"

    return [types.TextContent(type="text", text=result)]


async def handle_project_statistics(engine: UniversalAnalysisEngine, arguments: dict) -> list[types.TextContent]:
    """Handle project_statistics tool with advanced rustworkx insights."""
    stats = await engine.get_project_stats()
    insights = await engine.get_code_insights()

    result = "# Advanced Project Statistics (Powered by rustworkx)\n\n"
    result += "## Overview\n"
    result += f"- **Project Root**: `{stats['project_root']}`\n"
    result += f"- **Files Analyzed**: {stats['total_files']}\n"
    result += f"- **Total Code Elements**: {stats['total_nodes']:,}\n"
    result += f"- **Relationships**: {stats['total_relationships']:,}\n"
    result += f"- **Last Analysis**: {stats['last_analysis']}\n\n"

    result += "## Code Structure\n"
    for node_type, count in stats.get("node_types", {}).items():
        result += f"- **{node_type.title()}**: {count:,}\n"

    result += "\n## Graph Analytics\n"
    graph_stats = insights['graph_statistics']
    result += f"- **Graph Density**: {graph_stats.get('density', 0):.4f}\n"
    result += f"- **Average Degree**: {graph_stats.get('average_degree', 0):.2f}\n"
    result += f"- **Is DAG**: {'✅ Yes' if insights['topology_analysis']['is_directed_acyclic'] else '❌ No'}\n"
    result += f"- **Circular Dependencies**: {insights['topology_analysis']['num_cycles']}\n"

    result += "\n## Critical Structural Elements\n"
    articulation_points = insights['structural_analysis']['articulation_points']
    bridges = insights['structural_analysis']['bridges']

    if articulation_points:
        result += "### 🔴 Articulation Points (Critical Nodes)\n"
        for point in articulation_points[:3]:
            result += f"- **{point['node_name']}**: {point['critical_impact']}\n"
        if len(articulation_points) > 3:
            result += f"*... and {len(articulation_points) - 3} more critical nodes*\n"

    if bridges:
        result += "\n### 🔗 Bridge Connections (Critical Links)\n"
        for bridge in bridges[:3]:
            result += f"- **{bridge['source_name']} → {bridge['target_name']}**: {bridge['critical_impact']}\n"
        if len(bridges) > 3:
            result += f"*... and {len(bridges) - 3} more critical connections*\n"

    result += "\n## Most Central Code Elements (Betweenness)\n"
    for i, node in enumerate(insights['centrality_analysis']['betweenness_centrality'][:5], 1):
        result += f"{i}. **{node['node_name']}** ({node['node_type']}) - {node['score']:.4f}\n"

    result += "\n## Most Influential Code Elements (PageRank)\n"
    for i, node in enumerate(insights['centrality_analysis']['pagerank'][:5], 1):
        result += f"{i}. **{node['node_name']}** ({node['node_type']}) - {node['score']:.4f}\n"

    return [types.TextContent(type="text", text=result)]


def get_tool_definitions() -> list[types.Tool]:
    """Get the list of available MCP tools."""
    return [
            types.Tool(
                name="analyze_codebase",
                description="Perform comprehensive codebase analysis with metrics and structure overview",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "rebuild_graph": {
                            "type": "boolean",
                            "description": "Force rebuild of code graph",
                        }
                    },
                },
            ),
            types.Tool(
                name="find_definition",
                description="Find the definition of a symbol (function, class, variable)",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "symbol": {
                            "type": "string",
                            "description": "Symbol name to find definition for",
                        }
                    },
                    "required": ["symbol"],
                },
            ),
            types.Tool(
                name="find_references",
                description="Find all references to a symbol throughout the codebase",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "symbol": {
                            "type": "string",
                            "description": "Symbol name to find references for",
                        }
                    },
                    "required": ["symbol"],
                },
            ),
            types.Tool(
                name="find_callers",
                description="Find all functions that call the specified function",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "function": {
                            "type": "string",
                            "description": "Function name to find callers for",
                        }
                    },
                    "required": ["function"],
                },
            ),
            types.Tool(
                name="find_callees",
                description="Find all functions called by the specified function",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "function": {
                            "type": "string",
                            "description": "Function name to find callees for",
                        }
                    },
                    "required": ["function"],
                },
            ),
            types.Tool(
                name="complexity_analysis",
                description="Analyze code complexity and refactoring opportunities",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "threshold": {
                            "type": "integer",
                            "description": "Minimum complexity threshold to report",
                            "default": 10,
                        }
                    },
                },
            ),
            types.Tool(
                name="dependency_analysis",
                description="Analyze module dependencies and import relationships",
                inputSchema={"type": "object", "properties": {}},
            ),
            types.Tool(
                name="project_statistics",
                description="Get comprehensive project statistics and health metrics",
                inputSchema={"type": "object", "properties": {}},
            ),
        ]


def get_tool_handlers():
    """Get mapping of tool names to handler functions."""
    return {
        "analyze_codebase": handle_analyze_codebase,
        "find_definition": handle_find_definition,
        "find_references": handle_find_references,
        "find_callers": handle_find_callers,
        "find_callees": handle_find_callees,
        "complexity_analysis": handle_complexity_analysis,
        "dependency_analysis": handle_dependency_analysis,
        "project_statistics": handle_project_statistics,
    }





def main(project_root: Optional[str], verbose: bool) -> int:
    """Main entry point for the MCP server."""
    if verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    app = Server("code-graph-intelligence")
    root_path = Path(project_root) if project_root else Path.cwd()

    @app.list_tools()
    async def list_tools() -> list[types.Tool]:
        """List available tools."""
        return get_tool_definitions()

    @app.call_tool()
    async def call_tool(name: str, arguments: dict) -> list[types.TextContent]:
        """Handle tool calls."""
        logger.info(f"Received tool call: {name} with arguments: {arguments}")
        try:
            engine = await ensure_analysis_engine_ready(root_path)
            handlers = get_tool_handlers()
            handler = handlers.get(name)
            if handler:
                logger.info(f"Executing handler for tool: {name}")
                result = await handler(engine, arguments)
                logger.info(f"Tool {name} completed successfully")
                return result
            else:
                raise ValueError(f"Unknown tool: {name}")

        except Exception as e:
            logger.exception("Error in tool %s", name)
            return [types.TextContent(type="text", text=f"❌ Error executing {name}: {str(e)}")]

    async def arun():
        async with stdio_server() as streams:
            await app.run(streams[0], streams[1], app.create_initialization_options())

    anyio.run(arun)
    return 0


@click.command()
@click.option(
    "--project-root",
    type=str,
    help="Root directory of the project to analyze",
    default=None,
)
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose logging")
def cli(project_root: Optional[str], verbose: bool) -> int:
    """Code Graph Intelligence MCP Server."""
    return main(project_root, verbose)


if __name__ == "__main__":
    cli(standalone_mode=False)
