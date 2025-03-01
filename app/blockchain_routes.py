"""Blockchain API routes."""
from typing import Dict, List, Optional, Any
from fastapi import APIRouter, Query, Path, Depends, HTTPException
from pydantic import BaseModel, Field

from app.database.arango.database import ArangoDatabase

# Response models
class WalletResponse(BaseModel):
    """Wallet response model."""
    address: str = Field(..., description="Wallet address")
    chain: str = Field(..., description="Blockchain identifier")
    balance: int = Field(0, description="Current wallet balance")
    wallet_type: str = Field(..., description="Wallet type (EOA, contract, etc.)")
    first_seen: Optional[str] = Field(None, description="Timestamp of first activity")
    last_active: Optional[str] = Field(None, description="Timestamp of latest activity")
    risk_score: Optional[float] = Field(None, description="Risk assessment score (0-100)")
    tags: List[str] = Field(default_factory=list, description="Wallet tags/labels")

class TransactionResponse(BaseModel):
    """Transaction response model."""
    hash: str = Field(..., description="Transaction hash")
    chain: str = Field(..., description="Blockchain identifier")
    block_number: int = Field(..., description="Block containing the transaction")
    timestamp: str = Field(..., description="Transaction timestamp")
    from_address: str = Field(..., description="Sender address")
    to_address: Optional[str] = Field(None, description="Recipient address")
    value: int = Field(0, description="Transaction amount")
    status: str = Field(..., description="Transaction status")
    gas_used: Optional[int] = Field(None, description="Gas consumed")
    gas_price: Optional[int] = Field(None, description="Gas price")
    risk_score: Optional[float] = Field(None, description="Risk assessment score (0-100)")

class ContractResponse(BaseModel):
    """Contract response model."""
    address: str = Field(..., description="Contract address")
    chain: str = Field(..., description="Blockchain identifier")
    creator: Optional[str] = Field(None, description="Creator address")
    creation_timestamp: Optional[str] = Field(None, description="Creation time")
    verified: bool = Field(False, description="Whether source code is verified")
    name: Optional[str] = Field(None, description="Contract name")
    risk_score: Optional[float] = Field(None, description="Risk assessment score (0-100)")
    vulnerabilities: List[Dict[str, Any]] = Field(default_factory=list, description="Detected vulnerabilities")

class EventResponse(BaseModel):
    """Event response model."""
    contract_address: str = Field(..., description="Contract address")
    tx_hash: str = Field(..., description="Transaction hash")
    block_number: int = Field(..., description="Block containing the event")
    log_index: int = Field(..., description="Index in the transaction logs")
    timestamp: str = Field(..., description="Event timestamp")
    name: Optional[str] = Field(None, description="Event name")
    signature: Optional[str] = Field(None, description="Event signature")
    params: Dict[str, Any] = Field(default_factory=dict, description="Event parameters")

class AlertResponse(BaseModel):
    """Alert response model."""
    id: str = Field(..., description="Alert ID")
    timestamp: str = Field(..., description="Alert generation time")
    severity: str = Field(..., description="Alert severity (low, medium, high, critical)")
    type: str = Field(..., description="Alert type")
    entity: str = Field(..., description="Related entity (address, tx hash, etc.)")
    entity_type: str = Field(..., description="Entity type (wallet, contract, transaction)")
    description: str = Field(..., description="Alert description")
    status: str = Field(..., description="Alert status (new, acknowledged, resolved)")

# Multi-entity responses
class WalletList(BaseModel):
    """Wallet list response."""
    items: List[WalletResponse] = Field(..., description="List of wallets")
    count: int = Field(..., description="Total count of wallets returned")

class TransactionList(BaseModel):
    """Transaction list response."""
    items: List[TransactionResponse] = Field(..., description="List of transactions")
    count: int = Field(..., description="Total count of transactions returned")

class ContractList(BaseModel):
    """Contract list response."""
    items: List[ContractResponse] = Field(..., description="List of contracts")
    count: int = Field(..., description="Total count of contracts returned")

class EventList(BaseModel):
    """Event list response."""
    items: List[EventResponse] = Field(..., description="List of events")
    count: int = Field(..., description="Total count of events returned")

class AlertList(BaseModel):
    """Alert list response."""
    items: List[AlertResponse] = Field(..., description="List of alerts")
    count: int = Field(..., description="Total count of alerts returned")

# API router
router = APIRouter(prefix="/blockchain", tags=["blockchain"])

# Dependency to get database
async def get_db():
    """Get database connection."""
    db = ArangoDatabase(
        host="localhost",
        port=8529,
        username="root",
        password="password",
        db_name="neurospark"
    )
    await db.connect()
    try:
        yield db
    finally:
        await db.disconnect()

# Wallet routes
@router.get("/wallets/{address}", response_model=WalletResponse)
async def get_wallet(
    address: str = Path(..., description="Wallet address"),
    chain: str = Query("ethereum", description="Blockchain identifier"),
    db: ArangoDatabase = Depends(get_db)
):
    """Get wallet information from the database."""
    wallet = await db.get_wallet(address, chain)
    
    if not wallet:
        raise HTTPException(status_code=404, detail=f"Wallet {address} not found on {chain} chain")
    
    return wallet

@router.get("/wallets/{address}/transactions", response_model=TransactionList)
async def get_wallet_transactions(
    address: str = Path(..., description="Wallet address"),
    chain: str = Query("ethereum", description="Blockchain identifier"),
    limit: int = Query(20, ge=1, le=100, description="Maximum number of transactions to return"),
    offset: int = Query(0, ge=0, description="Number of transactions to skip"),
    sort_field: str = Query("timestamp", description="Field to sort by"),
    sort_direction: str = Query("desc", description="Sort direction (asc or desc)"),
    db: ArangoDatabase = Depends(get_db)
):
    """Get transactions for a wallet."""
    transactions = await db.get_wallet_transactions(
        address=address,
        chain=chain,
        limit=limit,
        offset=offset,
        sort_field=sort_field,
        sort_direction=sort_direction
    )
    
    return {
        "items": transactions,
        "count": len(transactions)
    }

@router.get("/wallets/{address}/contracts", response_model=ContractList)
async def get_wallet_contracts(
    address: str = Path(..., description="Wallet address"),
    chain: str = Query("ethereum", description="Blockchain identifier"),
    limit: int = Query(20, ge=1, le=100, description="Maximum number of contracts to return"),
    offset: int = Query(0, ge=0, description="Number of contracts to skip"),
    db: ArangoDatabase = Depends(get_db)
):
    """Get contracts deployed or interacted with by a wallet."""
    contracts = await db.get_wallet_contracts(
        address=address,
        chain=chain,
        limit=limit,
        offset=offset
    )
    
    return {
        "items": contracts,
        "count": len(contracts)
    }

# Transaction routes
@router.get("/transactions/{tx_hash}", response_model=TransactionResponse)
async def get_transaction(
    tx_hash: str = Path(..., description="Transaction hash"),
    chain: str = Query("ethereum", description="Blockchain identifier"),
    db: ArangoDatabase = Depends(get_db)
):
    """Get transaction information from the database."""
    transaction = await db.get_transaction(tx_hash, chain)
    
    if not transaction:
        raise HTTPException(status_code=404, detail=f"Transaction {tx_hash} not found on {chain} chain")
    
    return transaction

# Contract routes
@router.get("/contracts/{address}", response_model=ContractResponse)
async def get_contract(
    address: str = Path(..., description="Contract address"),
    chain: str = Query("ethereum", description="Blockchain identifier"),
    db: ArangoDatabase = Depends(get_db)
):
    """Get contract information from the database."""
    contract = await db.get_contract(address, chain)
    
    if not contract:
        raise HTTPException(status_code=404, detail=f"Contract {address} not found on {chain} chain")
    
    return contract

@router.get("/contracts/{address}/events", response_model=EventList)
async def get_contract_events(
    address: str = Path(..., description="Contract address"),
    chain: str = Query("ethereum", description="Blockchain identifier"),
    event_name: Optional[str] = Query(None, description="Optional event name filter"),
    from_block: Optional[int] = Query(None, description="Optional starting block number"),
    to_block: Optional[int] = Query(None, description="Optional ending block number"),
    limit: int = Query(20, ge=1, le=100, description="Maximum number of events to return"),
    offset: int = Query(0, ge=0, description="Number of events to skip"),
    db: ArangoDatabase = Depends(get_db)
):
    """Get events for a contract."""
    events = await db.get_contract_events(
        contract_address=address,
        chain=chain,
        event_name=event_name,
        from_block=from_block,
        to_block=to_block,
        limit=limit,
        offset=offset
    )
    
    return {
        "items": events,
        "count": len(events)
    }

# Risk routes
@router.get("/risk/{entity_type}", response_model=Dict[str, Any])
async def get_high_risk_entities(
    entity_type: str = Path(..., description="Entity type (wallets, contracts, transactions)"),
    min_risk_score: float = Query(75.0, ge=0.0, le=100.0, description="Minimum risk score"),
    limit: int = Query(20, ge=1, le=50, description="Maximum number of entities to return"),
    db: ArangoDatabase = Depends(get_db)
):
    """Get high-risk entities from the database."""
    if entity_type not in ["wallets", "contracts", "transactions"]:
        raise HTTPException(status_code=400, detail=f"Invalid entity type: {entity_type}")
    
    entities = await db.get_high_risk_entities(
        entity_type=entity_type,
        min_risk_score=min_risk_score,
        limit=limit
    )
    
    return {
        "entity_type": entity_type,
        "min_risk_score": min_risk_score,
        "count": len(entities),
        "items": entities
    }

@router.get("/risk/alerts", response_model=AlertList)
async def get_active_alerts(
    severity: Optional[str] = Query(None, description="Filter by severity level (low, medium, high, critical)"),
    entity_type: Optional[str] = Query(None, description="Filter by entity type (wallet, contract, transaction)"),
    alert_type: Optional[str] = Query(None, description="Filter by alert type"),
    limit: int = Query(50, ge=1, le=100, description="Maximum number of alerts to return"),
    db: ArangoDatabase = Depends(get_db)
):
    """Get active security alerts from the database."""
    alerts = await db.get_active_alerts(
        severity=severity,
        entity_type=entity_type,
        alert_type=alert_type,
        limit=limit
    )
    
    return {
        "items": alerts,
        "count": len(alerts)
    }