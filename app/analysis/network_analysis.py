"""NetworkX-based analysis of agent interaction graphs."""
import networkx as nx
import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional, Tuple, Union, Set
from datetime import datetime, timedelta
import logging
from loguru import logger

class NetworkAnalyzer:
    """Provides graph analysis capabilities using NetworkX."""
    
    def __init__(self, nodes: List[Dict], links: List[Dict], directed: bool = True):
        """Initialize with nodes and links data.
        
        Args:
            nodes: List of node dictionaries with at least an 'id' field
            links: List of link dictionaries with 'source' and 'target' fields
            directed: Whether to treat the graph as directed (default: True)
        """
        self.nodes = nodes
        self.links = links
        self.directed = directed
        self.graph = self._build_graph(nodes, links, directed)
        
    def _build_graph(self, nodes: List[Dict], links: List[Dict], directed: bool) -> Union[nx.Graph, nx.DiGraph]:
        """Convert nodes and links to a NetworkX graph.
        
        Args:
            nodes: List of node dictionaries
            links: List of link dictionaries
            directed: Whether to create a directed graph
            
        Returns:
            NetworkX graph object
        """
        G = nx.DiGraph() if directed else nx.Graph()
        
        # Add nodes with all attributes
        # Make deep copies to avoid modifying original data
        for node in nodes:
            node_copy = node.copy()
            if "id" not in node_copy:
                logger.warning(f"Node missing id field, skipping: {node_copy}")
                continue
            
            node_id = node_copy.pop("id")
            G.add_node(node_id, **node_copy)
            
        # Add edges with all attributes
        # Make deep copies to avoid modifying original data
        for link in links:
            link_copy = link.copy()
            
            # Get source and target
            source = None
            if "source" in link_copy:
                source = link_copy.pop("source")
            elif "from" in link_copy:
                source = link_copy.pop("from")
                
            target = None    
            if "target" in link_copy:
                target = link_copy.pop("target")
            elif "to" in link_copy:
                target = link_copy.pop("to")
            
            if source is None or target is None:
                logger.warning(f"Skipping link with missing source or target: {link_copy}")
                continue
                
            # Skip self-loops if needed
            if source == target:
                continue
                
            G.add_edge(source, target, **link_copy)
            
        return G
    
    def get_basic_metrics(self) -> Dict[str, Any]:
        """Calculate basic graph metrics.
        
        Returns:
            Dictionary of graph metrics
        """
        metrics = {
            "node_count": self.graph.number_of_nodes(),
            "edge_count": self.graph.number_of_edges(),
            "density": nx.density(self.graph),
            "average_degree": sum(dict(self.graph.degree()).values()) / self.graph.number_of_nodes() if self.graph.number_of_nodes() > 0 else 0,
        }
        
        # For directed graphs
        if self.directed:
            metrics.update({
                "is_strongly_connected": nx.is_strongly_connected(self.graph),
                "strongly_connected_components": nx.number_strongly_connected_components(self.graph),
                "is_weakly_connected": nx.is_weakly_connected(self.graph),
                "weakly_connected_components": nx.number_weakly_connected_components(self.graph),
            })
        else:
            # For undirected graphs
            metrics.update({
                "is_connected": nx.is_connected(self.graph),
                "connected_components": nx.number_connected_components(self.graph),
            })
            
        # Calculate clustering and average path length safely
        try:
            metrics["average_clustering"] = nx.average_clustering(self.graph)
        except Exception as e:
            logger.warning(f"Could not calculate average clustering: {e}")
            metrics["average_clustering"] = None
            
        try:
            if (self.directed and nx.is_strongly_connected(self.graph)) or \
               (not self.directed and nx.is_connected(self.graph)):
                metrics["diameter"] = nx.diameter(self.graph)
                metrics["average_shortest_path_length"] = nx.average_shortest_path_length(self.graph)
            else:
                # For disconnected graphs, calculate metrics on the largest component
                if self.directed:
                    largest_cc = max(nx.strongly_connected_components(self.graph), key=len)
                else:
                    largest_cc = max(nx.connected_components(self.graph), key=len)
                    
                largest_sg = self.graph.subgraph(largest_cc)
                if len(largest_cc) > 1:
                    metrics["diameter_largest_component"] = nx.diameter(largest_sg)
                    metrics["average_shortest_path_length_largest_component"] = nx.average_shortest_path_length(largest_sg)
                    metrics["largest_component_size"] = len(largest_cc)
                    metrics["largest_component_percentage"] = len(largest_cc) / self.graph.number_of_nodes()
        except Exception as e:
            logger.warning(f"Could not calculate path-based metrics: {e}")
            metrics["diameter"] = None
            metrics["average_shortest_path_length"] = None
            
        return metrics
    
    def get_centrality_metrics(self, top_n: Optional[int] = None, normalized: bool = True) -> Dict[str, Dict]:
        """Calculate node centrality metrics.
        
        Args:
            top_n: If provided, return only the top N nodes for each metric
            normalized: Whether to normalize centrality values
            
        Returns:
            Dictionary of centrality metrics for each node
        """
        centrality_metrics = {}
        
        # Calculate degree centrality (handles both directed and undirected)
        if self.directed:
            centrality_metrics["in_degree"] = nx.in_degree_centrality(self.graph)
            centrality_metrics["out_degree"] = nx.out_degree_centrality(self.graph)
        else:
            centrality_metrics["degree"] = nx.degree_centrality(self.graph)
        
        # Calculate other centrality metrics safely
        try:
            centrality_metrics["closeness"] = nx.closeness_centrality(self.graph)
        except Exception as e:
            logger.warning(f"Could not calculate closeness centrality: {e}")
            
        try:
            centrality_metrics["betweenness"] = nx.betweenness_centrality(self.graph, normalized=normalized)
        except Exception as e:
            logger.warning(f"Could not calculate betweenness centrality: {e}")
            
        try:
            # Eigenvector centrality may fail to converge on directed graphs
            centrality_metrics["eigenvector"] = nx.eigenvector_centrality(
                self.graph, max_iter=1000, tol=1e-6, normalized=normalized
            )
        except Exception as e:
            logger.warning(f"Could not calculate eigenvector centrality: {e}")
            try:
                # Fall back to power iteration method which is more robust
                centrality_metrics["eigenvector"] = nx.eigenvector_centrality_numpy(self.graph)
            except Exception as e:
                logger.warning(f"Could not calculate eigenvector centrality with numpy: {e}")
        
        # Calculate PageRank for directed graphs
        if self.directed:
            try:
                centrality_metrics["pagerank"] = nx.pagerank(self.graph, alpha=0.85)
            except Exception as e:
                logger.warning(f"Could not calculate PageRank: {e}")
        
        # If top_n is provided, filter to top nodes for each metric
        if top_n is not None and top_n > 0:
            for metric, values in centrality_metrics.items():
                sorted_nodes = sorted(values.items(), key=lambda x: x[1], reverse=True)[:top_n]
                centrality_metrics[metric] = dict(sorted_nodes)
        
        return centrality_metrics
    
    def detect_communities(self, algorithm: str = "louvain") -> Dict[str, Any]:
        """Detect communities in the graph.
        
        Args:
            algorithm: Community detection algorithm to use 
                       (louvain, greedy, label_propagation, girvan_newman)
            
        Returns:
            Dictionary with community detection results
        """
        # Convert to undirected for community detection algorithms that require it
        if self.directed:
            G_undirected = self.graph.to_undirected()
        else:
            G_undirected = self.graph
            
        communities = []
        algorithm = algorithm.lower()
        
        try:
            if algorithm == "louvain":
                try:
                    import community as community_louvain
                    partition = community_louvain.best_partition(G_undirected)
                    # Convert partition dict to list of communities
                    community_to_nodes = {}
                    for node, community_id in partition.items():
                        if community_id not in community_to_nodes:
                            community_to_nodes[community_id] = []
                        community_to_nodes[community_id].append(node)
                    communities = list(community_to_nodes.values())
                except ImportError:
                    logger.warning("Could not import python-louvain, falling back to greedy modularity")
                    algorithm = "greedy"
            
            if algorithm == "greedy":
                communities = list(nx.algorithms.community.greedy_modularity_communities(G_undirected))
                
            elif algorithm == "label_propagation":
                communities = list(nx.algorithms.community.label_propagation_communities(G_undirected))
                
            elif algorithm == "girvan_newman":
                # Take the first iteration of Girvan-Newman which gives a reasonable partition
                communities = list(list(c) for c in next(nx.algorithms.community.girvan_newman(G_undirected)))
                
            # Convert communities from sets to lists for JSON serialization
            communities = [list(c) for c in communities]
            
            # Calculate modularity
            try:
                modularity = nx.algorithms.community.modularity(G_undirected, communities)
            except Exception as e:
                logger.warning(f"Could not calculate modularity: {e}")
                modularity = None
                
            return {
                "community_count": len(communities),
                "communities": communities,
                "algorithm": algorithm,
                "modularity": modularity,
                "community_sizes": [len(c) for c in communities]
            }
            
        except Exception as e:
            logger.error(f"Error in community detection: {e}")
            return {
                "community_count": 0,
                "communities": [],
                "algorithm": algorithm,
                "modularity": None,
                "error": str(e)
            }
    
    def get_layout_positions(self, layout: str = "spring", scale: float = 100.0, 
                          center: Optional[Tuple[float, float]] = None, 
                          dimensions: int = 2) -> Dict[str, List[float]]:
        """Get node positions for visualization using various layout algorithms.
        
        Args:
            layout: Layout algorithm to use
            scale: Scale factor for the layout
            center: Optional center point (x, y) for the layout
            dimensions: Number of dimensions (2 or 3)
            
        Returns:
            Dictionary mapping node IDs to position coordinates
        """
        layout_functions = {
            "spring": nx.spring_layout,
            "circular": nx.circular_layout,
            "kamada_kawai": nx.kamada_kawai_layout,
            "spectral": nx.spectral_layout,
            "shell": nx.shell_layout,
            "spiral": nx.spiral_layout,
            "random": nx.random_layout,
            "bipartite": nx.bipartite_layout if nx.is_bipartite(self.graph) else nx.spring_layout
        }
        
        layout_func = layout_functions.get(layout.lower(), nx.spring_layout)
        
        # Set common parameters
        layout_params = {
            "G": self.graph,
            "scale": scale,
            "dim": dimensions
        }
        
        if center:
            layout_params["center"] = center
            
        # Add layout-specific parameters
        if layout.lower() == "spring":
            layout_params["k"] = 2/(self.graph.number_of_nodes()**0.5)
            layout_params["iterations"] = 100
            
        try:
            positions = layout_func(**layout_params)
            
            # Convert numpy arrays to lists for JSON serialization
            return {node: [float(coord) for coord in coords] for node, coords in positions.items()}
        except Exception as e:
            logger.error(f"Error generating layout {layout}: {e}")
            # Fall back to random layout
            return {node: [float(x) for x in coords] 
                    for node, coords in nx.random_layout(self.graph, scale=scale, dim=dimensions).items()}
    
    def get_nodes_with_positions(self, layout: str = "spring", include_metrics: bool = False) -> List[Dict]:
        """Get node data enriched with position coordinates and optional metrics.
        
        Args:
            layout: Layout algorithm to use
            include_metrics: Whether to include centrality metrics for each node
            
        Returns:
            List of node dictionaries with added position and metric data
        """
        # Get positions for each node
        positions = self.get_layout_positions(layout)
        
        # Get centrality metrics if requested
        node_metrics = {}
        if include_metrics:
            centrality = self.get_centrality_metrics()
            for metric_name, metric_values in centrality.items():
                for node_id, value in metric_values.items():
                    if node_id not in node_metrics:
                        node_metrics[node_id] = {}
                    node_metrics[node_id][metric_name] = value
        
        # Add positions and metrics to node data
        nodes_with_data = []
        for node in self.nodes:
            node_id = node["id"]
            node_copy = node.copy()
            
            # Add position data if available
            if node_id in positions:
                node_copy["x"] = positions[node_id][0]
                node_copy["y"] = positions[node_id][1]
                if len(positions[node_id]) > 2:
                    node_copy["z"] = positions[node_id][2]
            
            # Add metrics if requested and available
            if include_metrics and node_id in node_metrics:
                node_copy["metrics"] = node_metrics[node_id]
                
            nodes_with_data.append(node_copy)
            
        return nodes_with_data
    
    def get_temporal_metrics(self, window_size: timedelta = timedelta(days=1), 
                          max_windows: int = 30) -> Dict[str, List[Dict]]:
        """Calculate metrics over time using a sliding window.
        
        Args:
            window_size: Size of each time window
            max_windows: Maximum number of windows to return
            
        Returns:
            Dictionary containing metrics over time
        """
        # Collect timestamps from links if available
        timestamps = []
        for link in self.links:
            if "timestamp" in link:
                try:
                    timestamp = link["timestamp"]
                    if isinstance(timestamp, str):
                        # Parse ISO format timestamp
                        timestamps.append(datetime.fromisoformat(timestamp.replace('Z', '+00:00')))
                    elif isinstance(timestamp, datetime):
                        timestamps.append(timestamp)
                except Exception as e:
                    logger.warning(f"Could not parse timestamp {link.get('timestamp')}: {e}")
                    
        if not timestamps:
            return {"error": "No valid timestamps found in links"}
            
        # Sort timestamps and find min/max
        timestamps.sort()
        min_time = timestamps[0]
        max_time = timestamps[-1]
        
        # Calculate window boundaries
        total_duration = max_time - min_time
        if total_duration <= window_size:
            windows = [(min_time, max_time)]
        else:
            # Calculate number of windows
            n_windows = min(max_windows, int(total_duration / window_size) + 1)
            window_duration = total_duration / n_windows
            
            windows = []
            for i in range(n_windows):
                start = min_time + i * window_duration
                end = min_time + (i + 1) * window_duration
                windows.append((start, end))
                
        # Calculate metrics for each window
        metrics_over_time = []
        for window_start, window_end in windows:
            # Filter links in this time window
            window_links = []
            for link in self.links:
                if "timestamp" in link:
                    try:
                        timestamp = link["timestamp"]
                        if isinstance(timestamp, str):
                            timestamp = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                        
                        if window_start <= timestamp <= window_end:
                            window_links.append(link)
                    except:
                        continue
            
            # Skip if no links in this window
            if not window_links:
                continue
                
            # Build graph for this window
            # Create deep copies of nodes to preserve their structure
            nodes_copy = [node.copy() for node in self.nodes]
            window_links_copy = [link.copy() for link in window_links]
            
            try:
                window_analyzer = NetworkAnalyzer(nodes_copy, window_links_copy, self.directed)
                window_metrics = window_analyzer.get_basic_metrics()
            except Exception as e:
                logger.warning(f"Error calculating window metrics: {e}")
                window_metrics = {"error": str(e)}
            
            metrics_over_time.append({
                "window_start": window_start.isoformat(),
                "window_end": window_end.isoformat(),
                "link_count": len(window_links),
                "metrics": window_metrics
            })
            
        return {
            "window_size_seconds": window_size.total_seconds(),
            "metrics_over_time": metrics_over_time
        }
    
    def get_network_visualization_data(self, layout: str = "spring", 
                                    include_communities: bool = False,
                                    include_metrics: bool = False,
                                    community_algorithm: str = "louvain") -> Dict[str, Any]:
        """Get complete data for network visualization including optional community detection.
        
        Args:
            layout: Layout algorithm to use
            include_communities: Whether to include community detection results
            include_metrics: Whether to include node centrality metrics
            community_algorithm: Community detection algorithm to use
            
        Returns:
            Dictionary with complete visualization data
        """
        # Get nodes with positions and metrics
        nodes = self.get_nodes_with_positions(layout, include_metrics)
        
        # Build result dictionary
        result = {
            "nodes": nodes,
            "links": self.links,
            "layout": layout,
            "graph_metrics": self.get_basic_metrics()
        }
        
        # Add community detection if requested
        if include_communities:
            communities = self.detect_communities(algorithm=community_algorithm)
            result["communities"] = communities
            
            # Add community assignments to nodes
            if communities["communities"]:
                community_map = {}
                for i, community in enumerate(communities["communities"]):
                    for node_id in community:
                        community_map[node_id] = i
                        
                for node in result["nodes"]:
                    node_id = node["id"]
                    node["community"] = community_map.get(node_id, -1)
        
        return result