"""Agent for the Streamlit demo."""

import json
from pprint import pprint
from langchain_core.messages import BaseMessage, ToolMessage
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph.state import CompiledStateGraph
from langgraph.prebuilt import create_react_agent


class Agent:
    """Agent wrapper."""

    def __init__(self, config: dict, model: str = "openai:gpt-4o-mini") -> None:
        """Initialize the agent."""
        self.model = model
        self.config = config
        self.agent = None

    async def _create_agent(self) -> CompiledStateGraph:
        """Create an agent with MCP tools."""
        client = MultiServerMCPClient(
            {
                "ui-mcp-server": {
                    "command": "python",
                    "args": ["ui_mcp_server/server.py"],
                    "transport": "stdio",
                }
            }
        )
        tools = await client.get_tools()
        prompt_msg = await client.get_prompt("ui-mcp-server", "ui_component_prompt")
        prompt = prompt_msg[-1].content
        checkpointer = InMemorySaver()

        return create_react_agent(
            self.model,
            tools,
            prompt=prompt,
            checkpointer=checkpointer,
        )

    async def initialize(self) -> None:
        """Initialize the agent asynchronously."""
        if self.agent is None:
            self.agent = await self._create_agent()

    def get_past_messages(self) -> list[BaseMessage]:
        """Get past messages from an existing agent."""
        if self.agent is None:
            return []
        past_state = list(self.agent.get_state_history(self.config))
        if len(past_state) > 0:
            return past_state[0].values["messages"]
        return []

    def update_message(self, message: BaseMessage) -> None:
        """Update a message.

        Old message will be replaced according to the message id.
        If the message id is not found, the message will be appended to the end
        of the messages.

        Args:
            message: The message to update.
        """
        if self.agent is None:
            raise ValueError("Agent is not initialized.")
        past_messages = self.get_past_messages()
        self.agent.update_state(self.config, {"messages": past_messages + [message]})

    async def get_response(
        self,
        user_input: str,
    ) -> list[BaseMessage]:
        """Get response from an existing agent and return new messages."""
        if self.agent is None:
            await self.initialize()

        past_messages = self.get_past_messages()
        response = await self.agent.ainvoke(
            {"messages": [{"role": "user", "content": user_input}]},
            self.config,
        )
        return response["messages"][len(past_messages) :]


if __name__ == "__main__":
    import asyncio
    from dotenv import load_dotenv

    load_dotenv()

    def update_tool_data(message: ToolMessage) -> ToolMessage:
        """Update the tool data."""
        data = json.loads(message.content)
        data["value"] = 10
        message.content = json.dumps(data)
        return message

    async def main():
        """Run the demo agent."""
        agent = Agent(config={"configurable": {"thread_id": "1"}})

        result = await agent.get_response(
            "Generate a number input between 0 and 100",
        )
        pprint(result)

        updated_tool_message = None
        for msg in result:
            if msg.type == "tool":
                updated_tool_message = update_tool_data(msg)
                agent.update_message(updated_tool_message)

        result = await agent.get_response(
            "What is the value of the number input?",
        )
        pprint(result)

        # result = await agent.get_response(
        #     "What did I just ask?",
        # )
        # pprint(result)

        # result = await agent.get_response(
        #     "What is the value of the number input?",
        # )
        # pprint(result)

    asyncio.run(main())
