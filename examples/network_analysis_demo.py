#!/usr/bin/env python
"""
Network Analysis Demo Script

This example demonstrates how to use the NetworkX integration endpoints
to analyze a predator-prey network graph.

Version: 0.8.2
"""

import requests
import json
import matplotlib.pyplot as plt
import networkx as nx

# Base URL for API
BASE_URL = "http://localhost:8000"

def generate_data(scenario="predator_prey", num_agents=30, num_interactions=100):
    """Generate synthetic data for demonstration."""
    print(f"Generating {scenario} scenario with {num_agents} agents and {num_interactions} interactions...")
    
    response = requests.post(
        f"{BASE_URL}/generate/scenario",
        json={
            "scenario": scenario,
            "numAgents": num_agents,
            "numInteractions": num_interactions
        }
    )
    
    if response.status_code == 200:
        print("Data generated successfully!")
        return response.json()["data"]
    else:
        print(f"Error generating data: {response.status_code} - {response.text}")
        return None

def get_graph_metrics():
    """Get basic graph metrics."""
    print("\nFetching graph metrics...")
    
    response = requests.get(f"{BASE_URL}/analysis/metrics")
    
    if response.status_code == 200:
        metrics = response.json()["metrics"]
        print("\nGraph Metrics:")
        print(f"- Node count: {metrics['node_count']}")
        print(f"- Edge count: {metrics['edge_count']}")
        print(f"- Density: {metrics['density']:.4f}")
        print(f"- Average degree: {metrics['average_degree']:.2f}")
        
        if "is_strongly_connected" in metrics:
            print(f"- Strongly connected: {metrics['is_strongly_connected']}")
            print(f"- Strongly connected components: {metrics['strongly_connected_components']}")
            print(f"- Weakly connected: {metrics['is_weakly_connected']}")
            
        if "average_clustering" in metrics and metrics["average_clustering"] is not None:
            print(f"- Average clustering: {metrics['average_clustering']:.4f}")
            
        if "diameter_largest_component" in metrics:
            print(f"- Diameter (largest component): {metrics['diameter_largest_component']}")
            
        return metrics
    else:
        print(f"Error fetching metrics: {response.status_code} - {response.text}")
        return None

def get_centrality_measures(top_n=5):
    """Get node centrality measures."""
    print("\nFetching centrality measures...")
    
    response = requests.get(f"{BASE_URL}/analysis/centrality?top_n={top_n}")
    
    if response.status_code == 200:
        centrality = response.json()["centrality"]
        
        print(f"\nTop {top_n} nodes by centrality:")
        
        # In-degree centrality (if available)
        if "in_degree" in centrality:
            print("\nIn-degree Centrality (incoming connections):")
            sorted_nodes = sorted(centrality["in_degree"].items(), key=lambda x: x[1], reverse=True)[:top_n]
            for node_id, value in sorted_nodes:
                print(f"- {node_id}: {value:.4f}")
        
        # Out-degree centrality (if available)
        if "out_degree" in centrality:
            print("\nOut-degree Centrality (outgoing connections):")
            sorted_nodes = sorted(centrality["out_degree"].items(), key=lambda x: x[1], reverse=True)[:top_n]
            for node_id, value in sorted_nodes:
                print(f"- {node_id}: {value:.4f}")
                
        # Betweenness centrality (if available)
        if "betweenness" in centrality:
            print("\nBetweenness Centrality (bridging role):")
            sorted_nodes = sorted(centrality["betweenness"].items(), key=lambda x: x[1], reverse=True)[:top_n]
            for node_id, value in sorted_nodes:
                print(f"- {node_id}: {value:.4f}")
        
        return centrality
    else:
        print(f"Error fetching centrality: {response.status_code} - {response.text}")
        return None

def detect_communities():
    """Detect communities in the graph."""
    print("\nDetecting communities...")
    
    response = requests.get(f"{BASE_URL}/analysis/communities")
    
    if response.status_code == 200:
        data = response.json()
        communities = data["communities"]
        
        print(f"\nCommunity Detection ({communities['algorithm']} algorithm):")
        print(f"- Number of communities: {communities['community_count']}")
        print(f"- Modularity: {communities.get('modularity', 'N/A')}")
        print(f"- Community sizes: {communities['community_sizes']}")
        
        return communities
    else:
        print(f"Error detecting communities: {response.status_code} - {response.text}")
        return None

def get_visualization_data():
    """Get enhanced visualization data."""
    print("\nFetching visualization data...")
    
    response = requests.get(
        f"{BASE_URL}/analysis/visualization?include_communities=true&include_metrics=true"
    )
    
    if response.status_code == 200:
        data = response.json()["visualization"]
        
        print(f"\nVisualization data:")
        print(f"- Node count: {len(data['nodes'])}")
        print(f"- Link count: {len(data['links'])}")
        print(f"- Layout: {data['layout']}")
        
        if "communities" in data:
            print(f"- Communities included: {data['communities']['community_count']} communities")
            
        return data
    else:
        print(f"Error fetching visualization data: {response.status_code} - {response.text}")
        return None

def main():
    """Main demo function."""
    print("NetworkX Integration Demo for KQML Parser Backend")
    print("================================================")
    
    # Generate synthetic data
    generate_data()
    
    # Get basic metrics
    metrics = get_graph_metrics()
    
    # Get centrality measures
    centrality = get_centrality_measures()
    
    # Detect communities
    communities = detect_communities()
    
    # Get visualization data
    vis_data = get_visualization_data()
    
    print("\nDemo completed successfully!")

if __name__ == "__main__":
    main()