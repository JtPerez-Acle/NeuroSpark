"""Analysis routes for the Agent Interaction Backend."""
from fastapi import APIRouter, Request, HTTPException, Query, Body
from fastapi.responses import JSONResponse
from typing import Dict, Any, List, Optional, Literal
import logging
from datetime import datetime, timedelta

from .analysis.network_analysis import NetworkAnalyzer

# Configure logging
logger = logging.getLogger("kqml-parser-backend")

# Create router
analysis_router = APIRouter()

def get_db(request: Request):
    """Get database instance from app state."""
    return request.app.state.db

async def get_graph_data(request, limit: int = 1000):
    """Helper to get graph data from database.
    
    For blockchain data, this returns wallet and contract nodes connected by transactions.
    """
    db = get_db(request)
    
    # First, ensure blockchain collections exist
    await db.setup_blockchain_collections()
    
    # Get blockchain network data with a limit
    network = await db.get_blockchain_network({
        "limit": limit
    })
    
    # Return network data - might be empty if no blockchain data exists yet
    return network

@analysis_router.get("/metrics",
    response_model=Dict[str, Any],
    summary="Get Graph Metrics",
    description="""Calculate various metrics for the graph using NetworkX.
    
    Metrics include:
    - Node and edge counts
    - Graph density
    - Average degree
    - Connectivity (strongly and weakly connected components)
    - Clustering coefficient
    - Diameter and average path length of largest component
    """,
    response_description="Graph metrics."
)
async def get_graph_metrics(
    request: Request,
    directed: bool = Query(True, description="Whether to treat the graph as directed"),
    link_limit: int = Query(1000, description="Maximum number of links to analyze")
) -> Dict[str, Any]:
    """Get graph metrics."""
    try:
        logger.info(f"Calculating graph metrics (directed={directed}, link_limit={link_limit})")
        graph_data = await get_graph_data(request, limit=link_limit)
        
        if not graph_data["nodes"] or not graph_data["links"]:
            return {"message": "Graph is empty", "metrics": {}}
            
        analyzer = NetworkAnalyzer(graph_data["nodes"], graph_data["links"], directed=directed)
        metrics = analyzer.get_basic_metrics()
        
        return {
            "message": "Graph metrics calculated successfully",
            "node_count": len(graph_data["nodes"]),
            "link_count": len(graph_data["links"]),
            "metrics": metrics
        }
    except Exception as e:
        logger.error(f"Error calculating graph metrics: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@analysis_router.get("/centrality",
    response_model=Dict[str, Any],
    summary="Get Node Centrality",
    description="""Calculate centrality metrics for nodes in the interaction graph.
    
    Centrality metrics include:
    - Degree centrality (in-degree and out-degree for directed graphs)
    - Betweenness centrality (nodes that bridge communities)
    - Closeness centrality (nodes that have short paths to all other nodes)
    - Eigenvector centrality (nodes connected to other important nodes)
    - PageRank (for directed graphs)
    
    These metrics help identify important agents in the interaction network.
    """,
    response_description="Node centrality measures."
)
async def get_centrality(
    request: Request,
    directed: bool = Query(True, description="Whether to treat the graph as directed"),
    top_n: Optional[int] = Query(10, description="Limit results to top N nodes"),
    link_limit: int = Query(1000, description="Maximum number of links to analyze"),
    normalized: bool = Query(True, description="Whether to normalize centrality values")
) -> Dict[str, Any]:
    """Get node centrality metrics."""
    try:
        logger.info(f"Calculating node centrality (directed={directed}, top_n={top_n})")
        graph_data = await get_graph_data(request, limit=link_limit)
        
        if not graph_data["nodes"] or not graph_data["links"]:
            return {"message": "Graph is empty", "centrality": {}}
            
        analyzer = NetworkAnalyzer(graph_data["nodes"], graph_data["links"], directed=directed)
        centrality = analyzer.get_centrality_metrics(top_n=top_n, normalized=normalized)
        
        return {
            "message": "Node centrality calculated successfully",
            "node_count": len(graph_data["nodes"]),
            "centrality": centrality
        }
    except Exception as e:
        logger.error(f"Error calculating centrality: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@analysis_router.get("/communities",
    response_model=Dict[str, Any],
    summary="Detect Communities",
    description="""Detect communities or clusters in the interaction graph.
    
    Supported community detection algorithms:
    - louvain: Fast modularity-based algorithm (default)
    - greedy: Greedy modularity optimization
    - label_propagation: Fast label propagation method
    - girvan_newman: Based on edge betweenness (slowest but often accurate)
    
    Community detection helps identify natural groupings of agents that interact more frequently with each other.
    """,
    response_description="Community detection results."
)
async def get_communities(
    request: Request,
    algorithm: str = Query("louvain", description="Community detection algorithm"),
    directed: bool = Query(False, description="Whether to treat the graph as directed"),
    link_limit: int = Query(1000, description="Maximum number of links to analyze")
) -> Dict[str, Any]:
    """Detect communities in the graph."""
    try:
        logger.info(f"Detecting communities with algorithm {algorithm}")
        graph_data = await get_graph_data(request, limit=link_limit)
        
        if not graph_data["nodes"] or not graph_data["links"]:
            return {"message": "Graph is empty", "communities": {}}
            
        analyzer = NetworkAnalyzer(graph_data["nodes"], graph_data["links"], directed=directed)
        communities = analyzer.detect_communities(algorithm=algorithm)
        
        return {
            "message": "Communities detected successfully",
            "node_count": len(graph_data["nodes"]),
            "algorithm": algorithm,
            "communities": communities
        }
    except Exception as e:
        logger.error(f"Error detecting communities: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@analysis_router.get("/layout",
    response_model=Dict[str, Any],
    summary="Get Graph Layout",
    description="""Generate layout coordinates for graph visualization.
    
    Supported layout algorithms:
    - spring: Force-directed layout based on Fruchterman-Reingold (default)
    - circular: Arrange nodes in a circle
    - kamada_kawai: Force-directed layout based on Kamada-Kawai algorithm
    - spectral: Layout based on the eigenvectors of the graph Laplacian
    - shell: Concentric circles layout
    - spiral: Arrange nodes in a spiral pattern
    - random: Random node positions
    
    These positions can be used for visualizing the interaction network.
    """,
    response_description="Node positions for visualization."
)
async def get_layout(
    request: Request,
    layout: str = Query("spring", description="Layout algorithm to use"),
    directed: bool = Query(True, description="Whether to treat the graph as directed"),
    dimensions: int = Query(2, description="Number of dimensions (2 or 3)"),
    scale: float = Query(100.0, description="Scale factor for the layout"),
    link_limit: int = Query(1000, description="Maximum number of links to analyze")
) -> Dict[str, Any]:
    """Get layout coordinates for graph visualization."""
    try:
        logger.info(f"Generating {layout} layout with {dimensions} dimensions")
        graph_data = await get_graph_data(request, limit=link_limit)
        
        if not graph_data["nodes"] or not graph_data["links"]:
            return {"message": "Graph is empty", "positions": {}}
            
        analyzer = NetworkAnalyzer(graph_data["nodes"], graph_data["links"], directed=directed)
        positions = analyzer.get_layout_positions(layout=layout, scale=scale, dimensions=dimensions)
        
        return {
            "message": f"{layout} layout generated successfully",
            "layout": layout,
            "dimensions": dimensions,
            "positions": positions
        }
    except Exception as e:
        logger.error(f"Error generating layout: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@analysis_router.get("/degree_centrality",
    response_model=Dict[str, Any],
    summary="Get Degree Centrality",
    description="""Get degree centrality for nodes in the graph.
    
    This endpoint is for compatibility with older tests.
    For more complete centrality metrics, use the /centrality endpoint.
    """,
    response_description="Degree centrality for nodes."
)
async def get_degree_centrality(
    request: Request,
    directed: bool = Query(True, description="Whether to treat the graph as directed"),
    link_limit: int = Query(1000, description="Maximum number of links to analyze")
) -> Dict[str, Any]:
    """Get degree centrality for nodes."""
    try:
        logger.info(f"Calculating degree centrality (directed={directed})")
        graph_data = await get_graph_data(request, limit=link_limit)
        
        if not graph_data["nodes"] or not graph_data["links"]:
            return {"message": "Graph is empty", "node_degrees": {}}
        
        analyzer = NetworkAnalyzer(graph_data["nodes"], graph_data["links"], directed=directed)
        centrality = analyzer.get_centrality_metrics()
        
        # Return in-degree centrality for directed graphs, regular degree for undirected
        if directed and "in_degree" in centrality:
            degree_centrality = centrality["in_degree"]
        elif not directed and "degree" in centrality:
            degree_centrality = centrality["degree"]
        else:
            degree_centrality = {}
        
        return {
            "message": "Degree centrality calculated successfully",
            "node_degrees": degree_centrality
        }
    except Exception as e:
        logger.error(f"Error calculating degree centrality: {str(e)}")
        return {
            "message": "Error calculating degree centrality",
            "node_degrees": {},
            "error": str(e)
        }

@analysis_router.get("/temporal",
    response_model=Dict[str, Any],
    summary="Get Temporal Analysis",
    description="""Analyze graph metrics over time using temporal windows.
    
    This endpoint divides interactions into time windows and calculates metrics for each window:
    - Node and edge counts over time
    - Graph density changes
    - Connectivity evolution
    - Other basic metrics
    
    This helps track how the interaction network evolves over time and identify patterns or trends.
    Smaller window sizes provide more granular analysis but require more processing.
    """,
    response_description="Temporal analysis of graph metrics."
)
async def get_temporal_analysis(
    request: Request,
    window_size: int = Query(86400, description="Window size in seconds (default: 1 day)"),
    max_windows: int = Query(30, description="Maximum number of windows to return"),
    directed: bool = Query(True, description="Whether to treat the graph as directed"),
    link_limit: int = Query(5000, description="Maximum number of links to analyze")
) -> Dict[str, Any]:
    """Analyze graph metrics over time."""
    try:
        logger.info(f"Generating temporal analysis with window size {window_size}s")
        graph_data = await get_graph_data(request, limit=link_limit)
        
        if not graph_data["nodes"] or not graph_data["links"]:
            return {"message": "Graph is empty", "temporal_metrics": {}}
            
        analyzer = NetworkAnalyzer(graph_data["nodes"], graph_data["links"], directed=directed)
        temporal_metrics = analyzer.get_temporal_metrics(
            window_size=timedelta(seconds=window_size),
            max_windows=max_windows
        )
        
        return {
            "message": "Temporal analysis completed successfully",
            "window_size_seconds": window_size,
            "max_windows": max_windows,
            "temporal_metrics": temporal_metrics
        }
    except Exception as e:
        logger.error(f"Error in temporal analysis: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@analysis_router.get("/visualization",
    response_model=Dict[str, Any],
    summary="Get Advanced Visualization Data",
    description="""Get complete network visualization data with enhanced metrics, layouts, and community detection.
    
    This endpoint combines multiple analysis features into one comprehensive dataset:
    - Node data with position coordinates based on selected layout algorithm
    - Centrality metrics for each node (if requested)
    - Community detection results with node assignments (if requested)
    - Basic graph metrics
    
    This is especially useful for creating advanced visualizations that encode multiple 
    dimensions of information (position, size, color, grouping) based on network properties.
    """,
    response_description="Enhanced network visualization data."
)
async def get_visualization(
    request: Request,
    layout: str = Query("spring", description="Layout algorithm to use"),
    directed: bool = Query(True, description="Whether to treat the graph as directed"),
    include_communities: bool = Query(False, description="Whether to include community detection"),
    include_metrics: bool = Query(False, description="Whether to include node metrics"),
    community_algorithm: str = Query("louvain", description="Community detection algorithm"),
    link_limit: int = Query(1000, description="Maximum number of links to analyze")
) -> Dict[str, Any]:
    """Get advanced network visualization data."""
    try:
        logger.info(f"Generating visualization data with layout {layout}")
        graph_data = await get_graph_data(request, limit=link_limit)
        
        if not graph_data["nodes"] or not graph_data["links"]:
            return {"message": "Graph is empty", "visualization": {"nodes": [], "links": []}}
        
        analyzer = NetworkAnalyzer(graph_data["nodes"], graph_data["links"], directed=directed)
        visualization_data = analyzer.get_network_visualization_data(
            layout=layout,
            include_communities=include_communities,
            include_metrics=include_metrics,
            community_algorithm=community_algorithm
        )
        
        return {
            "message": "Visualization data generated successfully",
            "visualization": visualization_data
        }
    except Exception as e:
        logger.error(f"Error generating visualization data: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))