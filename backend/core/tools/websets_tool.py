from typing import Optional, List, Dict, Any
import asyncio
import structlog
import json
from decimal import Decimal
from exa_py import Exa
from exa_py.websets.types import (
    CreateWebsetParameters,
    CreateEnrichmentParameters
)
from core.agentpress.tool import Tool, ToolResult, openapi_schema, tool_metadata
from core.utils.config import config, EnvMode
from core.utils.logger import logger
from core.agentpress.thread_manager import ThreadManager
from core.billing.credits.manager import CreditManager
from core.services.supabase import DBConnection

@tool_metadata(
    display_name="Websets",
    description="Create and manage research collections for people, companies, papers, and articles with AI-powered search and enrichment",
    icon="Database",
    color="bg-zinc-100 dark:bg-zinc-800/50",
    weight=240,
    visible=True,
    usage_guide="""
### WEBSETS - FIND A LIST OF EXACTLY WHAT YOU'RE LOOKING FOR

**🎯 PERFECT FOR: Finding thousands of precise matches at scale**

Discover professionals, companies, research papers, articles, and more using AI-powered search that understands exactly what you need.

**⚠️ COST: Variable pricing based on usage** (1 credit = $0.01)
- Base search: 45 credits + 3 credits/result
- Enrichments: 10 credits/item batch
- Monitors: 5 credits/day

**🚀 PROVEN USE CASES:**

**Sales Intelligence:**
→ "US based startups having raised 10m$+ in longevity healthcare"
→ "B2B SaaS companies with 50-200 employees in NYC"
Result: Qualified lead lists with company details, decision-makers, funding info

**Recruiting & Talent:**
→ "Every engineer in San Francisco" (23k+ results)
→ "Senior ML engineers with Python and PyTorch experience"
Result: Profile URLs, past employers, education, skills, years of experience

**VC & Investment:**
→ "Find startups funded by YC. Get me their batch, status, and industries"
→ "All active VC firms in the USA with typical check sizes"
Result: Company profiles, funding rounds, founding teams, industries

**Market Research:**
→ "All top executives at a Fortune 500 firm" (4k+ results)
→ "Every news story about M&A in 2025" (68k+ results)
Result: Comprehensive data for competitive intelligence and trend analysis

**🎨 ENTITY TYPES (Flexible - Any String):**

Common types:
- `company`: Businesses, startups, enterprises, VC firms
- `person`: Professionals, engineers, executives, candidates, designers
- `research_paper`: Academic papers, studies, technical docs
- `article`: News stories, blog posts, analysis

Creative types (examples):
- `github_repo`: Open source repositories
- `museum_exhibition`: Art exhibitions and displays
- `animated_music_video`: Music videos with animation
- `sci_fi_book_review`: Book reviews in sci-fi genre
- `podcast_episode`: Podcast content
- `conference_talk`: Tech talks and presentations
- `startup_job_posting`: Job listings from startups

**You can use ANY descriptive string as entity_type!** The AI search understands your intent.

**💡 WORKFLOW:**

1. **CREATE** a webset with specific criteria
   → Use natural language: "Find longevity healthcare startups with 10M+ funding"
   → **CRITICAL**: Immediately after calling create_webset(), use the `ask` tool to inform user:
     "I've started creating your webset! This typically takes 1-3 minutes. Watch the Webset viewer above - it will populate in real-time as results are discovered. You can give me instructions at any time to refine or modify the search!"
   
2. **MONITOR LIVE PROGRESS**
   → The frontend automatically polls and displays results as they're found
   → User can see progress: items found, completion %, time remaining
   → Results appear incrementally in the table
   
3. **INTERACT DURING PROCESSING**
   → User can ask to refine criteria, change query, or modify search at any time
   → You can respond to user requests while webset is processing
   → Be ready to adjust based on initial results they see
   
4. **REVIEW** results when complete
   → list_items to see what was found
   → Refine query if needed based on results
   
5. **ENRICH** with custom data
   → "Find CEO email and LinkedIn for each company"
   → "Get years of experience and skills for each person"
   
6. **MONITOR** for ongoing discovery
   → Set up daily/weekly alerts for new matches
   → Stay updated as new entities appear
   
7. **MANAGE** your collections
   → All websets tracked in thread
   → Access anytime with external_id

**✨ BEST PRACTICES:**

- Start with count=10-50 to validate query, then scale to 100s-1000s
- Use external_id for easy reference: "sf_engineers_2025", "yc_batch_w25"
- Specify criteria: location, funding stage, skills, experience level
- Review results before enriching (enrichments cost per item)
- Use monitors for ongoing research needs (recruiting pipelines, lead gen)
- Export results or integrate with your CRM/ATS

**📝 EXAMPLE QUERIES:**

Startup Discovery:
create_webset(
  query="AI startups in San Francisco with Series A funding in the last year",
  entity_type="company",
  count=100,
  criteria=["Founded after 2020", "Has AI/ML in product"],
  external_id="sf_ai_startups_2025"
)

Executive Search:
create_webset(
  query="CTOs at enterprise SaaS companies with 500+ employees",
  entity_type="person",
  count=50,
  enrichment_description="LinkedIn profile URL, years of experience, previous companies",
  external_id="cto_prospects"
)

Academic Research:
create_webset(
  query="Recent papers on transformer architectures published in 2024-2025",
  entity_type="research_paper",
  count=100,
  external_id="transformer_research"
)

GitHub Discovery:
create_webset(
  query="GitHub repos with 1000+ stars focused on AI agents",
  entity_type="custom",
  count=200,
  enrichment_description="Star count, primary language, top contributors",
  external_id="ai_agent_repos"
)

**🎯 KEY BENEFITS:**
✓ Scale: Find 1000s of results, not just 10
✓ Precision: AI understands nuanced criteria  
✓ Enrichment: Extract any data point you need
✓ Persistence: Collections saved across conversation
✓ Monitoring: Track new matches automatically
✓ Export: Use results in your workflows

**💬 USER COMMUNICATION:**

**CRITICAL - After creating a webset:**
1. **IMMEDIATELY use the `ask` tool** to inform the user:
   "I've started creating your webset! This process typically takes 1-3 minutes depending on the number of results requested. The webset is now processing in the background, and you can watch it populate in real-time in the Webset viewer above. Results will appear as they're discovered - you'll see them being added live!"

2. **Explain the live viewer:**
   "Keep an eye on the Webset viewer - it will automatically update as new results are found. You'll see a progress indicator showing how many results have been discovered so far."

3. **Encourage interaction:**
   "Feel free to give me instructions at any time while the webset is processing. You can ask me to refine the search, change criteria, add enrichments, or modify anything about the search. I'm here to help!"

4. **After completion:**
   - Always explain what Websets found and show sample results
   - Mention scale: "Found 234 matching companies"
   - Offer enrichment: "I can find emails/details for these results"
   - Suggest monitoring: "Want me to track new matches weekly?"
   - Make results actionable: Offer to export, analyze, or integrate
"""
)
class WebsetsTool(Tool):
    def __init__(self, thread_manager: ThreadManager):
        super().__init__()
        self.thread_manager = thread_manager
        self.api_key = config.EXA_API_KEY
        self.db = DBConnection()
        self.credit_manager = CreditManager()
        self.exa_client = None
        
        if self.api_key:
            self.exa_client = Exa(self.api_key)
            logger.info("Websets Tool initialized.")
        else:
            logger.warning("EXA_API_KEY not configured - Websets Tool will not be available")
    
    async def _get_current_thread_and_user(self) -> tuple[Optional[str], Optional[str]]:
        """Get current thread_id and user_id from execution context"""
        try:
            context_vars = structlog.contextvars.get_contextvars()
            thread_id = context_vars.get('thread_id')
            
            if not thread_id:
                logger.warning("No thread_id in execution context")
                return None, None
            
            client = await self.db.client
            thread = await client.from_('threads').select('account_id').eq('thread_id', thread_id).single().execute()
            if thread.data:
                return thread_id, thread.data.get('account_id')
                
        except Exception as e:
            logger.error(f"Failed to get thread context: {e}")
        return None, None
    
    async def _load_websets_state(self) -> Dict[str, Any]:
        """Load websets state from thread message (type='webset_state')"""
        try:
            thread_id, _ = await self._get_current_thread_and_user()
            if not thread_id:
                return {"websets": {}, "monitors": {}}
            
            client = await self.db.client
            result = await client.table('messages').select('*')\
                .eq('thread_id', thread_id)\
                .eq('type', 'webset_state')\
                .order('created_at', desc=True).limit(1).execute()
            
            if result.data and result.data[0].get('content'):
                content = result.data[0]['content']
                if isinstance(content, str):
                    content = json.loads(content)
                return content
            
            return {"websets": {}, "monitors": {}}
        except Exception as e:
            logger.error(f"Error loading websets state: {e}")
            return {"websets": {}, "monitors": {}}
    
    async def _save_websets_state(self, state: Dict[str, Any]):
        """Save websets state to thread message"""
        try:
            thread_id, _ = await self._get_current_thread_and_user()
            if not thread_id:
                logger.warning("Cannot save websets state: no thread_id")
                return
            
            client = await self.db.client
            
            # Find existing message
            result = await client.table('messages').select('message_id')\
                .eq('thread_id', thread_id)\
                .eq('type', 'webset_state')\
                .order('created_at', desc=True).limit(1).execute()
            
            if result.data:
                # Update existing
                await client.table('messages').update({'content': state})\
                    .eq('message_id', result.data[0]['message_id']).execute()
            else:
                # Create new
                await client.table('messages').insert({
                    'thread_id': thread_id,
                    'type': 'webset_state',
                    'content': state,
                    'is_llm_message': False,
                    'metadata': {}
                }).execute()
        except Exception as e:
            logger.error(f"Error saving websets state: {e}")
            raise
    
    def _calculate_credits(
        self,
        operation: str,
        result_count: int = 0,
        enrichment_count: int = 0,
        monitor_days: int = 0
    ) -> int:
        """Calculate credits (1 credit = 1 cent = $0.01)"""
        if operation == 'search':
            base_credits = 45
            results_credits = 3 * result_count
            return base_credits + results_credits
        elif operation == 'enrichment':
            return 10 * enrichment_count  # per item
        elif operation == 'monitor':
            return 5 * monitor_days  # per day
        return 0
    
    async def _deduct_credits(self, user_id: str, credits: int, description: str, thread_id: Optional[str] = None) -> bool:
        """Deduct credits for an operation"""
        if credits <= 0:
            return True
        
        amount_dollars = Decimal(credits) / 100  # Convert credits to dollars
        
        try:
            result = await self.credit_manager.deduct_credits(
                account_id=user_id,
                amount=amount_dollars,
                description=description,
                type='usage',
                thread_id=thread_id
            )
            
            if result.get('success'):
                new_balance = result.get('new_balance') or result.get('new_total', 0)
                logger.info(f"Deducted {credits} credits (${amount_dollars:.2f}) for {description}. New balance: ${new_balance:.2f}")
                return True
            else:
                error_msg = result.get('error', 'Unknown error')
                logger.warning(f"Failed to deduct credits: {error_msg}")
                return False
                
        except Exception as e:
            logger.error(f"Error deducting credits: {e}", exc_info=True)
            return False
    
    def _format_evaluations(self, evaluations: List[Dict]) -> List[Dict]:
        """Format criteria evaluations"""
        return [
            {
                "criterion": eval.get('criterion', ''),
                "satisfied": eval.get('satisfied', 'unclear'),  # "yes" | "no" | "unclear"
                "reasoning": eval.get('reasoning', ''),
                "references": eval.get('references', [])
            }
            for eval in evaluations
        ]
    
    def _format_enrichments(self, enrichments: List[Dict]) -> Dict[str, Any]:
        """Format enrichment results as key-value pairs"""
        formatted = {}
        for enrich in enrichments or []:
            if enrich.get('status') == 'completed':
                enrichment_id = enrich.get('enrichmentId', '')
                result = enrich.get('result', [])
                # Result is array, take first value
                formatted[enrichment_id] = result[0] if result else None
        return formatted
    
    def _format_company_result(self, item: Dict) -> Dict:
        """Format company item from API response"""
        props = item.get('properties', {})
        company = props.get('company', {})
        
        return {
            "id": item.get('id'),
            "name": company.get('name', ''),
            "industry": company.get('industry', ''),
            "location": company.get('location', ''),
            "logo_url": company.get('logoUrl', ''),
            "description": props.get('description', ''),
            "url": props.get('url', ''),
            "evaluations": self._format_evaluations(item.get('evaluations', [])),
            "enrichments": self._format_enrichments(item.get('enrichments', []))
        }
    
    def _format_person_result(self, item: Dict) -> Dict:
        """Format person item from API response"""
        props = item.get('properties', {})
        person = props.get('person', {})
        company = person.get('company', {})
        
        return {
            "id": item.get('id'),
            "name": person.get('name', ''),
            "position": person.get('position', ''),
            "company_name": company.get('name', ''),
            "location": person.get('location', ''),
            "picture_url": person.get('pictureUrl', ''),
            "description": props.get('description', ''),
            "url": props.get('url', ''),
            "evaluations": self._format_evaluations(item.get('evaluations', [])),
            "enrichments": self._format_enrichments(item.get('enrichments', []))
        }
    
    def _format_paper_result(self, item: Dict) -> Dict:
        """Format research paper item from API response"""
        props = item.get('properties', {})
        paper = props.get('researchPaper', {})
        
        return {
            "id": item.get('id'),
            "title": paper.get('title', ''),
            "authors": paper.get('authors', []),
            "publication": paper.get('publication', ''),
            "year": paper.get('year'),
            "citations": paper.get('citations', 0),
            "abstract": paper.get('abstract', ''),
            "url": props.get('url', ''),
            "evaluations": self._format_evaluations(item.get('evaluations', [])),
            "enrichments": self._format_enrichments(item.get('enrichments', []))
        }
    
    def _format_article_result(self, item: Dict) -> Dict:
        """Format article item from API response"""
        props = item.get('properties', {})
        article = props.get('article', {})
        
        return {
            "id": item.get('id'),
            "title": article.get('title', ''),
            "publisher": article.get('publisher', ''),
            "date": article.get('date', ''),
            "summary": article.get('summary', ''),
            "url": props.get('url', ''),
            "evaluations": self._format_evaluations(item.get('evaluations', [])),
            "enrichments": self._format_enrichments(item.get('enrichments', []))
        }
    
    def _status_to_str(self, status) -> str:
        """Convert status enum/object to string for JSON serialization"""
        if status is None:
            return None
        if isinstance(status, str):
            return status
        return str(status)
    
    def _format_item_by_type(self, item: Dict) -> Dict:
        """Format item based on entity type"""
        props = item.get('properties', {})
        entity_type = props.get('type', '').lower()
        
        if entity_type == 'company':
            return self._format_company_result(item)
        elif entity_type == 'person':
            return self._format_person_result(item)
        elif entity_type == 'research_paper' or entity_type == 'researchpaper':
            return self._format_paper_result(item)
        elif entity_type == 'article':
            return self._format_article_result(item)
        else:
            # Generic formatting for custom types
            return {
                "id": item.get('id'),
                "type": entity_type,
                "description": props.get('description', ''),
                "url": props.get('url', ''),
                "properties": props,
                "evaluations": self._format_evaluations(item.get('evaluations', [])),
                "enrichments": self._format_enrichments(item.get('enrichments', []))
            }
    
    # ==================== WEBSET MANAGEMENT METHODS ====================
    
    @openapi_schema({
        "type": "function",
        "function": {
            "name": "create_webset",
            "description": "Create a new Webset to find and collect entities matching your search criteria. Use this to discover people, companies, research papers, articles, or any custom entity type at scale.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Natural language search query describing what you're looking for. Be specific and descriptive. Examples: 'AI startups in San Francisco with Series A funding', 'Senior ML engineers with Python experience', 'Recent papers on transformer architectures'"
                    },
                    "entity_type": {
                        "type": "string",
                        "description": "Type of entity to search for. Can be any descriptive string. Common: 'company', 'person', 'research_paper', 'article'. Custom examples: 'github_repo', 'museum_exhibition', 'podcast_episode'. If omitted, will be auto-detected from query."
                    },
                    "count": {
                        "type": "integer",
                        "description": "Number of results to find (default: 10, max: 100+)",
                        "default": 10
                    },
                    "external_id": {
                        "type": "string",
                        "description": "User-friendly identifier for easy reference (e.g., 'sf_engineers_2025', 'yc_batch_w25')"
                    },
                    "criteria": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Additional search criteria. Auto-generated if omitted. Examples: ['Founded after 2020', 'Has AI/ML in product']"
                    },
                    "enrichment_description": {
                        "type": "string",
                        "description": "What data to extract from each result. Examples: 'LinkedIn profile URL', 'CEO email', 'Funding amount'"
                    },
                    "metadata": {
                        "type": "object",
                        "description": "Custom key-value pairs to associate with the webset"
                    }
                },
                "required": ["query"]
            }
        }
    })
    async def create_webset(
        self,
        query: str,
        entity_type: Optional[str] = None,
        count: int = 10,
        external_id: Optional[str] = None,
        criteria: Optional[List[str]] = None,
        enrichment_description: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> ToolResult:
        """Create a new Webset with search and optional enrichment"""
        if not self.exa_client:
            return self.fail_response(
                "Websets is not available. EXA_API_KEY is not configured. "
                "Please contact your administrator to enable this feature."
            )
        
        if not query:
            return self.fail_response("Search query is required.")
        
        thread_id, user_id = await self._get_current_thread_and_user()
        
        if config.ENV_MODE != EnvMode.LOCAL and (not thread_id or not user_id):
            return self.fail_response(
                "No active session context for billing. This tool requires an active agent session."
            )
        
        try:
            logger.info(f"Creating Exa webset for: '{query}' with {count} results")
            
            # Build request parameters
            search_params = {
                "query": query,
                "count": count,
            }
            
            if entity_type:
                search_params["entity"] = {"type": entity_type}
            
            if criteria:
                search_params["criteria"] = [{"description": c} for c in criteria]
            
            search_params["recall"] = True  # Get estimate of total matches
            
            params = CreateWebsetParameters(
                search=search_params,
                enrichments=[
                    {
                        "description": enrichment_description,
                        "format": "text"
                    }
                ] if enrichment_description else None,
                externalId=external_id,
                metadata=metadata or {}
            )
            
            # Execute API call with retry logic for duplicate external_id
            webset = None
            max_retries = 3
            retry_count = 0
            current_external_id = external_id
            
            while webset is None and retry_count < max_retries:
                try:
                    # Create new params with current external_id (Pydantic models are immutable)
                    create_params = CreateWebsetParameters(
                        search=search_params,
                        enrichments=[
                            {
                                "description": enrichment_description,
                                "format": "text"
                            }
                        ] if enrichment_description else None,
                        externalId=current_external_id,
                        metadata=metadata or {}
                    )
                    
                    webset = await asyncio.to_thread(
                        self.exa_client.websets.create,
                        params=create_params
                    )
                    logger.info(f"Webset created with ID: {webset.id}")
                    external_id = current_external_id  # Update to final external_id
                    break
                    
                except ValueError as e:
                    error_str = str(e)
                    # Handle 409 Conflict - webset with external_id already exists
                    if "409" in error_str and current_external_id:
                        retry_count += 1
                        logger.info(f"Webset with external_id '{current_external_id}' already exists (attempt {retry_count}/{max_retries})")
                        
                        # Try to find existing webset by external_id
                        try:
                            # List websets and find by external_id
                            all_websets = await asyncio.to_thread(
                                self.exa_client.websets.list
                            )
                            existing_webset = None
                            for ws in all_websets.results if hasattr(all_websets, 'results') else []:
                                if getattr(ws, 'external_id', None) == current_external_id:
                                    existing_webset = ws
                                    break
                            
                            if existing_webset:
                                # Get full webset details
                                webset = await asyncio.to_thread(
                                    self.exa_client.websets.get,
                                    existing_webset.id,
                                    expand=["searches", "enrichments"]
                                )
                                logger.info(f"Retrieved existing webset {webset.id} with external_id '{current_external_id}'")
                                external_id = current_external_id  # Update to final external_id
                                break
                        except Exception as retrieve_error:
                            logger.warning(f"Could not retrieve existing webset: {repr(retrieve_error)}")
                        
                        # If we didn't find it or retrieval failed, make external_id unique
                        if webset is None:
                            import time
                            import random
                            # Add timestamp and random suffix to ensure uniqueness
                            current_external_id = f"{external_id}_{int(time.time())}_{random.randint(1000, 9999)}"
                            logger.info(f"Making external_id unique: '{current_external_id}'")
                    else:
                        # Re-raise if it's not a 409 or no external_id
                        raise
            
            if webset is None:
                return self.fail_response(
                    f"Failed to create webset after {max_retries} attempts. "
                    "The external_id may already exist and could not be retrieved."
                )
            
            # Calculate and deduct credits BEFORE processing (charge upfront)
            credits = self._calculate_credits('search', result_count=count)
            
            if config.ENV_MODE == EnvMode.LOCAL:
                logger.info("Running in LOCAL mode - skipping billing")
                cost_str = f"{credits} credits (LOCAL - not charged)"
            else:
                credits_deducted = await self._deduct_credits(
                    user_id,
                    credits,
                    f"Webset creation: {count} results requested",
                    thread_id
                )
                if not credits_deducted:
                    # Cancel the webset if we can't charge
                    try:
                        await asyncio.to_thread(self.exa_client.websets.delete, webset.id)
                    except Exception:
                        pass
                    return self.fail_response(
                        f"Insufficient credits. This search costs {credits} credits ({count} results). "
                        "Please add credits to continue."
                    )
                cost_str = f"{credits} credits"
            
            # Get initial item count from search progress
            item_count = 0
            if webset.searches and len(webset.searches) > 0:
                first_search = webset.searches[0]
                if hasattr(first_search, 'progress') and hasattr(first_search.progress, 'found'):
                    item_count = first_search.progress.found
            
            # Store webset info in thread state immediately
            state = await self._load_websets_state()
            # Convert status to string for JSON serialization
            webset_status_str = self._status_to_str(webset.status)
            
            state.setdefault("websets", {})[webset.id] = {
                "id": webset.id,
                "external_id": external_id or getattr(webset, 'external_id', None),
                "entity_type": entity_type or (webset.searches[0].entity.type if webset.searches and len(webset.searches) > 0 and hasattr(webset.searches[0], 'entity') else ''),
                "query": query,
                "created_at": str(webset.created_at),
                "status": webset_status_str,
                "item_count": item_count,
                "count": count
            }
            await self._save_websets_state(state)
            
            # Return immediately - frontend will poll for updates
            # Status will be "running" while search is in progress
            logger.info(f"Webset {webset.id} created and processing in background (status: {webset.status})")
            
            # Get search progress info
            search_progress = None
            if webset.searches and len(webset.searches) > 0:
                s = webset.searches[0]
                if hasattr(s, 'progress'):
                    search_progress = {
                        "found": getattr(s.progress, 'found', 0),
                        "analyzed": getattr(s.progress, 'analyzed', 0),
                        "completion": getattr(s.progress, 'completion', 0),
                        "time_left": getattr(s.progress, 'time_left', None)
                    }
            
            # Format response - return immediately without waiting
            # Convert status to string to avoid JSON serialization issues
            webset_status = self._status_to_str(webset.status)
            
            output = {
                "webset_id": webset.id,
                "external_id": external_id or getattr(webset, 'external_id', None),
                "status": webset_status,
                "query": query,
                "entity_type": entity_type or (webset.searches[0].entity.type if webset.searches and len(webset.searches) > 0 and hasattr(webset.searches[0], 'entity') else 'auto-detected'),
                "item_count": item_count,
                "cost_deducted": cost_str,
                "is_processing": webset_status in ["running", "pending"],
                "progress": search_progress,
                "message": "Webset created! Results are being discovered in real-time." if webset_status in ["running", "pending"] else "Webset ready",
                "searches": [
                    {
                        "id": s.id,
                        "status": self._status_to_str(s.status),
                        "query": s.query,
                        "progress": {
                            "found": s.progress.found if hasattr(s, 'progress') else 0,
                            "completion": s.progress.completion if hasattr(s, 'progress') else 0
                        }
                    }
                    for s in webset.searches
                ] if webset.searches else [],
                "enrichments": [
                    {
                        "id": e.id,
                        "status": self._status_to_str(e.status),
                        "title": getattr(e, 'title', None),
                        "description": getattr(e, 'description', None)
                    }
                    for e in webset.enrichments
                ] if webset.enrichments else []
            }
            
            logger.info(f"Successfully created webset {webset.id} with {item_count} items")
            return self.success_response(output)
            
        except Exception as e:
            logger.error(f"Webset creation failed: {repr(e)}", exc_info=True)
            error_str = str(e)
            if "401" in error_str:
                return self.fail_response("Authentication failed with Exa API. Please check your API key configuration.")
            elif "400" in error_str:
                return self.fail_response("Invalid request to Exa API. Please check your query format.")
            else:
                return self.fail_response(f"Failed to create webset: {error_str}")
    
    @openapi_schema({
        "type": "function",
        "function": {
            "name": "preview_webset",
            "description": "Preview what a search query will detect before creating a full webset. Shows auto-detected entity type, criteria, and suggested enrichments.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Natural language search query to preview"
                    },
                    "entity_type": {
                        "type": "string",
                        "description": "Optional entity type hint for the preview"
                    }
                },
                "required": ["query"]
            }
        }
    })
    async def preview_webset(
        self,
        query: str,
        entity_type: Optional[str] = None
    ) -> ToolResult:
        """Preview what a webset search will detect"""
        if not self.exa_client:
            return self.fail_response("Websets is not available. EXA_API_KEY is not configured.")
        
        if not query:
            return self.fail_response("Search query is required.")
        
        try:
            preview_params = {
                "search": {
                    "query": query,
                    "count": 10  # Preview returns max 10 items
                }
            }
            
            if entity_type:
                preview_params["search"]["entity"] = {"type": entity_type}
            
            preview = await asyncio.to_thread(
                self.exa_client.websets.preview,
                params=preview_params
            )
            
            output = {
                "query": query,
                "detected_entity": preview.search.entity.type if preview.search.entity else None,
                "detected_criteria": [c.description for c in preview.search.criteria] if preview.search.criteria else [],
                "suggested_enrichments": [
                    {
                        "description": e.description,
                        "format": e.format
                    }
                    for e in preview.enrichments
                ] if preview.enrichments else [],
                "preview_items": [
                    self._format_item_by_type(item)
                    for item in preview.items[:5]  # Show first 5 preview items
                ] if preview.items else []
            }
            
            return self.success_response(output)
            
        except Exception as e:
            logger.error(f"Webset preview failed: {repr(e)}", exc_info=True)
            return self.fail_response(f"Failed to preview webset: {str(e)}")
    
    @openapi_schema({
        "type": "function",
        "function": {
            "name": "list_websets",
            "description": "List all websets created in this conversation thread",
            "parameters": {
                "type": "object",
                "properties": {
                    "sync_with_api": {
                        "type": "boolean",
                        "description": "Fetch latest status from API (default: false)",
                        "default": False
                    }
                }
            }
        }
    })
    async def list_websets(
        self,
        sync_with_api: bool = False
    ) -> ToolResult:
        """List all websets from thread state"""
        try:
            state = await self._load_websets_state()
            websets = state.get("websets", {})
            
            # Optionally sync with API for latest status
            if sync_with_api and self.exa_client:
                for webset_id in list(websets.keys()):
                    try:
                        api_webset = await asyncio.to_thread(
                            self.exa_client.websets.get,
                            webset_id
                        )
                        # Update cached state with latest from API
                        if webset_id in websets:
                            websets[webset_id]["status"] = api_webset.status
                            if api_webset.searches and len(api_webset.searches) > 0:
                                first_search = api_webset.searches[0]
                                if hasattr(first_search, 'progress') and hasattr(first_search.progress, 'found'):
                                    websets[webset_id]["item_count"] = first_search.progress.found
                    except Exception:
                        pass  # Webset may have been deleted
            
            output = {
                "websets": list(websets.values()),
                "total": len(websets)
            }
            
            return self.success_response(output)
            
        except Exception as e:
            logger.error(f"Failed to list websets: {repr(e)}", exc_info=True)
            return self.fail_response(f"Failed to list websets: {str(e)}")
    
    @openapi_schema({
        "type": "function",
        "function": {
            "name": "get_webset",
            "description": "Get full details of a webset including searches, enrichments, and optionally items",
            "parameters": {
                "type": "object",
                "properties": {
                    "webset_id": {
                        "type": "string",
                        "description": "Webset ID or external_id"
                    },
                    "include_items": {
                        "type": "boolean",
                        "description": "Include full item list (default: false)",
                        "default": False
                    }
                },
                "required": ["webset_id"]
            }
        }
    })
    async def get_webset(
        self,
        webset_id: str,
        include_items: bool = False
    ) -> ToolResult:
        """Get full webset details"""
        if not self.exa_client:
            return self.fail_response("Websets is not available. EXA_API_KEY is not configured.")
        
        try:
            # Can use either webset ID or externalId
            expand = ["items"] if include_items else None
            webset = await asyncio.to_thread(
                self.exa_client.websets.get,
                webset_id,
                expand=expand
            )
            
            # Update thread message cache
            state = await self._load_websets_state()
            if webset.id in state.get("websets", {}):
                item_count = 0
                if webset.searches and len(webset.searches) > 0:
                    first_search = webset.searches[0]
                    if hasattr(first_search, 'progress') and hasattr(first_search.progress, 'found'):
                        item_count = first_search.progress.found
                state["websets"][webset.id].update({
                    "status": self._status_to_str(webset.status),
                    "item_count": item_count,
                    "updated_at": str(webset.updated_at)
                })
                await self._save_websets_state(state)
            
            output = {
                "id": webset.id,
                "external_id": getattr(webset, 'external_id', None),
                "status": self._status_to_str(webset.status),
                "title": webset.title,
                "searches": [
                    {
                        "id": s.id,
                        "status": self._status_to_str(s.status),
                        "query": s.query,
                        "entity_type": s.entity.type if s.entity else None,
                        "count": s.count,
                        "progress": {
                            "found": s.progress.found,
                            "analyzed": s.progress.analyzed,
                            "completion": s.progress.completion,
                            "time_left": s.progress.time_left
                        } if hasattr(s, 'progress') else None
                    }
                    for s in webset.searches
                ] if webset.searches else [],
                "enrichments": [
                    {
                        "id": e.id,
                        "status": self._status_to_str(e.status),
                        "title": e.title,
                        "description": e.description,
                        "format": e.format
                    }
                    for e in webset.enrichments
                ] if webset.enrichments else [],
                "monitors": [
                    {
                        "id": m.id,
                        "status": self._status_to_str(m.status),
                        "next_run": str(m.next_run_at) if m.next_run_at else None
                    }
                    for m in webset.monitors
                ] if webset.monitors else [],
                "items": [
                    self._format_item_by_type(item)
                    for item in webset.items
                ] if include_items and hasattr(webset, 'items') and webset.items else None,
                "created_at": str(webset.created_at),
                "updated_at": str(webset.updated_at)
            }
            
            return self.success_response(output)
            
        except Exception as e:
            logger.error(f"Failed to get webset: {repr(e)}", exc_info=True)
            return self.fail_response(f"Failed to get webset: {str(e)}")
    
    def _get_status_message(self, status: str, progress: Optional[Dict], is_complete: bool) -> str:
        """Generate a human-readable status message"""
        if is_complete:
            found = progress.get("found", 0) if progress else 0
            return f"Search complete! Found {found} matching results."
        
        if status in ["running", "pending"]:
            if progress:
                found = progress.get("found", 0)
                completion = progress.get("completion", 0)
                time_left = progress.get("time_left")
                msg = f"Searching... {found} results found ({completion}% complete)"
                if time_left:
                    msg += f" - ~{time_left}s remaining"
                return msg
            return "Starting search..."
        
        return f"Status: {status}"
    
    @openapi_schema({
        "type": "function",
        "function": {
            "name": "delete_webset",
            "description": "Delete a webset and remove it from thread state",
            "parameters": {
                "type": "object",
                "properties": {
                    "webset_id": {
                        "type": "string",
                        "description": "Webset ID or external_id"
                    }
                },
                "required": ["webset_id"]
            }
        }
    })
    async def delete_webset(
        self,
        webset_id: str
    ) -> ToolResult:
        """Delete a webset"""
        if not self.exa_client:
            return self.fail_response("Websets is not available. EXA_API_KEY is not configured.")
        
        try:
            # Delete from Exa API
            await asyncio.to_thread(
                self.exa_client.websets.delete,
                webset_id
            )
            
            # Remove from thread message state
            state = await self._load_websets_state()
            if webset_id in state.get("websets", {}):
                del state["websets"][webset_id]
            
            # Remove associated monitors
            monitors_to_remove = [
                mid for mid, m in state.get("monitors", {}).items()
                if m.get("webset_id") == webset_id
            ]
            for mid in monitors_to_remove:
                del state["monitors"][mid]
            
            await self._save_websets_state(state)
            
            output = {
                "webset_id": webset_id,
                "deleted": True
            }
            
            return self.success_response(output)
            
        except Exception as e:
            logger.error(f"Failed to delete webset: {repr(e)}", exc_info=True)
            return self.fail_response(f"Failed to delete webset: {str(e)}")
    
    # ==================== SEARCH MANAGEMENT METHODS ====================
    
    @openapi_schema({
        "type": "function",
        "function": {
            "name": "create_search",
            "description": "Add an additional search to an existing webset to expand the collection",
            "parameters": {
                "type": "object",
                "properties": {
                    "webset_id": {
                        "type": "string",
                        "description": "Webset ID or external_id"
                    },
                    "query": {
                        "type": "string",
                        "description": "Natural language search query"
                    },
                    "count": {
                        "type": "integer",
                        "description": "Number of results to find",
                        "default": 10
                    },
                    "entity_type": {
                        "type": "string",
                        "description": "Entity type (optional, uses webset default if omitted)"
                    },
                    "criteria": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Additional search criteria"
                    },
                    "behavior": {
                        "type": "string",
                        "enum": ["override", "append"],
                        "description": "override = replace existing items, append = add to existing (default: append)",
                        "default": "append"
                    }
                },
                "required": ["webset_id", "query", "count"]
            }
        }
    })
    async def create_search(
        self,
        webset_id: str,
        query: str,
        count: int,
        entity_type: Optional[str] = None,
        criteria: Optional[List[str]] = None,
        behavior: str = "append"
    ) -> ToolResult:
        """Add additional search to existing webset"""
        if not self.exa_client:
            return self.fail_response("Websets is not available. EXA_API_KEY is not configured.")
        
        thread_id, user_id = await self._get_current_thread_and_user()
        
        try:
            search_params = {
                "query": query,
                "count": count,
                "recall": True,
                "behavior": behavior,
            }
            
            if entity_type:
                search_params["entity"] = {"type": entity_type}
            
            if criteria:
                search_params["criteria"] = [{"description": c} for c in criteria]
            
            search = await asyncio.to_thread(
                self.exa_client.websets.create_search,
                webset_id=webset_id,
                params=search_params
            )
            
            # Wait for completion
            webset = await asyncio.to_thread(
                self.exa_client.websets.wait_until_idle,
                webset_id
            )
            
            # Calculate and deduct credits
            credits = self._calculate_credits('search', result_count=count)
            
            if config.ENV_MODE != EnvMode.LOCAL and user_id:
                credits_deducted = await self._deduct_credits(
                    user_id,
                    credits,
                    f"Search added to webset: {count} results",
                    thread_id
                )
                if not credits_deducted:
                    return self.fail_response(
                        f"Insufficient credits. This search costs {credits} credits."
                    )
            
            output = {
                "search_id": search.id,
                "webset_id": webset_id,
                "status": search.status,
                "query": query,
                "count": count,
                "behavior": behavior,
                "cost_deducted": f"{credits} credits" if config.ENV_MODE != EnvMode.LOCAL else f"{credits} credits (LOCAL)"
            }
            
            return self.success_response(output)
            
        except Exception as e:
            logger.error(f"Failed to create search: {repr(e)}", exc_info=True)
            return self.fail_response(f"Failed to create search: {str(e)}")
    
    @openapi_schema({
        "type": "function",
        "function": {
            "name": "list_searches",
            "description": "List all searches for a webset",
            "parameters": {
                "type": "object",
                "properties": {
                    "webset_id": {
                        "type": "string",
                        "description": "Webset ID or external_id"
                    }
                },
                "required": ["webset_id"]
            }
        }
    })
    async def list_searches(
        self,
        webset_id: str
    ) -> ToolResult:
        """List all searches for a webset"""
        if not self.exa_client:
            return self.fail_response("Websets is not available. EXA_API_KEY is not configured.")
        
        try:
            webset = await asyncio.to_thread(
                self.exa_client.websets.get,
                webset_id
            )
            
            searches = [
                {
                    "id": s.id,
                    "status": self._status_to_str(s.status),
                    "query": s.query,
                    "entity_type": s.entity.type if s.entity else None,
                    "count": s.count,
                    "progress": {
                        "found": s.progress.found,
                        "analyzed": s.progress.analyzed,
                        "completion": s.progress.completion,
                        "time_left": s.progress.time_left
                    } if hasattr(s, 'progress') else None,
                    "behavior": s.behavior if hasattr(s, 'behavior') else None,
                    "created_at": str(s.created_at)
                }
                for s in webset.searches
            ] if webset.searches else []
            
            output = {
                "webset_id": webset_id,
                "searches": searches,
                "total": len(searches)
            }
            
            return self.success_response(output)
            
        except Exception as e:
            logger.error(f"Failed to list searches: {repr(e)}", exc_info=True)
            return self.fail_response(f"Failed to list searches: {str(e)}")
    
    @openapi_schema({
        "type": "function",
        "function": {
            "name": "cancel_search",
            "description": "Cancel a running search",
            "parameters": {
                "type": "object",
                "properties": {
                    "webset_id": {
                        "type": "string",
                        "description": "Webset ID or external_id"
                    },
                    "search_id": {
                        "type": "string",
                        "description": "Specific search ID to cancel, or omit to cancel all running operations"
                    }
                },
                "required": ["webset_id"]
            }
        }
    })
    async def cancel_search(
        self,
        webset_id: str,
        search_id: Optional[str] = None
    ) -> ToolResult:
        """Cancel a running search"""
        if not self.exa_client:
            return self.fail_response("Websets is not available. EXA_API_KEY is not configured.")
        
        try:
            if search_id:
                await asyncio.to_thread(
                    self.exa_client.websets.cancel_search,
                    webset_id=webset_id,
                    search_id=search_id
                )
            else:
                # Cancel entire webset (cancels all running operations)
                await asyncio.to_thread(
                    self.exa_client.websets.cancel,
                    webset_id
                )
            
            output = {
                "webset_id": webset_id,
                "search_id": search_id,
                "cancelled": True
            }
            
            return self.success_response(output)
            
        except Exception as e:
            logger.error(f"Failed to cancel search: {repr(e)}", exc_info=True)
            return self.fail_response(f"Failed to cancel search: {str(e)}")
    
    # ==================== ITEM MANAGEMENT METHODS ====================
    
    @openapi_schema({
        "type": "function",
        "function": {
            "name": "list_items",
            "description": "List all items in a webset with cursor-based pagination",
            "parameters": {
                "type": "object",
                "properties": {
                    "webset_id": {
                        "type": "string",
                        "description": "Webset ID or external_id"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Items per page (default: 50, max: 100)",
                        "default": 50
                    },
                    "cursor": {
                        "type": "string",
                        "description": "Pagination cursor from previous response (use next_cursor value)"
                    }
                },
                "required": ["webset_id"]
            }
        }
    })
    async def list_items(
        self,
        webset_id: str,
        limit: int = 50,
        cursor: Optional[str] = None
    ) -> ToolResult:
        """List all items in a webset using cursor-based pagination"""
        if not self.exa_client:
            return self.fail_response("Websets is not available. EXA_API_KEY is not configured.")
        
        try:
            # Build kwargs for the API call - only include params that are set
            kwargs = {"limit": limit}
            if cursor:
                kwargs["cursor"] = cursor
            
            items_response = await asyncio.to_thread(
                self.exa_client.websets.items.list,
                webset_id,
                **kwargs
            )
            
            items = items_response.data if items_response else []
            formatted_items = [self._format_item_by_type(item) for item in items]
            
            output = {
                "webset_id": webset_id,
                "items": formatted_items,
                "total": len(formatted_items),
                "limit": limit,
                "has_more": getattr(items_response, 'has_more', False),
                "next_cursor": getattr(items_response, 'next_cursor', None)
            }
            
            logger.info(f"Retrieved {len(formatted_items)} items from webset {webset_id}")
            return self.success_response(output)
            
        except Exception as e:
            logger.error(f"Failed to list items: {repr(e)}", exc_info=True)
            return self.fail_response(f"Failed to list items: {str(e)}")
    
    @openapi_schema({
        "type": "function",
        "function": {
            "name": "get_item",
            "description": "Get full details for a specific item in a webset",
            "parameters": {
                "type": "object",
                "properties": {
                    "webset_id": {
                        "type": "string",
                        "description": "Webset ID or external_id"
                    },
                    "item_id": {
                        "type": "string",
                        "description": "Item ID"
                    }
                },
                "required": ["webset_id", "item_id"]
            }
        }
    })
    async def get_item(
        self,
        webset_id: str,
        item_id: str
    ) -> ToolResult:
        """Get specific item details"""
        if not self.exa_client:
            return self.fail_response("Websets is not available. EXA_API_KEY is not configured.")
        
        try:
            item = await asyncio.to_thread(
                self.exa_client.websets.items.get,
                webset_id=webset_id,
                item_id=item_id
            )
            
            formatted_item = self._format_item_by_type(item)
            
            output = {
                "webset_id": webset_id,
                "item": formatted_item
            }
            
            return self.success_response(output)
            
        except Exception as e:
            logger.error(f"Failed to get item: {repr(e)}", exc_info=True)
            return self.fail_response(f"Failed to get item: {str(e)}")
    
    # ==================== ENRICHMENT MANAGEMENT METHODS ====================
    
    @openapi_schema({
        "type": "function",
        "function": {
            "name": "create_enrichment",
            "description": "Create an enrichment to extract additional data from all items in a webset",
            "parameters": {
                "type": "object",
                "properties": {
                    "webset_id": {
                        "type": "string",
                        "description": "Webset ID or external_id"
                    },
                    "description": {
                        "type": "string",
                        "description": "What to find/extract for each item. Examples: 'Find CEO email', 'Get funding amount', 'Extract LinkedIn profile URL'"
                    },
                    "format": {
                        "type": "string",
                        "enum": ["text", "date", "number", "options", "email", "phone", "url"],
                        "description": "Format of enrichment result (auto-detected if omitted)"
                    },
                    "options": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "If format='options', list of choices"
                    }
                },
                "required": ["webset_id", "description"]
            }
        }
    })
    async def create_enrichment(
        self,
        webset_id: str,
        description: str,
        format: Optional[str] = None,
        options: Optional[List[str]] = None
    ) -> ToolResult:
        """Create enrichment for webset items"""
        if not self.exa_client:
            return self.fail_response("Websets is not available. EXA_API_KEY is not configured.")
        
        thread_id, user_id = await self._get_current_thread_and_user()
        
        try:
            enrichment_params = CreateEnrichmentParameters(
                description=description,
                format=format,
                options=[{"label": opt} for opt in options] if options else None,
                metadata={}
            )
            
            enrichment = await asyncio.to_thread(
                self.exa_client.websets.enrichments.create,
                webset_id=webset_id,
                params=enrichment_params
            )
            
            # Wait for completion (enrichments can take minutes)
            webset = await asyncio.to_thread(
                self.exa_client.websets.wait_until_idle,
                webset_id
            )
            
            # Get item count from webset
            webset = await asyncio.to_thread(
                self.exa_client.websets.get,
                webset_id
            )
            item_count = 0
            if webset.searches and len(webset.searches) > 0:
                first_search = webset.searches[0]
                if hasattr(first_search, 'progress') and hasattr(first_search.progress, 'found'):
                    item_count = first_search.progress.found
            
            # Calculate and deduct credits
            credits = self._calculate_credits('enrichment', enrichment_count=item_count)
            
            if config.ENV_MODE != EnvMode.LOCAL and user_id:
                credits_deducted = await self._deduct_credits(
                    user_id,
                    credits,
                    f"Enrichment for webset: {item_count} items",
                    thread_id
                )
                if not credits_deducted:
                    return self.fail_response(
                        f"Insufficient credits. This enrichment costs {credits} credits ({item_count} items)."
                    )
            
            output = {
                "enrichment_id": enrichment.id,
                "webset_id": webset_id,
                "status": self._status_to_str(enrichment.status),
                "title": enrichment.title,
                "description": description,
                "format": enrichment.format,
                "item_count": item_count,
                "cost_deducted": f"{credits} credits" if config.ENV_MODE != EnvMode.LOCAL else f"{credits} credits (LOCAL)"
            }
            
            logger.info(f"Created enrichment {enrichment.id} for webset {webset_id}")
            return self.success_response(output)
            
        except Exception as e:
            logger.error(f"Failed to create enrichment: {repr(e)}", exc_info=True)
            return self.fail_response(f"Failed to create enrichment: {str(e)}")
    
    @openapi_schema({
        "type": "function",
        "function": {
            "name": "get_enrichment",
            "description": "Get enrichment details and status",
            "parameters": {
                "type": "object",
                "properties": {
                    "webset_id": {
                        "type": "string",
                        "description": "Webset ID or external_id"
                    },
                    "enrichment_id": {
                        "type": "string",
                        "description": "Enrichment ID"
                    }
                },
                "required": ["webset_id", "enrichment_id"]
            }
        }
    })
    async def get_enrichment(
        self,
        webset_id: str,
        enrichment_id: str
    ) -> ToolResult:
        """Get enrichment details"""
        if not self.exa_client:
            return self.fail_response("Websets is not available. EXA_API_KEY is not configured.")
        
        try:
            enrichment = await asyncio.to_thread(
                self.exa_client.websets.enrichments.get,
                webset_id=webset_id,
                enrichment_id=enrichment_id
            )
            
            output = {
                "id": enrichment.id,
                "webset_id": webset_id,
                "status": self._status_to_str(enrichment.status),
                "title": enrichment.title,
                "description": enrichment.description,
                "format": enrichment.format,
                "created_at": str(enrichment.created_at),
                "updated_at": str(enrichment.updated_at)
            }
            
            return self.success_response(output)
            
        except Exception as e:
            logger.error(f"Failed to get enrichment: {repr(e)}", exc_info=True)
            return self.fail_response(f"Failed to get enrichment: {str(e)}")
    
    @openapi_schema({
        "type": "function",
        "function": {
            "name": "cancel_enrichment",
            "description": "Cancel a running enrichment",
            "parameters": {
                "type": "object",
                "properties": {
                    "webset_id": {
                        "type": "string",
                        "description": "Webset ID or external_id"
                    },
                    "enrichment_id": {
                        "type": "string",
                        "description": "Enrichment ID"
                    }
                },
                "required": ["webset_id", "enrichment_id"]
            }
        }
    })
    async def cancel_enrichment(
        self,
        webset_id: str,
        enrichment_id: str
    ) -> ToolResult:
        """Cancel running enrichment"""
        if not self.exa_client:
            return self.fail_response("Websets is not available. EXA_API_KEY is not configured.")
        
        try:
            await asyncio.to_thread(
                self.exa_client.websets.enrichments.cancel,
                webset_id=webset_id,
                enrichment_id=enrichment_id
            )
            
            output = {
                "webset_id": webset_id,
                "enrichment_id": enrichment_id,
                "cancelled": True
            }
            
            return self.success_response(output)
            
        except Exception as e:
            logger.error(f"Failed to cancel enrichment: {repr(e)}", exc_info=True)
            return self.fail_response(f"Failed to cancel enrichment: {str(e)}")
    
    # ==================== MONITOR MANAGEMENT METHODS ====================
    
    @openapi_schema({
        "type": "function",
        "function": {
            "name": "create_monitor",
            "description": "Create a monitor to automatically track new matching results",
            "parameters": {
                "type": "object",
                "properties": {
                    "webset_id": {
                        "type": "string",
                        "description": "Webset ID or external_id"
                    },
                    "frequency": {
                        "type": "string",
                        "description": "How often to run: 'daily', 'weekly', 'hourly', or custom cron expression (e.g., '0 9 * * *' for daily at 9 AM)",
                        "default": "daily"
                    },
                    "count": {
                        "type": "integer",
                        "description": "Max results to find per run (default: 10)",
                        "default": 10
                    }
                },
                "required": ["webset_id"]
            }
        }
    })
    async def create_monitor(
        self,
        webset_id: str,
        frequency: str = "daily",
        count: int = 10
    ) -> ToolResult:
        """Create monitor for webset"""
        if not self.exa_client:
            return self.fail_response("Websets is not available. EXA_API_KEY is not configured.")
        
        thread_id, user_id = await self._get_current_thread_and_user()
        
        try:
            # Convert frequency to cron expression
            cron_map = {
                "daily": "0 9 * * *",  # Daily at 9 AM
                "weekly": "0 9 * * 1",  # Weekly on Monday at 9 AM
                "hourly": "0 * * * *"  # Every hour
            }
            
            cron_expression = cron_map.get(frequency.lower(), frequency)
            
            # Get webset to use its search parameters
            webset = await asyncio.to_thread(
                self.exa_client.websets.get,
                webset_id
            )
            
            # Use last search parameters if available
            last_search = webset.searches[-1] if webset.searches else None
            
            monitor_params = {
                "cadence": {
                    "cron": cron_expression,
                    "timezone": "UTC"
                },
                "behavior": {
                    "type": "search",
                    "config": {
                        "count": count,
                        "behavior": "append"
                    }
                }
            }
            
            # Add search parameters from last search if available
            if last_search:
                if hasattr(last_search, 'query') and last_search.query:
                    monitor_params["behavior"]["config"]["query"] = last_search.query
                if hasattr(last_search, 'criteria') and last_search.criteria:
                    monitor_params["behavior"]["config"]["criteria"] = [
                        {"description": c.description} if hasattr(c, 'description') else {"description": str(c)}
                        for c in last_search.criteria
                    ]
                if hasattr(last_search, 'entity') and last_search.entity:
                    monitor_params["behavior"]["config"]["entity"] = {"type": last_search.entity.type}
            
            monitor = await asyncio.to_thread(
                self.exa_client.websets.monitors.create,
                webset_id=webset_id,
                params=monitor_params
            )
            
            # Store in thread message state
            state = await self._load_websets_state()
            state.setdefault("monitors", {})[monitor.id] = {
                "id": monitor.id,
                "webset_id": webset_id,
                "frequency": frequency,
                "cron": monitor.cadence.cron,
                "next_run": str(monitor.next_run_at) if monitor.next_run_at else None,
                "created_at": str(monitor.created_at)
            }
            await self._save_websets_state(state)
            
            output = {
                "monitor_id": monitor.id,
                "webset_id": webset_id,
                "status": self._status_to_str(monitor.status),
                "frequency": frequency,
                "cron": monitor.cadence.cron,
                "next_run": str(monitor.next_run_at) if monitor.next_run_at else None,
                "count": count
            }
            
            logger.info(f"Created monitor {monitor.id} for webset {webset_id}")
            return self.success_response(output)
            
        except Exception as e:
            logger.error(f"Failed to create monitor: {repr(e)}", exc_info=True)
            return self.fail_response(f"Failed to create monitor: {str(e)}")
    
    @openapi_schema({
        "type": "function",
        "function": {
            "name": "list_monitors",
            "description": "List all monitors for a webset or all monitors in this thread",
            "parameters": {
                "type": "object",
                "properties": {
                    "webset_id": {
                        "type": "string",
                        "description": "Optional: Filter by webset ID, or omit to list all from thread"
                    }
                }
            }
        }
    })
    async def list_monitors(
        self,
        webset_id: Optional[str] = None
    ) -> ToolResult:
        """List all monitors"""
        if not self.exa_client:
            return self.fail_response("Websets is not available. EXA_API_KEY is not configured.")
        
        try:
            if webset_id:
                # Get monitors for specific webset
                webset = await asyncio.to_thread(
                    self.exa_client.websets.get,
                    webset_id
                )
                
                monitors = [
                    {
                        "id": m.id,
                        "status": self._status_to_str(m.status),
                        "webset_id": webset_id,
                        "cadence": {
                            "cron": m.cadence.cron,
                            "timezone": m.cadence.timezone
                        },
                        "next_run": str(m.next_run_at) if m.next_run_at else None,
                        "last_run": {
                            "status": self._status_to_str(getattr(m.lastRun, 'status', None)) if hasattr(m, 'lastRun') and m.lastRun else None,
                            "completed_at": str(getattr(m.lastRun, 'completed_at', None) or getattr(m.lastRun, 'completedAt', None)) if hasattr(m, 'lastRun') and m.lastRun and (hasattr(m.lastRun, 'completed_at') or hasattr(m.lastRun, 'completedAt')) else None
                        } if hasattr(m, 'lastRun') and m.lastRun else None
                    }
                    for m in webset.monitors
                ] if webset.monitors else []
            else:
                # List all monitors from thread state
                state = await self._load_websets_state()
                monitors = list(state.get("monitors", {}).values())
            
            output = {
                "monitors": monitors,
                "total": len(monitors)
            }
            
            return self.success_response(output)
            
        except Exception as e:
            logger.error(f"Failed to list monitors: {repr(e)}", exc_info=True)
            return self.fail_response(f"Failed to list monitors: {str(e)}")
    
    @openapi_schema({
        "type": "function",
        "function": {
            "name": "update_monitor",
            "description": "Update monitor configuration (frequency/schedule)",
            "parameters": {
                "type": "object",
                "properties": {
                    "webset_id": {
                        "type": "string",
                        "description": "Webset ID or external_id"
                    },
                    "monitor_id": {
                        "type": "string",
                        "description": "Monitor ID"
                    },
                    "frequency": {
                        "type": "string",
                        "description": "New frequency: 'daily', 'weekly', 'hourly', or custom cron"
                    }
                },
                "required": ["webset_id", "monitor_id", "frequency"]
            }
        }
    })
    async def update_monitor(
        self,
        webset_id: str,
        monitor_id: str,
        frequency: str
    ) -> ToolResult:
        """Update monitor configuration"""
        if not self.exa_client:
            return self.fail_response("Websets is not available. EXA_API_KEY is not configured.")
        
        try:
            # Convert frequency to cron
            cron_map = {
                "daily": "0 9 * * *",
                "weekly": "0 9 * * 1",
                "hourly": "0 * * * *"
            }
            cron_expression = cron_map.get(frequency.lower(), frequency)
            
            update_params = {
                "cadence": {
                    "cron": cron_expression,
                    "timezone": "UTC"
                }
            }
            
            monitor = await asyncio.to_thread(
                self.exa_client.websets.monitors.update,
                webset_id=webset_id,
                monitor_id=monitor_id,
                params=update_params
            )
            
            # Update thread state
            state = await self._load_websets_state()
            if monitor_id in state.get("monitors", {}):
                state["monitors"][monitor_id]["cron"] = cron_expression
                state["monitors"][monitor_id]["frequency"] = frequency
                state["monitors"][monitor_id]["next_run"] = str(monitor.next_run_at) if monitor.next_run_at else None
            await self._save_websets_state(state)
            
            output = {
                "monitor_id": monitor_id,
                "webset_id": webset_id,
                "frequency": frequency,
                "cron": cron_expression,
                "next_run": str(monitor.next_run_at) if monitor.next_run_at else None
            }
            
            return self.success_response(output)
            
        except Exception as e:
            logger.error(f"Failed to update monitor: {repr(e)}", exc_info=True)
            return self.fail_response(f"Failed to update monitor: {str(e)}")
    
    @openapi_schema({
        "type": "function",
        "function": {
            "name": "delete_monitor",
            "description": "Delete a monitor and stop tracking",
            "parameters": {
                "type": "object",
                "properties": {
                    "webset_id": {
                        "type": "string",
                        "description": "Webset ID or external_id"
                    },
                    "monitor_id": {
                        "type": "string",
                        "description": "Monitor ID"
                    }
                },
                "required": ["webset_id", "monitor_id"]
            }
        }
    })
    async def delete_monitor(
        self,
        webset_id: str,
        monitor_id: str
    ) -> ToolResult:
        """Delete monitor"""
        if not self.exa_client:
            return self.fail_response("Websets is not available. EXA_API_KEY is not configured.")
        
        try:
            await asyncio.to_thread(
                self.exa_client.websets.monitors.delete,
                webset_id=webset_id,
                monitor_id=monitor_id
            )
            
            # Remove from thread state
            state = await self._load_websets_state()
            if monitor_id in state.get("monitors", {}):
                del state["monitors"][monitor_id]
            await self._save_websets_state(state)
            
            output = {
                "monitor_id": monitor_id,
                "webset_id": webset_id,
                "deleted": True
            }
            
            return self.success_response(output)
            
        except Exception as e:
            logger.error(f"Failed to delete monitor: {repr(e)}", exc_info=True)
            return self.fail_response(f"Failed to delete monitor: {str(e)}")
