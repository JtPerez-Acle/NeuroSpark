"""Run database operations."""
from typing import Dict, Any, List
from neo4j import AsyncSession
import logging
import json

logger = logging.getLogger(__name__)

async def store_run(session: AsyncSession, run: Dict[str, Any]) -> None:
    """Store a run in the database.
    
    Args:
        session: Database session
        run: Dictionary containing run data
        
    Raises:
        ValueError: If agent not found
    """
    try:
        tx = await session.begin_transaction()
        try:
            # First check if agent exists
            logger.info(f"Checking if agent {run['agent_id']} exists")
            result = await tx.run(
                """
                MATCH (a:Agent {id: $agent_id})
                RETURN a
                """,
                {"agent_id": run["agent_id"]}
            )
            record = await result.single()
            if not record:
                logger.error(f"Agent {run['agent_id']} not found")
                raise ValueError(f"Agent {run['agent_id']} not found")

            # Store run
            logger.info(f"Storing run {run['id']} for agent {run['agent_id']}")
            await tx.run(
                """
                MATCH (a:Agent {id: $agent_id})
                CREATE (r:Run {
                    id: $run_id,
                    timestamp: $timestamp,
                    status: $status,
                    metrics: $metrics
                })
                CREATE (a)-[:EXECUTED]->(r)
                """,
                {
                    "agent_id": run["agent_id"],
                    "run_id": run["id"],
                    "timestamp": run["timestamp"],
                    "status": run["status"],
                    "metrics": json.dumps(run["metrics"])
                }
            )
            logger.info(f"Successfully stored run {run['id']}")
            await tx.commit()
        except Exception as e:
            await tx.rollback()
            raise
        finally:
            await tx.close()
    except Exception as e:
        logger.error(f"Error storing run: {str(e)}")
        raise

async def get_runs(session: AsyncSession, agent_id: str = None) -> List[Dict[str, Any]]:
    """Get runs from the database.
    
    Args:
        session: Database session
        agent_id: Optional agent ID to filter runs
        
    Returns:
        List of run dictionaries
    """
    # First check if agent exists when filtering by agent_id
    if agent_id:
        result = await session.run(
            """
            MATCH (a:Agent {id: $agent_id})
            RETURN a
            """,
            {"agent_id": agent_id}
        )
        if not await result.single():
            raise ValueError(f"Agent {agent_id} not found")

    if agent_id:
        result = await session.run(
            """
            MATCH (a:Agent {id: $agent_id})-[:EXECUTED]->(r:Run)
            RETURN r.id as id, r.timestamp as timestamp, 
                   r.status as status, r.metrics as metrics,
                   a.id as agent_id
            """,
            {"agent_id": agent_id}
        )
    else:
        result = await session.run(
            """
            MATCH (a:Agent)-[:EXECUTED]->(r:Run)
            RETURN r.id as id, r.timestamp as timestamp, 
                   r.status as status, r.metrics as metrics,
                   a.id as agent_id
            """
        )
    
    runs = []
    async for record in result:
        runs.append({
            "id": record["id"],
            "timestamp": record["timestamp"],
            "status": record["status"],
            "metrics": record["metrics"],
            "agent_id": record["agent_id"]
        })
    return runs
