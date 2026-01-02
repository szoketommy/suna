import asyncio
from typing import Optional
from core.utils.logger import logger
from core.services.supabase import DBConnection
from core.utils.agentik_default_agent_service import agentiKDefaultAgentService

_installation_cache = set()
_installation_in_progress = set()

async def ensure_agentik_installed(account_id: str) -> None:
    if account_id in _installation_cache:
        return
    
    if account_id in _installation_in_progress:
        return
    
    try:
        _installation_in_progress.add(account_id)
        
        db = DBConnection()
        await db.initialize()
        client = await db.client
        
        existing = await client.from_('agents').select('agent_id').eq(
            'account_id', account_id
        ).eq('metadata->>is_agentik_default', 'true').limit(1).execute()
        
        if existing.data:
            _installation_cache.add(account_id)
            logger.debug(f"agentiK already installed for account {account_id}")
            return
        
        logger.info(f"Installing agentiK agent for account {account_id}")
        service = agentiKDefaultAgentService(db)
        agent_id = await service.install_agentik_agent_for_user(account_id, replace_existing=False)
        
        if agent_id:
            _installation_cache.add(account_id)
            logger.info(f"Successfully installed agentiK agent {agent_id} for account {account_id}")
        else:
            logger.warning(f"Failed to install agentiK agent for account {account_id}")
            
    except Exception as e:
        logger.error(f"Error ensuring agentiK installation for {account_id}: {e}")
    finally:
        _installation_in_progress.discard(account_id)


def trigger_agentik_installation(account_id: str) -> None:
    try:
        asyncio.create_task(ensure_agentik_installed(account_id))
    except RuntimeError:
        pass

