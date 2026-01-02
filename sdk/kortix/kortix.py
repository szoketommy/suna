from .api import agents, threads
from .agent import agentiKAgent
from .thread import agentiKThread
from .tools import AgentPressTools, MCPTools


class agentiK:
    def __init__(self, api_key: str, api_url="https://api.agentik.com/v1"):
        self._agents_client = agents.create_agents_client(api_url, api_key)
        self._threads_client = threads.create_threads_client(api_url, api_key)

        self.Agent = agentiKAgent(self._agents_client)
        self.Thread = agentiKThread(self._threads_client)
