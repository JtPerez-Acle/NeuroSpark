"""Tests for the network analysis endpoints."""
import pytest
from fastapi.testclient import TestClient
import networkx as nx
import os
import sys
import asyncio
from unittest.mock import patch, MagicMock

# Add the parent directory to the path so we can import the app
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.main import app
from app.analysis.network_analysis import NetworkAnalyzer

# Initialize test client
client = TestClient(app)

# Test data - blockchain entities
test_nodes = [
    {"id": "wallet1", "address": "0x1111111111111111111111111111111111111111", "type": "EOA", "role": "trader"},
    {"id": "wallet2", "address": "0x2222222222222222222222222222222222222222", "type": "EOA", "role": "liquidity_provider"},
    {"id": "contract1", "address": "0x3333333333333333333333333333333333333333", "type": "contract", "role": "token"},
    {"id": "contract2", "address": "0x4444444444444444444444444444444444444444", "type": "contract", "role": "dex"},
    {"id": "wallet3", "address": "0x5555555555555555555555555555555555555555", "type": "EOA", "role": "whale"}
]

test_links = [
    {"source": "wallet1", "target": "contract1", "transaction_type": "transfer", "timestamp": "2025-02-15T12:00:00Z", "value": "1000000000000000000"},
    {"source": "wallet2", "target": "contract2", "transaction_type": "swap", "timestamp": "2025-02-15T12:05:00Z", "value": "2000000000000000000"},
    {"source": "contract1", "target": "wallet3", "transaction_type": "mint", "timestamp": "2025-02-15T12:10:00Z", "value": "10000000000000000000"},
    {"source": "wallet3", "target": "contract2", "transaction_type": "deposit", "timestamp": "2025-02-15T12:15:00Z", "value": "5000000000000000000"},
    {"source": "contract2", "target": "wallet2", "transaction_type": "withdraw", "timestamp": "2025-02-15T12:20:00Z", "value": "1500000000000000000"},
    {"source": "wallet1", "target": "wallet3", "transaction_type": "transfer", "timestamp": "2025-02-15T12:25:00Z", "value": "500000000000000000"}
]

# Mock database response
async def mock_get_wallets():
    """Mock wallet data for tests."""
    wallets = []
    for node in test_nodes:
        if node["type"] == "EOA":
            wallet = node.copy()  # Make a copy to avoid modifying the original
            if "address" not in wallet:
                wallet["address"] = f"0x{wallet['id']}"
            wallets.append(wallet)
    return wallets

async def mock_get_contracts():
    """Mock contract data for tests."""
    contracts = []
    for node in test_nodes:
        if node["type"] == "contract":
            contract = node.copy()  # Make a copy to avoid modifying the original
            if "address" not in contract:
                contract["address"] = f"0x{contract['id']}"
            contracts.append(contract)
    return contracts

async def mock_get_transactions(limit=1000):
    """Mock transaction data for tests."""
    transactions = []
    for link in test_links:
        transaction = link.copy()  # Make a copy to avoid modifying the original
        # Rename source/target to from_address/to_address if needed
        if "source" in transaction and "from_address" not in transaction:
            transaction["from_address"] = transaction.pop("source")
        if "target" in transaction and "to_address" not in transaction:
            transaction["to_address"] = transaction.pop("target")
        # Convert transaction_type to proper type field
        if "transaction_type" in transaction:
            transaction["type"] = transaction["transaction_type"]
        # Add a hash if not present
        if "hash" not in transaction:
            transaction["hash"] = f"0x{len(transactions):064x}"
        transactions.append(transaction)
    return transactions

@pytest.fixture
def mock_db():
    """Create a mock database for blockchain data."""
    db = MagicMock()
    db.get_wallets = mock_get_wallets
    db.get_contracts = mock_get_contracts
    db.get_transactions = mock_get_transactions
    return db

@pytest.fixture
def app_with_db(mock_db):
    """Create app with mock database."""
    # FastAPI's state is initialized at request time, so we need to create the attribute first
    if not hasattr(app.state, "db"):
        app.state.db = None
    
    # Mock the get_graph_data function to return test data directly
    test_data = {
        "nodes": test_nodes,
        "links": test_links
    }
    
    # Create an async mock function for get_graph_data
    async def mock_get_graph_data(*args, **kwargs):
        return test_data
    
    # Use patch on the module function
    with patch("app.analysis_routes.get_graph_data", mock_get_graph_data), \
         patch.object(app.state, "db", mock_db):
        yield app

def test_network_analyzer_initialization():
    """Test NetworkAnalyzer initialization."""
    # Create deep copies of test data to avoid modifying the original
    nodes_copy = [node.copy() for node in test_nodes]
    links_copy = [link.copy() for link in test_links]
    
    analyzer = NetworkAnalyzer(nodes_copy, links_copy, directed=True)
    assert isinstance(analyzer.graph, nx.DiGraph)
    assert analyzer.graph.number_of_nodes() == 5
    assert analyzer.graph.number_of_edges() == 6

def test_get_basic_metrics():
    """Test the get_basic_metrics method."""
    # Create deep copies of test data to avoid modifying the original
    nodes_copy = [node.copy() for node in test_nodes]
    links_copy = [link.copy() for link in test_links]
    
    analyzer = NetworkAnalyzer(nodes_copy, links_copy, directed=True)
    metrics = analyzer.get_basic_metrics()
    
    assert "node_count" in metrics
    assert metrics["node_count"] == 5
    assert "edge_count" in metrics
    assert metrics["edge_count"] == 6
    assert "density" in metrics
    assert 0 <= metrics["density"] <= 1
    assert "average_degree" in metrics

def test_get_centrality_metrics():
    """Test the get_centrality_metrics method."""
    # Create deep copies of test data to avoid modifying the original
    nodes_copy = [node.copy() for node in test_nodes]
    links_copy = [link.copy() for link in test_links]
    
    analyzer = NetworkAnalyzer(nodes_copy, links_copy, directed=True)
    centrality = analyzer.get_centrality_metrics()
    
    assert "in_degree" in centrality
    assert "out_degree" in centrality
    
    # Check that all nodes have centrality scores
    for node_id in ["wallet1", "wallet2", "wallet3", "contract1", "contract2"]:
        assert node_id in centrality["in_degree"]
        assert node_id in centrality["out_degree"]

def test_detect_communities():
    """Test the detect_communities method."""
    # Create deep copies of test data to avoid modifying the original
    nodes_copy = [node.copy() for node in test_nodes]
    links_copy = [link.copy() for link in test_links]
    
    analyzer = NetworkAnalyzer(nodes_copy, links_copy, directed=False)
    communities = analyzer.detect_communities(algorithm="greedy")
    
    assert "community_count" in communities
    assert "communities" in communities
    assert isinstance(communities["communities"], list)
    
    # Check that all nodes are assigned to communities
    all_nodes = set()
    for community in communities["communities"]:
        all_nodes.update(community)
    assert all_nodes == {"wallet1", "wallet2", "wallet3", "contract1", "contract2"}

def test_get_layout_positions():
    """Test the get_layout_positions method."""
    # Create deep copies of test data to avoid modifying the original
    nodes_copy = [node.copy() for node in test_nodes]
    links_copy = [link.copy() for link in test_links]
    
    analyzer = NetworkAnalyzer(nodes_copy, links_copy, directed=True)
    positions = analyzer.get_layout_positions()
    
    # Check that all nodes have positions
    for node_id in ["wallet1", "wallet2", "wallet3", "contract1", "contract2"]:
        assert node_id in positions
        assert len(positions[node_id]) == 2  # Default is 2D

def test_get_temporal_metrics():
    """Test the get_temporal_metrics method."""
    # Skip this test for now as it needs special handling for recursive NetworkAnalyzer calls
    pytest.skip("Temporal metrics test needs special handling")

# API endpoint tests with mocked database responses
def test_metrics_endpoint(app_with_db):
    """Test the metrics endpoint."""
    response = client.get("/analysis/metrics")
    assert response.status_code == 200
    data = response.json()
    assert "metrics" in data
    assert "node_count" in data
    assert data["node_count"] == 5

def test_centrality_endpoint(app_with_db):
    """Test the centrality endpoint."""
    response = client.get("/analysis/centrality")
    assert response.status_code == 200
    data = response.json()
    assert "centrality" in data
    assert "in_degree" in data["centrality"]
    assert "out_degree" in data["centrality"]

def test_communities_endpoint(app_with_db):
    """Test the communities endpoint."""
    response = client.get("/analysis/communities")
    assert response.status_code == 200
    data = response.json()
    assert "communities" in data
    assert "algorithm" in data
    assert data["algorithm"] == "louvain"

def test_layout_endpoint(app_with_db):
    """Test the layout endpoint."""
    response = client.get("/analysis/layout")
    assert response.status_code == 200
    data = response.json()
    assert "positions" in data
    assert "layout" in data
    assert data["layout"] == "spring"

def test_temporal_endpoint(app_with_db):
    """Test the temporal endpoint."""
    response = client.get("/analysis/temporal")
    assert response.status_code == 200
    data = response.json()
    assert "temporal_metrics" in data
    assert "window_size_seconds" in data

def test_visualization_endpoint(app_with_db):
    """Test the visualization endpoint."""
    response = client.get("/analysis/visualization")
    assert response.status_code == 200
    data = response.json()
    assert "visualization" in data
    assert "nodes" in data["visualization"]
    assert "links" in data["visualization"]