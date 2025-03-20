"""Graph routes for the Blockchain Intelligence Backend."""
from fastapi import APIRouter, Request, HTTPException, Query, Body
from typing import Dict, Any, List, Optional
import logging
from datetime import datetime, timezone

# Configure logging
logger = logging.getLogger(__name__)

# Create router
graph_router = APIRouter()

def get_db(request: Request):
    """Get database instance from app state."""
    return request.app.state.db

@graph_router.get("/data",
    response_model=Dict[str, Any],
    summary="Get Blockchain Graph Data",
    description="Get wallets, contracts, and transactions for graph visualization.",
    response_description="Graph visualization data with nodes and edges.",
    responses={
        500: {"description": "Internal server error"}
    }
)
async def get_graph_data(
    request: Request,
    node_type: Optional[str] = Query(None, description="Filter nodes by type (wallet, contract)"),
    time_range: Optional[str] = Query(None, description="Time range (24h, 7d, 30d, all)"),
    min_risk: Optional[float] = Query(None, description="Minimum risk score")
) -> Dict[str, Any]:
    """Get blockchain network data for graph visualization."""
    try:
        db = get_db(request)
        
        # Create filters
        filters = {}
        if node_type:
            filters["node_type"] = node_type
        if time_range:
            filters["time_range"] = time_range
        if min_risk is not None:
            filters["min_risk"] = min_risk
        
        # Get blockchain network data
        network = await db.get_blockchain_network(filters)
        
        # Rename links to edges for compatibility with visualization libraries
        if "edges" in network:
            network["links"] = network["edges"]
            
        return network
    except Exception as e:
        logger.error(f"Error fetching blockchain graph data: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@graph_router.get("/wallet/{address}",
    response_model=Dict[str, Any],
    summary="Get Wallet Graph",
    description="Get wallet-centric subgraph showing connected wallets and contracts.",
    response_description="Wallet-centric subgraph data.",
    responses={
        404: {"description": "Wallet not found"},
        500: {"description": "Internal server error"}
    }
)
async def get_wallet_graph(
    address: str, 
    request: Request,
    chain: str = Query("ethereum", description="Blockchain identifier"),
    depth: int = Query(1, description="Connection depth (1-3)"),
    limit: int = Query(100, description="Maximum number of connected nodes")
) -> Dict[str, Any]:
    """Get wallet-centric subgraph showing connected wallets and contracts."""
    try:
        db = get_db(request)
        
        # Get wallet data
        wallet = await db.get_wallet(address, chain)
        if not wallet:
            raise HTTPException(status_code=404, detail=f"Wallet {address} not found on {chain} chain")
        
        # Create initial node
        nodes = [{
            "id": wallet["address"],
            "label": wallet.get("role", "wallet"),
            "type": "wallet",
            "subtype": wallet.get("wallet_type", "EOA"),
            "risk_score": wallet.get("risk_score", 0),
            "chain": wallet.get("chain", "ethereum"),
            "details": f"Address: {wallet['address']}, Type: {wallet.get('wallet_type', 'EOA')}"
        }]
        
        # Get wallet transactions (connections)
        transactions = await db.get_wallet_transactions(address, chain, limit=limit)
        
        edges = []
        connected_addresses = set()
        
        for tx in transactions:
            from_addr = tx.get("from_address")
            to_addr = tx.get("to_address")
            
            if from_addr == address:
                # This wallet is the sender
                connected_addresses.add(to_addr)
                edges.append({
                    "id": tx.get("hash", "unknown"),
                    "source": from_addr,
                    "target": to_addr,
                    "type": "transaction",
                    "value": tx.get("value", 0),
                    "timestamp": tx.get("timestamp")
                })
            elif to_addr == address:
                # This wallet is the receiver
                connected_addresses.add(from_addr)
                edges.append({
                    "id": tx.get("hash", "unknown"),
                    "source": from_addr,
                    "target": to_addr,
                    "type": "transaction",
                    "value": tx.get("value", 0),
                    "timestamp": tx.get("timestamp")
                })
        
        # Get connected wallet data
        for connected_addr in connected_addresses:
            conn_wallet = await db.get_wallet(connected_addr, chain)
            if conn_wallet:
                nodes.append({
                    "id": conn_wallet["address"],
                    "label": conn_wallet.get("role", "wallet"),
                    "type": "wallet",
                    "subtype": conn_wallet.get("wallet_type", "EOA"),
                    "risk_score": conn_wallet.get("risk_score", 0),
                    "chain": conn_wallet.get("chain", "ethereum"),
                    "details": f"Address: {conn_wallet['address']}, Type: {conn_wallet.get('wallet_type', 'EOA')}"
                })
            
            # Check if it's a contract
            contract = await db.get_contract(connected_addr, chain)
            if contract:
                # If it's a contract, update the node type
                for node in nodes:
                    if node["id"] == connected_addr:
                        node["type"] = "contract"
                        node["subtype"] = contract.get("role", "contract")
                        node["details"] = f"Contract: {contract.get('name', connected_addr)}, Verified: {contract.get('verified', False)}"
                        break
        
        return {
            "nodes": nodes,
            "edges": edges
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching wallet graph data: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
        
@graph_router.get("/contract/{address}",
    response_model=Dict[str, Any],
    summary="Get Contract Graph",
    description="Get contract-centric subgraph showing connected wallets and other contracts.",
    response_description="Contract-centric subgraph data.",
    responses={
        404: {"description": "Contract not found"},
        500: {"description": "Internal server error"}
    }
)
async def get_contract_graph(
    address: str, 
    request: Request,
    chain: str = Query("ethereum", description="Blockchain identifier"),
    depth: int = Query(1, description="Connection depth (1-3)"),
    limit: int = Query(100, description="Maximum number of connected nodes")
) -> Dict[str, Any]:
    """Get contract-centric subgraph showing connected wallets and other contracts."""
    try:
        db = get_db(request)
        
        # Get contract data
        contract = await db.get_contract(address, chain)
        if not contract:
            raise HTTPException(status_code=404, detail=f"Contract {address} not found on {chain} chain")
        
        # Create initial node
        nodes = [{
            "id": contract["address"],
            "label": contract.get("name", "contract"),
            "type": "contract",
            "subtype": contract.get("contract_type", "unknown"),
            "risk_score": contract.get("risk_score", 0),
            "chain": contract.get("chain", "ethereum"),
            "details": f"Contract: {contract.get('name', address)}, Verified: {contract.get('verified', False)}"
        }]
        
        # Get contract wallet interactions
        wallet_contracts = await db.get_wallet_contracts(address, chain, limit=limit)
        
        # Get transactions involving this contract
        transactions = await db.get_wallet_transactions(address, chain, limit=limit)
        
        edges = []
        connected_addresses = set()
        
        for tx in transactions:
            from_addr = tx.get("from_address")
            to_addr = tx.get("to_address")
            
            if from_addr == address:
                # Contract is the sender
                connected_addresses.add(to_addr)
                edges.append({
                    "id": tx.get("hash", "unknown"),
                    "source": from_addr,
                    "target": to_addr,
                    "type": "transaction",
                    "value": tx.get("value", 0),
                    "timestamp": tx.get("timestamp")
                })
            elif to_addr == address:
                # Contract is the receiver
                connected_addresses.add(from_addr)
                edges.append({
                    "id": tx.get("hash", "unknown"),
                    "source": from_addr,
                    "target": to_addr,
                    "type": "transaction",
                    "value": tx.get("value", 0),
                    "timestamp": tx.get("timestamp")
                })
        
        # Get connected wallet/contract data
        for connected_addr in connected_addresses:
            # Try as wallet first
            conn_wallet = await db.get_wallet(connected_addr, chain)
            if conn_wallet:
                nodes.append({
                    "id": conn_wallet["address"],
                    "label": conn_wallet.get("role", "wallet"),
                    "type": "wallet",
                    "subtype": conn_wallet.get("wallet_type", "EOA"),
                    "risk_score": conn_wallet.get("risk_score", 0),
                    "chain": conn_wallet.get("chain", "ethereum"),
                    "details": f"Address: {conn_wallet['address']}, Type: {conn_wallet.get('wallet_type', 'EOA')}"
                })
            
            # Check if it's a contract
            conn_contract = await db.get_contract(connected_addr, chain)
            if conn_contract:
                # If it's a contract, update the node type or add a new node
                node_exists = False
                for node in nodes:
                    if node["id"] == connected_addr:
                        node["type"] = "contract"
                        node["label"] = conn_contract.get("name", "contract")
                        node["subtype"] = conn_contract.get("contract_type", "unknown")
                        node["details"] = f"Contract: {conn_contract.get('name', connected_addr)}, Verified: {conn_contract.get('verified', False)}"
                        node_exists = True
                        break
                
                if not node_exists:
                    nodes.append({
                        "id": conn_contract["address"],
                        "label": conn_contract.get("name", "contract"),
                        "type": "contract",
                        "subtype": conn_contract.get("contract_type", "unknown"),
                        "risk_score": conn_contract.get("risk_score", 0),
                        "chain": conn_contract.get("chain", "ethereum"),
                        "details": f"Contract: {conn_contract.get('name', connected_addr)}, Verified: {conn_contract.get('verified', False)}"
                    })
        
        return {
            "nodes": nodes,
            "edges": edges
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching contract graph data: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@graph_router.get("/network",
    response_model=Dict[str, Any],
    summary="Get Blockchain Network",
    description="Get the entire blockchain network graph with wallets and transactions.",
    response_description="Blockchain network graph data.",
    responses={
        500: {"description": "Internal server error"}
    }
)
async def get_network(
    request: Request,
    node_type: Optional[str] = Query(None, description="Filter nodes by type (wallet, contract)"),
    time_range: Optional[str] = Query(None, description="Time range (24h, 7d, 30d, all)"),
    limit: int = Query(1000, description="Maximum number of nodes to return")
) -> Dict[str, Any]:
    """Get the entire blockchain network graph with wallets and transactions."""
    try:
        db = get_db(request)
        
        # Create filters
        filters = {"limit": limit}
        if node_type:
            filters["node_type"] = node_type
        if time_range:
            filters["time_range"] = time_range
        
        # Get blockchain network data
        network = await db.get_blockchain_network(filters)
        
        # Make sure links property exists for GraphViz compatibility
        if "edges" in network and "links" not in network:
            network["links"] = network["edges"]
        
        return network
    except Exception as e:
        logger.error(f"Error fetching blockchain network data: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@graph_router.post("/query",
    response_model=Dict[str, Any],
    summary="Query Blockchain Network",
    description="Advanced query of the blockchain network with multiple filter options.",
    response_description="Filtered blockchain network data.",
    responses={
        422: {"description": "Validation Error"},
        500: {"description": "Internal server error"}
    }
)
async def query_network(
    request: Request,
    query: Dict[str, Any] = Body(..., description="Query parameters")
) -> Dict[str, Any]:
    """Advanced query of the blockchain network with multiple filter options."""
    try:
        db = get_db(request)
        
        # Extract parameters from query
        node_type = query.get("node_type")
        relationship_type = query.get("relationship_type")
        start_time = query.get("start_time")
        end_time = query.get("end_time")
        addresses = query.get("addresses")
        limit = query.get("limit", 1000)
        include_properties = query.get("include_properties", True)
        
        # Query blockchain network
        network = await db.query_network(
            node_type=node_type,
            relationship_type=relationship_type,
            start_time=start_time,
            end_time=end_time,
            addresses=addresses,  # Use addresses parameter directly
            limit=limit,
            include_properties=include_properties
        )
        
        # Make sure links property exists for GraphViz compatibility
        if "edges" in network and "links" not in network:
            network["links"] = network["edges"]
        
        return network
    except Exception as e:
        logger.error(f"Error querying blockchain network: {str(e)}")
        if "Invalid" in str(e) or "invalid" in str(e):
            raise HTTPException(status_code=422, detail=str(e))
        raise HTTPException(status_code=500, detail=str(e))