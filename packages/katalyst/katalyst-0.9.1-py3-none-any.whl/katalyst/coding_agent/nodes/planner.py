"""
Planner Node - Uses create_react_agent for intelligent planning.

This node:
1. Creates a planner agent with exploration tools
2. Uses the agent to explore the codebase and create a plan
3. Extracts subtasks from the agent's response
4. Updates state with the plan
"""

from typing import List
from langchain_core.messages import HumanMessage, AIMessage
from langgraph.prebuilt import create_react_agent

from katalyst.katalyst_core.state import KatalystState
from katalyst.katalyst_core.utils.models import PlannerOutput
from katalyst.katalyst_core.utils.logger import get_logger
from katalyst.katalyst_core.utils.checkpointer_manager import checkpointer_manager
from katalyst.katalyst_core.config import get_llm_config
from katalyst.katalyst_core.utils.langchain_models import get_langchain_chat_model
from katalyst.katalyst_core.utils.tools import (
    get_tool_functions_map,
    create_tools_with_context,
)
from katalyst.coding_agent.nodes.summarizer import get_summarization_node


# Planning-focused prompt
planner_prompt = """You are a senior software architect creating implementation plans.

CRITICAL: You are in the PLANNING phase. DO NOT execute any actions or make any changes!

Your role is to:
1. ANALYZE the current state of the codebase/filesystem
2. UNDERSTAND what needs to be built
3. CREATE a detailed plan for implementation

You are ONLY allowed to:
- Explore directory structure (ls) - to understand what exists
- Search for patterns (grep, glob) - to find relevant code
- Read files (read) - to understand existing architecture
- Find code definitions (list_code_definitions) - to understand code structure
- Ask questions (request_user_input) - when you need clarification

You MUST NOT:
- Create any files or directories
- Execute any commands
- Make any modifications
- Install any packages
- Run any builds or tests

PLANNING GUIDELINES:
- Each task should be a complete, actionable instruction
- Tasks should be roughly equal in scope
- Tasks should build on each other logically
- Include all setup, implementation, and testing tasks
- Be specific about file paths and component names

After exploring and understanding the requirements, provide your plan as a list of subtasks.

Example subtask format:
- Set up project directory structure with appropriate subdirectories
- Initialize development environment and install required dependencies
- Create core application architecture and entry points
- Implement data models and database schema
- Build API endpoints with proper routing and validation
- Develop frontend components and user interface
- Integrate frontend with backend services
- Write unit tests for critical functionality
- Add integration tests for API endpoints
- Configure deployment and build processes
"""


def planner(state: KatalystState) -> KatalystState:
    """
    Use a planning agent to explore the codebase and create an implementation plan.
    """
    logger = get_logger("coding_agent")
    logger.debug("[PLANNER] Starting planner node...")

    # Get checkpointer from manager
    checkpointer = checkpointer_manager.get_checkpointer()
    
    # Check if we have a checkpointer
    if not checkpointer:
        logger.error("[PLANNER] No checkpointer available from manager")
        state.error_message = "No checkpointer available for conversation"
        state.response = "Failed to initialize planner. Please try again."
        return state

    # Get configured model
    llm_config = get_llm_config()
    model_name = llm_config.get_model_for_component("planner")
    provider = llm_config.get_provider()
    timeout = llm_config.get_timeout()
    api_base = llm_config.get_api_base()

    logger.debug(f"[PLANNER] Using model: {model_name} (provider: {provider})")

    # Get planner model
    planner_model = get_langchain_chat_model(
        model_name=model_name,
        provider=provider,
        temperature=0,
        timeout=timeout,
        api_base=api_base,
    )

    # Get planner tools with logging context
    tool_functions = get_tool_functions_map(category="planner")
    tools = create_tools_with_context(tool_functions, "PLANNER")

    # Get summarization node for conversation compression
    summarization_node = get_summarization_node()

    # Create planner agent with structured output and summarization
    planner_agent = create_react_agent(
        model=planner_model,
        tools=tools,
        checkpointer=checkpointer,
        prompt=planner_prompt,  # Set as system prompt
        response_format=PlannerOutput,  # Use structured output
        pre_model_hook=summarization_node,  # Enable conversation summarization
    )

    # Create user request message
    user_request_message = HumanMessage(
        content=f"""User Request: {state.task}

Please explore the codebase as needed and create a detailed implementation plan.
Provide your final plan as a list of subtasks that can be executed to complete the request."""
    )

    # Initialize messages if needed
    if not state.messages:
        state.messages = []

    # Add user request message
    state.messages.append(user_request_message)

    try:
        # Use the planner agent to create a plan
        logger.info("[PLANNER] Invoking planner agent to create plan")
        result = planner_agent.invoke({"messages": state.messages})

        # Update messages
        state.messages = result.get("messages", state.messages)

        # Extract structured response
        structured_response = result.get("structured_response")

        if structured_response and isinstance(structured_response, PlannerOutput):
            subtasks = structured_response.subtasks

            if subtasks:
                # Update state with the plan
                state.task_queue = subtasks
                state.original_plan = subtasks
                state.task_idx = 0
                state.outer_cycles = 0
                state.completed_tasks = []
                state.response = None
                state.error_message = None
                state.plan_feedback = None

                # Log the plan
                plan_message = f"Generated plan:\n" + "\n".join(
                    f"{i+1}. {s}" for i, s in enumerate(subtasks)
                )
                logger.info(f"[PLANNER] {plan_message}")
            else:
                logger.error("[PLANNER] Structured response contained no subtasks")
                state.error_message = "Plan was empty"
                state.response = "Failed to create a plan. Please try again."
        else:
            # Fallback: check if there's an error message in the result
            logger.error(
                f"[PLANNER] No structured response received. Result keys: {list(result.keys())}"
            )
            state.error_message = "Failed to get structured plan from agent"
            state.response = "Failed to create a plan. Please try again."

            # Log any AI messages for debugging
            ai_messages = [msg for msg in state.messages if isinstance(msg, AIMessage)]
            if ai_messages:
                logger.debug(
                    f"[PLANNER] Last AI message: {ai_messages[-1].content[:200]}..."
                )

    except Exception as e:
        logger.error(f"[PLANNER] Failed to generate plan: {str(e)}")
        state.error_message = f"Failed to generate plan: {str(e)}"
        state.response = "Failed to generate initial plan. Please try again."

    logger.debug("[PLANNER] End of planner node.")
    return state
