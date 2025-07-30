"""
Virtual Expert Panel Orchestrator

This module implements the Virtual Expert Panel pattern, inspired by Microsoft's MAI-DxO,
but generalized for any domain. It orchestrates 5 expert agents to collaboratively solve
problems through a structured 3-action decision process.
"""

import asyncio
import logging
import uuid
from pathlib import Path
from typing import Any, Callable
from datetime import datetime

from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_ext.ui import RichConsole
from autogen_agentchat.base import TaskResult

from .panel import ExpertPanel
from .models.config import AgentConfig
from .models.virtual_panel import (
    VirtualPanelAction,
    ConversationState,
    PanelAction,
    ResearchTask,
    VirtualPanelResult,
    KnowledgeBase,
    OrchestratorDecision,
)
from .agents.web_research_agent import WebResearchAgent
from .tools.graphrag_integration import (
    GraphRAGKnowledgeManager,
    LegacyKnowledgeAdapter,
    create_graphrag_knowledge_manager,
    GRAPHRAG_AVAILABLE,
)
from .memory import Mem0Manager, create_mem0_manager


class VirtualExpertPanel:
    """
    Virtual Expert Panel orchestrator inspired by Microsoft's MAI-DxO pattern.

    This class manages a team of 5 expert agents that work together to solve complex
    problems through collaborative reasoning and a structured decision process.

    The panel can take three actions:
    1. ASK_QUESTION - Request clarification or additional information from the user
    2. REQUEST_TEST - Perform research, analysis, or other investigative actions
    3. PROVIDE_SOLUTION - Give the final answer or solution to the problem
    """

    def __init__(
        self,
        config_dir: Path | None = None,
        tools_dir: Path | None = None,
        config: AgentConfig | None = None,
        enable_memory: bool = False,
        memory_type: str = "simple",
        enable_graphrag: bool = True,
        graphrag_workspace: Path | None = None,
        persist_knowledge: bool = True,
        user_id: str | None = None,
        memory_path: Path | None = None,
        enable_mem0_cloud: bool = False,
        mem0_api_key: str | None = None,
    ):
        """
        Initialize the Virtual Expert Panel.

        Args:
            config_dir: Directory containing agent configuration files
            tools_dir: Directory containing custom tool definitions
            config: Default agent configuration for panel agents
            enable_memory: Whether to enable conversation memory
            memory_type: Type of memory system ("simple", "mem0", "advanced")
            enable_graphrag: Whether to enable GraphRAG for persistent knowledge storage
            graphrag_workspace: Custom workspace directory for GraphRAG data
            persist_knowledge: Whether to persist knowledge across sessions
            user_id: Unique identifier for memory isolation
            memory_path: Path for local Mem0 storage
            enable_mem0_cloud: Whether to use cloud-based Mem0
            mem0_api_key: API key for cloud-based Mem0
        """
        self.logger = logging.getLogger(__name__)
        self.config = config
        self.enable_memory = enable_memory
        self.memory_type = memory_type
        self.enable_graphrag = enable_graphrag
        self.persist_knowledge = persist_knowledge

        # Mem0 configuration
        self.user_id = user_id
        self.memory_path = memory_path
        self.enable_mem0_cloud = enable_mem0_cloud
        self.mem0_api_key = mem0_api_key

        # Initialize the base expert panel
        self.expert_panel = ExpertPanel(config_dir, tools_dir)

        # Create the orchestrator agent
        self.orchestrator = self._create_orchestrator_agent()

        # Initialize the web research agent for REQUEST_TEST actions
        self.web_research_agent = self._initialize_web_research_agent()

        # Initialize memory system if enabled
        self.memory = self._initialize_memory() if enable_memory else None

        # Initialize Mem0 memory manager if using mem0 memory type
        self.mem0_manager: Mem0Manager | None = None

        # Session state
        self.current_session: dict[str, Any] | None = None

        # Initialize knowledge base for general use
        self.knowledge_base = KnowledgeBase(
            domain="general", documents=[], web_research=[], facts=[], entities=[]
        )

        # Initialize GraphRAG knowledge manager if enabled
        self.graphrag_manager: GraphRAGKnowledgeManager | None = None
        self.graphrag_adapter: LegacyKnowledgeAdapter | None = None
        self.graphrag_workspace = graphrag_workspace

    def _create_orchestrator_agent(self) -> AssistantAgent:
        """Create the orchestrator agent that manages the decision process."""

        orchestrator_system_message = """
        You are the Orchestrator Agent for the Virtual Expert Panel, inspired by Microsoft's MAI-DxO pattern.

        Your role is to guide a team of 5 expert agents through a structured problem-solving process:
        - Advocate: Champions ideas with conviction and evidence
        - Critic: Rigorous quality assurance and risk analysis
        - Pragmatist: Practical implementation focus
        - Research Specialist: Fact-finding and evidence gathering
        - Innovator: Creative disruption and breakthrough solutions

        For every user query, you must orchestrate the panel to reach ONE of three decisions:

        1. ASK_QUESTION: When you need information that is specific to the user's goal and NOT industry standard knowledge
           - Ask for user-specific context, preferences, constraints, or requirements
           - Request details about their particular situation, environment, or objectives
           - Focus on information that only the user can provide about their specific case
           - Do NOT ask for general industry knowledge that can be researched

        2. REQUEST_TEST: When there is insufficient information in the knowledge base about industry standard knowledge or general topics
           - Identify gaps in general knowledge, best practices, or industry standards
           - Trigger web research to gather publicly available information
           - Research current trends, methodologies, technical specifications, or expert opinions
           - Use this for any information that can be found through internet research

        3. PROVIDE_SOLUTION: When you have sufficient information to give a final answer
           - Synthesize insights from all expert perspectives
           - Combine user-specific information with researched knowledge
           - Provide comprehensive, actionable recommendations
           - Include confidence levels and any remaining uncertainties

        DECISION PROCESS:
        1. Present the query to all 5 expert agents
        2. Evaluate current knowledge base to identify what information is missing
        3. Determine if missing information is user-specific or can be researched
        4. Make a clear decision: ASK_QUESTION, REQUEST_TEST, or PROVIDE_SOLUTION
        5. If ASK_QUESTION: wait for user response and restart process with new user info
        6. If REQUEST_TEST: perform web research, update knowledge base, then restart process
        7. If PROVIDE_SOLUTION: present final answer combining all available information

        DECISION CRITERIA:
        - ASK_QUESTION: Missing user-specific details (their goals, constraints, preferences, situation)
        - REQUEST_TEST: Missing general/industry knowledge that can be researched online
        - PROVIDE_SOLUTION: Have both user-specific context AND sufficient general knowledge

        Always be explicit about your decision and reasoning. The conversation continues until you choose PROVIDE_SOLUTION.
        """

        # Use configuration if provided, otherwise use the first expert agent's configuration
        if self.config:
            from autogen_ext.models.openai import OpenAIChatCompletionClient
            from autogen_core.models import ModelInfo

            model_client = OpenAIChatCompletionClient(
                model=self.config.model_name,
                base_url=self.config.openai_base_url,
                api_key=self.config.openai_api_key,
                model_info=ModelInfo(**self.config.model_info.model_dump()),
            )
        else:
            # Fallback to using the first expert agent's model client
            first_agent = list(self.expert_panel.agents.values())[0]
            model_client = first_agent._model_client

        orchestrator = AssistantAgent(
            name="VirtualPanelOrchestrator",
            model_client=model_client,
            system_message=orchestrator_system_message,
            description="Orchestrator agent that manages the Virtual Expert Panel decision process",
        )

        return orchestrator

    def _initialize_web_research_agent(self) -> WebResearchAgent | None:
        """Initialize the web research agent from configuration."""
        try:
            # Try to load from configuration first
            web_config_path = (
                self.expert_panel.config_dir / "web_research_specialist.yaml"
            )
            if web_config_path.exists():
                self.logger.info("Loading web research agent from configuration")
                try:
                    from .models.config import AgentConfig

                    config = AgentConfig.from_yaml(web_config_path)
                    web_agent = WebResearchAgent.from_config(
                        config=config,
                        use_tavily=True,
                        mem0_manager=None,  # Will be set later if available
                    )
                    self.logger.info(
                        "Web research agent initialized from configuration"
                    )
                    return web_agent
                except Exception as e:
                    self.logger.warning(
                        f"Failed to initialize web research agent from config: {e}"
                    )
            else:
                self.logger.info(
                    "Web research specialist config not found, using fallback initialization"
                )

            # Fallback to hardcoded initialization for backward compatibility
            try:
                web_agent = WebResearchAgent(use_tavily=True)
                self.logger.info(
                    "Web research agent initialized with hardcoded settings (Tavily)"
                )
                return web_agent
            except Exception as e:
                self.logger.warning(
                    f"Failed to initialize web research agent with Tavily: {e}"
                )
                try:
                    web_agent = WebResearchAgent(use_tavily=False)
                    self.logger.info(
                        "Web research agent initialized with hardcoded settings (simulation mode)"
                    )
                    return web_agent
                except Exception as e2:
                    self.logger.error(f"Failed to initialize web research agent: {e2}")
                    return None

        except Exception as e:
            self.logger.error(
                f"Web research agent initialization failed completely: {e}"
            )
            return None

    def _initialize_memory(self) -> Any | None:
        """Initialize the memory system based on the specified type."""
        if not self.enable_memory:
            return None

        try:
            if self.memory_type == "simple":
                # Simple in-memory storage
                return {"conversations": [], "facts": [], "context": {}}

            elif self.memory_type == "mem0":
                # Initialize the enhanced Mem0Manager
                # Note: This is async, so we'll initialize it later in virtual_solve
                self.logger.info(
                    "Mem0 memory type selected - will initialize Mem0Manager"
                )
                return {
                    "conversations": [],
                    "facts": [],
                    "context": {},
                }  # Fallback until async init

            else:
                self.logger.warning(
                    f"Unknown memory type: {self.memory_type}, using simple"
                )
                return {"conversations": [], "facts": [], "context": {}}

        except Exception as e:
            self.logger.error(f"Failed to initialize memory: {e}")
            return None

    async def _initialize_graphrag(self, domain: str = "general") -> bool:
        """
        Initialize the GraphRAG knowledge management system.

        Args:
            domain: Domain context for the knowledge base

        Returns:
            True if GraphRAG was successfully initialized
        """
        if not self.enable_graphrag:
            return False

        try:
            if not GRAPHRAG_AVAILABLE:
                self.logger.warning(
                    "GraphRAG is not available - disabling GraphRAG functionality"
                )
                return False

            self.graphrag_manager = await create_graphrag_knowledge_manager(
                domain=domain,
                workspace_dir=self.graphrag_workspace,
                persist_across_sessions=self.persist_knowledge,
            )

            if self.graphrag_manager:
                if GRAPHRAG_AVAILABLE and LegacyKnowledgeAdapter:
                    self.graphrag_adapter = LegacyKnowledgeAdapter(
                        self.graphrag_manager
                    )
                    self.logger.info(
                        f"GraphRAG knowledge manager initialized for domain: {domain}"
                    )
                    return True
                else:
                    self.logger.warning("GraphRAG adapter not available")
                    return False
            else:
                self.logger.warning(
                    "GraphRAG not available, using legacy knowledge storage"
                )
                return False

        except Exception as e:
            self.logger.error(f"Failed to initialize GraphRAG: {e}")
            return False

    async def _initialize_mem0(self) -> bool:
        """
        Initialize the Mem0 memory management system.

        Returns:
            True if Mem0 was successfully initialized
        """
        if not self.enable_memory or self.memory_type != "mem0":
            return False

        try:
            self.mem0_manager = await create_mem0_manager(
                user_id=self.user_id,
                memory_path=self.memory_path,
                enable_cloud=self.enable_mem0_cloud,
                api_key=self.mem0_api_key,
            )

            if self.mem0_manager:
                self.logger.info("Mem0 memory manager initialized successfully")
                return True
            else:
                self.logger.warning("Mem0 not available, using simple memory fallback")
                return False

        except Exception as e:
            self.logger.error(f"Failed to initialize Mem0: {e}")
            return False

    async def _get_memory_insights(self, query: str, domain: str) -> str:
        """
        Get relevant memory insights to help guide the conversation.

        Args:
            query: The current query
            domain: Domain context

        Returns:
            Memory insights as a formatted string
        """
        if not self.mem0_manager:
            return ""

        try:
            insights = []

            # Get relevant conversation patterns
            patterns = await self.mem0_manager.query_conversation_patterns(
                domain, query, limit=3
            )
            if patterns:
                insights.append("RELEVANT CONVERSATION PATTERNS:")
                for pattern in patterns:
                    insights.append(f"- {pattern['content']}")

            # Get user preferences
            preferences = await self.mem0_manager.query_user_preferences(query, limit=3)
            if preferences:
                insights.append("\nUSER PREFERENCES:")
                for pref in preferences:
                    insights.append(f"- {pref['content']}")

            # Get research strategies
            strategies = await self.mem0_manager.query_research_strategies(
                domain, query, limit=2
            )
            if strategies:
                insights.append("\nEFFECTIVE RESEARCH STRATEGIES:")
                for strategy in strategies:
                    insights.append(f"- {strategy['content']}")

            # Get domain knowledge
            knowledge = await self.mem0_manager.query_domain_knowledge(
                domain, query, limit=3
            )
            if knowledge:
                insights.append("\nRELEVANT DOMAIN KNOWLEDGE:")
                for know in knowledge:
                    insights.append(f"- {know['content']}")

            return "\n".join(insights) if insights else ""

        except Exception as e:
            self.logger.warning(f"Failed to retrieve memory insights: {e}")
            return ""

    async def _sync_knowledge_to_graphrag(self, session_id: str) -> None:
        """
        Synchronize the legacy knowledge base with GraphRAG.

        Args:
            session_id: Current session identifier
        """
        if self.graphrag_adapter and self.knowledge_base:
            try:
                await self.graphrag_adapter.migrate_knowledge_base(
                    self.knowledge_base, session_id
                )
                self.logger.info("Knowledge base synchronized with GraphRAG")
            except Exception as e:
                self.logger.error(f"Failed to sync knowledge to GraphRAG: {e}")

    async def _query_enhanced_knowledge(self, query: str) -> str:
        """
        Query both legacy knowledge base and GraphRAG for comprehensive results.

        Args:
            query: The query to search for

        Returns:
            Enhanced knowledge summary including GraphRAG insights
        """
        knowledge_summary = self.knowledge_base.summary

        # If GraphRAG is available, enhance with its knowledge
        if self.graphrag_adapter:
            try:
                graphrag_response = await self.graphrag_adapter.query_knowledge(
                    query, search_type="global"
                )

                # Check for successful response by looking for common error patterns
                error_patterns = ["failed:", "error:", "Error:", "Exception:", "not available"]
                if graphrag_response and not any(
                    error_pattern in graphrag_response for error_pattern in error_patterns
                ):
                    # Combine legacy and GraphRAG knowledge
                    enhanced_summary = f"""
Legacy Knowledge Base Summary:
{knowledge_summary}

GraphRAG Knowledge Analysis:
{graphrag_response}

Combined Knowledge Confidence: High (GraphRAG Enhanced)
                    """.strip()

                    return enhanced_summary

            except Exception as e:
                self.logger.error(f"Failed to query GraphRAG: {e}")

        # Fallback to legacy knowledge
        return knowledge_summary or "No significant knowledge accumulated yet."

    async def solve_problem(
        self,
        query: str,
        domain: str | None = None,
        max_iterations: int = 10,
        user_input_func: Callable[[str], str] | None = None,
    ) -> VirtualPanelResult:
        """
        Solve a problem using the Virtual Expert Panel process.

        Args:
            query: The problem or question to solve
            domain: Optional domain hint for context
            max_iterations: Maximum number of decision loops
            user_input_func: Function to get user input for ASK_QUESTION actions

        Returns:
            VirtualPanelResult with the complete session information
        """
        session_id = str(uuid.uuid4())
        self.logger.info(f"Starting Virtual Expert Panel session {session_id}")

        # Initialize Mem0 if enabled and not already initialized
        if self.memory_type == "mem0" and not self.mem0_manager:
            await self._initialize_mem0()

        # Update web research agent with Mem0 manager if available
        if self.mem0_manager and self.web_research_agent:
            self.web_research_agent.mem0_manager = self.mem0_manager

        # Initialize session state
        self.current_session = {
            "session_id": session_id,
            "query": query,
            "domain": domain or "general",
            "start_time": datetime.now(),
            "iteration": 0,
            "state": ConversationState.INITIALIZING,
        }

        # Initialize knowledge base
        self.knowledge_base = KnowledgeBase(
            domain=domain or "general",
            documents=[],
            web_research=[],
            facts=[],
            entities=[],
        )

        # Initialize GraphRAG if enabled
        await self._initialize_graphrag(domain or "general")

        # Track session data
        conversation_history = []
        actions_taken = []
        research_tasks = []

        # Initialize final_solution and iteration counter
        final_solution = None
        iteration = 0

        try:
            for iteration in range(max_iterations):
                self.current_session["iteration"] = iteration
                self.current_session["state"] = ConversationState.DELIBERATING

                self.logger.info(f"Virtual Panel iteration {iteration + 1}")

                # Get decision from the panel
                decision = await self._orchestrate_panel_decision(query, iteration)

                # Record the action
                panel_action = PanelAction(
                    action_type=decision.decision,
                    content=decision.rationale,
                    reasoning=f"Iteration {iteration + 1}: {decision.rationale}",
                    timestamp=datetime.now(),
                    metadata={
                        "confidence": decision.confidence,
                        "consensus": decision.panel_consensus,
                        "iteration": iteration,
                    },
                )
                actions_taken.append(panel_action)

                # Handle the decision
                if decision.decision == VirtualPanelAction.ASK_QUESTION:
                    if not user_input_func:
                        # No way to get user input, treat as insufficient info
                        final_solution = "Unable to proceed: Additional information needed but no input method available."
                        break

                    self.current_session["state"] = ConversationState.AWAITING_USER
                    user_response = await self._handle_ask_question(
                        decision, user_input_func
                    )
                    query = f"{query}\n\nAdditional Information: {user_response}"

                elif decision.decision == VirtualPanelAction.REQUEST_TEST:
                    self.current_session["state"] = ConversationState.RESEARCHING
                    research_results = await self._handle_request_test(decision)
                    research_tasks.extend(research_results)

                elif decision.decision == VirtualPanelAction.PROVIDE_SOLUTION:
                    self.current_session["state"] = ConversationState.CONCLUDING
                    final_solution = decision.rationale
                    break

            else:
                # Max iterations reached without solution
                final_solution = "Unable to reach a definitive solution within the iteration limit. Partial analysis available."

            # Create final result
            result = VirtualPanelResult(
                original_query=query,
                final_solution=final_solution,
                conversation_history=conversation_history,
                actions_taken=actions_taken,
                research_tasks=research_tasks,
                knowledge_artifacts=[
                    doc["title"] for doc in self.knowledge_base.documents
                ],
                session_state=self.current_session["state"],
                total_rounds=iteration + 1,
                participants=list(self.expert_panel.agents.keys()) + ["orchestrator"],
                start_time=self.current_session["start_time"],
                end_time=datetime.now(),
            )

            # Learn from this session if Mem0 is enabled
            if self.mem0_manager:
                try:
                    await self.mem0_manager.learn_from_session(result)
                    self.logger.info("Session learning stored in Mem0")
                except Exception as e:
                    self.logger.warning(
                        f"Failed to store session learning in Mem0: {e}"
                    )

            self.logger.info(f"Virtual Expert Panel session {session_id} completed")
            return result

        except Exception as e:
            self.logger.error(
                f"Error in Virtual Expert Panel session {session_id}: {e}"
            )
            raise

    async def _orchestrate_panel_decision(
        self, query: str, iteration: int
    ) -> OrchestratorDecision:
        """Orchestrate the panel to make a decision."""

        # Get memory insights for guidance
        memory_insights = await self._get_memory_insights(
            query, self.current_session["domain"]
        )

        # Create enhanced prompt with context
        if iteration == 0:
            discussion_prompt = f"""
            VIRTUAL EXPERT PANEL SESSION - NEW PROBLEM

            Query: {query}
            Domain: {self.current_session["domain"]}
            Current Knowledge Base: {await self._query_enhanced_knowledge(query)}

            {
                f'''
            MEMORY INSIGHTS FROM PAST SESSIONS:
            {memory_insights}
            '''
                if memory_insights
                else ""
            }

            Expert Panel, please analyze this problem and decide our next action:

            1. ASK_QUESTION - If we need USER-SPECIFIC information that cannot be researched
               (e.g., their goals, constraints, preferences, specific situation details)

            2. REQUEST_TEST - If we need GENERAL KNOWLEDGE that can be researched online
               (e.g., industry standards, best practices, current trends, methodologies)

            3. PROVIDE_SOLUTION - If we have sufficient information to answer confidently

            DECISION CRITERIA:
            - Do we need to know about the user's specific situation, goals, or constraints? → ASK_QUESTION
            - Do we need general/industry knowledge that can be found online? → REQUEST_TEST
            - Do we have both user context AND sufficient general knowledge? → PROVIDE_SOLUTION

            Current Knowledge Assessment:
            - User-specific information: {
                sum(
                    1
                    for doc in self.knowledge_base.documents
                    if doc.get("source") == "user_input"
                )
            } entries
            - General knowledge from research: {
                len(self.knowledge_base.web_research)
            } research results
            - Total facts available: {len(self.knowledge_base.facts)} facts

            Please discuss what type of information is missing and recommend which action to take.
            """
        else:
            discussion_prompt = f"""
            VIRTUAL EXPERT PANEL SESSION - CONTINUATION

            Original Query: {query}
            Iteration: {iteration + 1}
            Previous Actions: {len(self.current_session.get("actions", []))}
            Knowledge Base Status: {await self._query_enhanced_knowledge(query)}

            {
                f'''
            MEMORY INSIGHTS FROM PAST SESSIONS:
            {memory_insights}
            '''
                if memory_insights
                else ""
            }

            Based on our accumulated knowledge, what should our next action be?

            1. ASK_QUESTION - Need USER-SPECIFIC information from the user
               (their goals, constraints, preferences, specific situation)

            2. REQUEST_TEST - Need GENERAL KNOWLEDGE through web research
               (industry standards, best practices, current trends)

            3. PROVIDE_SOLUTION - Have sufficient information to provide final answer

            CURRENT KNOWLEDGE ASSESSMENT:
            - User-specific information: {
                sum(
                    1
                    for doc in self.knowledge_base.documents
                    if doc.get("source") == "user_input"
                )
            } entries
            - Web research results: {
                len(self.knowledge_base.web_research)
            } research sessions
            - Extracted facts: {len(self.knowledge_base.facts)} facts
            - Knowledge confidence: {self.knowledge_base.confidence_score:.2f}

            DECISION CRITERIA:
            - Missing user context about their specific situation? → ASK_QUESTION
            - Missing general knowledge that can be researched? → REQUEST_TEST
            - Have both user context AND general knowledge? → PROVIDE_SOLUTION

            Review what we've learned and what's still missing, then recommend our next step.
            """

        # Get all participating agents
        agents = list(self.expert_panel.agents.values()) + [self.orchestrator]

        # Run the panel discussion
        group_chat = RoundRobinGroupChat(agents, max_turns=len(agents) * 2)
        task_result: TaskResult = await RichConsole(
            group_chat.run_stream(task=discussion_prompt)
        )

        # Analyze the discussion to extract decision
        decision = await self._extract_decision_from_discussion(task_result, iteration)

        return decision

    async def _extract_decision_from_discussion(
        self, task_result: TaskResult, iteration: int
    ) -> OrchestratorDecision:
        """Extract the panel's decision from the discussion."""

        # Get the final message from the orchestrator
        messages = task_result.messages if hasattr(task_result, "messages") else []

        # Look for orchestrator's final decision
        orchestrator_messages = [
            msg
            for msg in messages
            if hasattr(msg, "source") and msg.source == "orchestrator"
        ]

        if orchestrator_messages:
            final_message = orchestrator_messages[-1]
            content = (
                final_message.content.lower()
                if hasattr(final_message, "content")
                else str(final_message).lower()
            )
        else:
            content = str(task_result).lower()

        # Analyze content to determine decision
        if "ask_question" in content or "ask question" in content:
            decision = VirtualPanelAction.ASK_QUESTION
            confidence = 0.8
        elif (
            "request_test" in content
            or "request test" in content
            or "research" in content
        ):
            decision = VirtualPanelAction.REQUEST_TEST
            confidence = 0.8
        elif (
            "provide_solution" in content
            or "provide solution" in content
            or "final answer" in content
        ):
            decision = VirtualPanelAction.PROVIDE_SOLUTION
            confidence = 0.9
        else:
            # Default based on iteration
            if iteration == 0:
                decision = VirtualPanelAction.REQUEST_TEST
            elif iteration < 3:
                decision = VirtualPanelAction.REQUEST_TEST
            else:
                decision = VirtualPanelAction.PROVIDE_SOLUTION
            confidence = 0.6

        return OrchestratorDecision(
            decision=decision,
            rationale=content[:500],  # Truncate for storage
            confidence=confidence,
            panel_consensus=True,  # Simplified - could analyze for actual consensus
        )

    async def _handle_ask_question(
        self, decision: OrchestratorDecision, user_input_func: Callable[[str], str]
    ) -> str:
        """
        Handle ASK_QUESTION action by prompting the user for specific information.

        This action is used when we need user-specific information that cannot be
        found through general research (e.g., their goals, constraints, preferences,
        specific situation details).
        """

        question = f"""
        The Virtual Expert Panel needs information specific to your situation:

        {decision.rationale}

        Please provide details about your specific context, goals, or requirements:
        """

        try:
            if asyncio.iscoroutinefunction(user_input_func):
                response = await user_input_func(question)
            else:
                response = user_input_func(question)

            # Store the user-specific information in knowledge base
            self.knowledge_base.add_document(
                title=f"User-Specific Context - Iteration {self.current_session['iteration']}",
                content=response,
                source="user_input",
                metadata={
                    "question": decision.rationale,
                    "type": "user_specific_information",
                    "iteration": self.current_session["iteration"],
                },
            )

            # Also store in GraphRAG if available
            if self.graphrag_manager:
                try:
                    await self.graphrag_manager.add_user_context(
                        response, "user_response", self.current_session["session_id"]
                    )
                    self.logger.info("User context added to GraphRAG")
                except Exception as e:
                    self.logger.error(f"Failed to add user context to GraphRAG: {e}")

            self.logger.info(
                f"Collected user-specific information: {len(response)} characters"
            )
            return response

        except Exception as e:
            self.logger.error(f"Error getting user input: {e}")
            return "No additional information provided."

    async def _handle_request_test(
        self, decision: OrchestratorDecision
    ) -> list[ResearchTask]:
        """
        Handle REQUEST_TEST action by performing web research to fill knowledge gaps.

        This action is used when there is insufficient information in the knowledge base
        about industry standard knowledge or general topics that can be researched online.
        """

        tasks = []
        task_id = f"research_{self.current_session['iteration']}_{uuid.uuid4().hex[:8]}"

        # Create research task
        research_task = ResearchTask(
            task_id=task_id,
            description=decision.rationale,
            agent_assigned="web_research_agent",
            status="in_progress",
        )

        try:
            self.logger.info(
                f"Starting web research for knowledge gap: {decision.rationale}"
            )

            # Check if web research agent is available
            if self.web_research_agent is None:
                raise RuntimeError("Web research agent is not available")

            # Conduct web research to fill knowledge gaps
            research_results = await self._conduct_web_research(decision.rationale)

            # Update research task with results
            research_task.status = "completed"
            research_task.results = research_results

            # Update knowledge base with research findings
            self._populate_knowledge_base_from_research(research_results)

            # Also store in GraphRAG if available
            if self.graphrag_manager:
                try:
                    await self.graphrag_manager.add_research_findings(
                        research_results, self.current_session["session_id"]
                    )
                    self.logger.info("Research findings added to GraphRAG")
                except Exception as e:
                    self.logger.error(
                        f"Failed to add research findings to GraphRAG: {e}"
                    )

            self.logger.info(
                f"Web research completed successfully. Added {len(research_results.get('key_findings', []))} findings to knowledge base"
            )

            tasks.append(research_task)

        except Exception as e:
            self.logger.error(f"Web research task failed: {e}")
            research_task.status = "failed"
            research_task.results = {
                "error": str(e),
                "summary": f"Web research failed: {str(e)}",
                "note": "Consider checking TAVILY_API_KEY or network connectivity",
            }
            tasks.append(research_task)

        return tasks

    async def _conduct_web_research(self, query: str) -> dict[str, Any]:
        """
        Conduct web research using the Tavily-powered web research agent.

        This method searches the internet for information to fill knowledge gaps
        about industry standards, best practices, and general knowledge.
        """
        try:
            self.logger.info(f"Conducting web research for: {query}")

            # Use the web research agent to perform comprehensive research
            research_results = await self.web_research_agent.research_topic(
                query=query,
                domain=self.current_session.get("domain", "general"),
            )

            self.logger.info(
                f"Web research completed: {len(research_results.get('key_findings', []))} findings, "
                f"confidence: {research_results.get('confidence_score', 0):.2f}"
            )

            return research_results

        except Exception as e:
            self.logger.error(f"Web research failed for query '{query}': {e}")
            raise RuntimeError(f"Web research failed: {e}")

    def _populate_knowledge_base_from_research(
        self, research_results: dict[str, Any]
    ) -> None:
        """
        Populate the knowledge base with findings from web research.

        This method processes research results and adds them to the knowledge base
        in a structured format for future reference.
        """
        try:
            # Add web research entry
            web_research_entry = {
                "query": research_results.get("original_query", ""),
                "summary": research_results.get("summary", ""),
                "confidence_score": research_results.get("confidence_score", 0.0),
                "sources": research_results.get("sources", []),
                "key_findings": research_results.get("key_findings", []),
                "timestamp": research_results.get("timestamp", datetime.now()),
                "iteration": self.current_session.get("iteration", 0),
            }

            self.knowledge_base.web_research.append(web_research_entry)

            # Extract and add individual facts
            for finding in research_results.get("key_findings", []):
                if isinstance(finding, dict):
                    fact_content = finding.get("content", str(finding))
                    fact_source = finding.get("url", "web_research")
                else:
                    fact_content = str(finding)
                    fact_source = "web_research"

                fact_entry = {
                    "fact": fact_content,
                    "source": fact_source,
                    "confidence": 0.8,  # High confidence for web research
                    "timestamp": datetime.now(),
                    "type": "web_research_finding",
                }

                self.knowledge_base.facts.append(fact_entry)

            # Update knowledge base summary
            self._update_knowledge_base_summary()

            self.logger.info(
                f"Knowledge base updated: {len(self.knowledge_base.web_research)} research entries, "
                f"{len(self.knowledge_base.facts)} facts"
            )

        except Exception as e:
            self.logger.error(f"Failed to populate knowledge base from research: {e}")

    def _update_knowledge_base_summary(self) -> None:
        """Update the knowledge base summary with current information."""
        try:
            total_entries = (
                len(self.knowledge_base.documents)
                + len(self.knowledge_base.web_research)
                + len(self.knowledge_base.facts)
            )

            user_info_count = sum(
                1
                for doc in self.knowledge_base.documents
                if doc.get("source") == "user_input"
            )

            web_research_count = len(self.knowledge_base.web_research)

            self.knowledge_base.summary = (
                f"Knowledge base contains {total_entries} total entries: "
                f"{user_info_count} user-specific inputs, "
                f"{web_research_count} web research results, "
                f"{len(self.knowledge_base.facts)} extracted facts."
            )

            # Calculate confidence based on information completeness
            if total_entries == 0:
                self.knowledge_base.confidence_score = 0.0
            elif user_info_count > 0 and web_research_count > 0:
                self.knowledge_base.confidence_score = (
                    0.9  # High confidence with both types
                )
            elif user_info_count > 0 or web_research_count > 0:
                self.knowledge_base.confidence_score = (
                    0.6  # Medium confidence with one type
                )
            else:
                self.knowledge_base.confidence_score = (
                    0.3  # Low confidence with only facts
                )

        except Exception as e:
            self.logger.error(f"Failed to update knowledge base summary: {e}")

    async def _generate_final_solution(self, query: str) -> str:
        """
        Generate the final solution based on accumulated knowledge and panel discussion.

        Args:
            query: The original query

        Returns:
            The final solution text
        """
        try:
            # Create enhanced prompt with all available knowledge
            knowledge_summary = await self._query_enhanced_knowledge(query)

            # Create a final solution using the orchestrator
            solution_prompt = f"""
            FINAL SOLUTION GENERATION

            Original Query: {query}
            Domain: {self.current_session.get("domain", "general") if self.current_session else "general"}

            Available Knowledge:
            {knowledge_summary}

            Based on all the information gathered and panel discussions, provide a comprehensive
            final solution to the original query. Your solution should:

            1. Directly address the original question or problem
            2. Incorporate insights from the knowledge base
            3. Be practical and actionable
            4. Include any important caveats or limitations
            5. Be well-structured and clear

            Please provide the final solution:
            """

            # Get all participating agents for the final solution
            agents = list(self.expert_panel.agents.values()) + [self.orchestrator]

            # Run a final discussion to generate the solution
            group_chat = RoundRobinGroupChat(agents, max_turns=len(agents))
            task_result: TaskResult = await RichConsole(
                group_chat.run_stream(task=solution_prompt)
            )

            # Extract the final solution from the discussion
            if task_result.messages:
                # Get the last message from the orchestrator or the last message overall
                orchestrator_messages = [
                    msg
                    for msg in task_result.messages
                    if hasattr(msg, "source")
                    and msg.source == "VirtualPanelOrchestrator"
                ]

                if orchestrator_messages:
                    final_message = orchestrator_messages[-1]
                else:
                    final_message = task_result.messages[-1]

                return getattr(final_message, "content", str(final_message))

            return "Unable to generate final solution - no panel response available."

        except Exception as e:
            self.logger.error(f"Failed to generate final solution: {e}")
            return f"Error generating final solution: {str(e)}"

    def _format_panel_context(
        self,
        query: str,
        domain: str,
        memory_insights: str,
        conversation_history: list[dict[str, Any]],
    ) -> str:
        """
        Format the panel context for discussions.

        Args:
            query: The current query
            domain: Domain context
            memory_insights: Memory insights from previous sessions
            conversation_history: Previous conversation history

        Returns:
            Formatted context string
        """
        context_parts = []

        # Add query and domain
        context_parts.append(f"Query: {query}")
        context_parts.append(f"Domain: {domain}")

        # Add memory insights if available
        if memory_insights:
            context_parts.append(f"\nMemory Insights:\n{memory_insights}")

        # Add conversation history if available
        if conversation_history:
            context_parts.append("\nConversation History:")
            for i, entry in enumerate(conversation_history[-5:]):  # Last 5 entries
                role = entry.get("role", "unknown")
                content = entry.get("content", "")
                context_parts.append(f"{i + 1}. {role}: {content[:100]}...")

        # Add knowledge base summary if available
        if hasattr(self, "knowledge_base") and self.knowledge_base:
            if self.knowledge_base.summary:
                context_parts.append(f"\nKnowledge Base: {self.knowledge_base.summary}")

        return "\n".join(context_parts)
