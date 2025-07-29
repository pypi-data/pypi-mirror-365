"""Agent executor for handling LLM conversations with tool support.

This module provides the core agent execution logic that orchestrates
LLM conversations with MCP tool calling support.
"""

import json
import logging
import uuid
from collections import OrderedDict
from pathlib import Path
from typing import Any

from ..config import DEFAULT_MAX_TOKENS, DEFAULT_MODEL, DEFAULT_TEMPERATURE
from .llm.base import LLMClient
from .llm.factory import LLMClientFactory
from .mcp_tool_manager import MCPToolManager, ToolConverter

logger = logging.getLogger(__name__)


class LRUConversationCache:
    """LRU cache for storing conversations with automatic eviction."""
    
    def __init__(self, max_size: int = 100):
        self.max_size = max_size
        self._cache: OrderedDict[str, list[dict[str, Any]]] = OrderedDict()
    
    def get(self, conversation_id: str) -> list[dict[str, Any]] | None:
        """Get conversation messages, moving to end if found."""
        if conversation_id in self._cache:
            # Move to end (most recently used)
            self._cache.move_to_end(conversation_id)
            return self._cache[conversation_id]
        return None
    
    def put(self, conversation_id: str, messages: list[dict[str, Any]]) -> None:
        """Store conversation messages, evicting oldest if needed."""
        if conversation_id in self._cache:
            # Update existing and move to end
            self._cache[conversation_id] = messages
            self._cache.move_to_end(conversation_id)
        else:
            # Add new conversation
            self._cache[conversation_id] = messages
            # Evict oldest if over capacity
            if len(self._cache) > self.max_size:
                self._cache.popitem(last=False)  # Remove oldest (FIFO)
    
    def remove(self, conversation_id: str) -> list[dict[str, Any]] | None:
        """Remove and return conversation if it exists."""
        return self._cache.pop(conversation_id, None)
    
    def size(self) -> int:
        """Return current cache size."""
        return len(self._cache)


# Global LRU cache for conversations
_conversations_cache = LRUConversationCache()


def _truncate_content(content: str, max_length: int = 150) -> str:
    """Truncate content for logging while preserving readability."""
    if len(content) <= max_length:
        return content
    return content[:max_length] + "..."


class AgentExecutor:
    """Executes agent requests with tool calling support."""

    def __init__(self, llm_client: LLMClient | None = None, mcp_manager: MCPToolManager | None = None, agent_tool_name: str | None = None):
        self.llm_client = llm_client or LLMClientFactory.create_default_client()
        self.agent_tool_name = agent_tool_name or "agent"
        self.mcp_manager = mcp_manager or MCPToolManager(agent_tool_name=self.agent_tool_name)

    async def execute(
        self,
        prompt: str,
        system_prompt_template: str,
        conversation_id: str | None = None,
        model: str = DEFAULT_MODEL,
        max_tokens: int = DEFAULT_MAX_TOKENS,
        temperature: float = DEFAULT_TEMPERATURE,
    ) -> tuple[str, str]:
        """Execute an agent request.

        Args:
            prompt: User prompt
            system_prompt_template: System prompt template (can contain {prompt} placeholder)
            conversation_id: Unique conversation identifier (auto-generated if None)
            model: Model to use for generation
            max_tokens: Maximum tokens to generate
            temperature: Temperature for sampling

        Returns:
            Tuple of (final response from the agent, conversation_id used)
        """
        # Auto-generate conversation ID if not provided
        if conversation_id is None:
            conversation_id = str(uuid.uuid4())
            logger.info(f"🆔 [{self.agent_tool_name}] Generated conversation ID: {conversation_id}")
        
        logger.info(f"🚀 [{self.agent_tool_name}] {model} | User: {_truncate_content(prompt)}")
        
        messages = _conversations_cache.get(conversation_id)

        if not messages:
            # New conversation
            formatted_prompt = system_prompt_template.format(prompt=prompt)
            messages = [{"role": "user", "content": formatted_prompt}]
            _conversations_cache.put(conversation_id, messages)
        else:
            # Existing conversation
            messages.append({"role": "user", "content": prompt})
            # Update cache with modified messages
            _conversations_cache.put(conversation_id, messages)

        # Get available tools
        mcp_tools = await self.mcp_manager.list_tools()
        openai_tools = ToolConverter.mcp_to_openai(mcp_tools) if mcp_tools else None

        turn_count = 0
        while True:
            turn_count += 1

            response_data = await self.llm_client.chat_completion(
                messages=messages,
                model=model,
                max_tokens=max_tokens,
                temperature=temperature,
                tools=openai_tools
            )

            if not response_data.get("choices"):
                logger.error(f"❌ [{self.agent_tool_name}] No response from LLM")
                return "No response content found"

            message = response_data["choices"][0]["message"]
            messages.append(message)
            
            # Log response details
            content = message.get("content", "")
            tool_calls = message.get("tool_calls", [])
            
            if tool_calls:
                tool_names = [tc.get("function", {}).get("name", "unknown") for tc in tool_calls]
                for tool_name in tool_names:
                    logger.info(f"🔧 [{self.agent_tool_name}] Calling tool: {tool_name}")
                if content:
                    logger.info(f"🤖 [{self.agent_tool_name}] {model} | Response: {_truncate_content(content)}")
            else:
                logger.info(f"🤖 [{self.agent_tool_name}] {model} | Response: {_truncate_content(content)}")

            # Handle tool calls
            if tool_calls and openai_tools:
                if await self._process_tool_calls(tool_calls, messages):
                    # Update cache with messages including tool results
                    _conversations_cache.put(conversation_id, messages)
                    continue  # Continue conversation loop

            # No tool calls or all processed, return final content
            final_content = message.get("content", "No content returned")
            
            # Update cache with final messages
            _conversations_cache.put(conversation_id, messages)

            return final_content, conversation_id

    async def _process_tool_calls(
        self,
        tool_calls: list[dict[str, Any]],
        messages: list[dict[str, Any]]
    ) -> bool:
        """Process tool calls and add results to messages.

        Args:
            tool_calls: List of tool calls from the LLM
            messages: Conversation messages list to append results to

        Returns:
            True if any tool calls were processed, False otherwise
        """
        has_tool_calls = False

        for tool_call in tool_calls:
            if tool_call["type"] != "function":
                continue

            has_tool_calls = True
            function_call = tool_call["function"]
            tool_name = function_call["name"]

            try:
                tool_args = json.loads(function_call["arguments"])
            except json.JSONDecodeError as e:
                logger.error(f"❌ [{self.agent_tool_name}] Invalid JSON in tool arguments for {tool_name}: {e}")
                tool_args = {}

            try:
                result = await self.mcp_manager.call_tool(tool_name, tool_args)
                content = result
            except Exception as e:
                content = f"Error calling MCP tool {tool_name}: {e}"
                logger.error(f"❌ [{self.agent_tool_name}] Tool {tool_name} failed: {e}")

            tool_result = {
                "role": "tool",
                "tool_call_id": tool_call["id"],
                "name": tool_name,
                "content": content,
            }
            messages.append(tool_result)

        return has_tool_calls

    async def cleanup(self) -> None:
        """Clean up resources."""
        if self.mcp_manager:
            await self.mcp_manager.cleanup()


async def query_llm(
    prompt: str,
    system_prompt_file: Path | None = None,
    mcp_config_file: Path | None = None,
    conversation_id: str | None = None,
    model: str = DEFAULT_MODEL,
    max_tokens: int = DEFAULT_MAX_TOKENS,
    temperature: float = DEFAULT_TEMPERATURE,
    agent_tool_name: str | None = None
) -> str:
    """Query an LLM with optional MCP tools and system prompt.

    This is the main entry point for LLM queries, providing a simple interface
    that handles all the complexity of setting up the executor and MCP tools.

    Args:
        prompt: User prompt to send to the LLM
        system_prompt_file: Optional path to system prompt template file
        mcp_config_file: Optional path to MCP configuration file
        conversation_id: Optional conversation ID for multi-turn conversations
        model: Model to use for generation
        max_tokens: Maximum tokens to generate
        temperature: Temperature for sampling
        agent_tool_name: Name of the agent tool for logging purposes

    Returns:
        Response from the LLM
    """
    # Generate conversation ID if not provided
    if conversation_id is None:
        conversation_id = str(uuid.uuid4())

    # Load system prompt template
    system_prompt_template = "{prompt}"  # Default template
    if system_prompt_file and system_prompt_file.exists():
        system_prompt_template = system_prompt_file.read_text(encoding="utf-8")

    # Set up MCP tool manager
    mcp_manager = MCPToolManager(agent_tool_name=agent_tool_name)
    if mcp_config_file and mcp_config_file.exists():
        await mcp_manager.load_from_file(mcp_config_file)

    # Create executor and run
    executor = AgentExecutor(mcp_manager=mcp_manager, agent_tool_name=agent_tool_name)
    try:
        response, _ = await executor.execute(
            prompt=prompt,
            system_prompt_template=system_prompt_template,
            conversation_id=conversation_id,
            model=model,
            max_tokens=max_tokens,
            temperature=temperature,
        )
        return response
    finally:
        await executor.cleanup()
