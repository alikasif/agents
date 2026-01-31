from agents import Agent, Runner, RunHooks, function_tool

class CustomHooks(RunHooks):
    async def on_tool_start(self, context, agent, tool) -> None:
        """Called immediately before a local tool is invoked."""
        # Note: Accessing specific tool arguments directly in on_tool_start might require
        # accessing the context object's internal structure or checking recent SDK updates,
        # as a previous issue noted this limitation.
        print(f"--- Hook: Agent '{agent.name}' is starting tool: '{tool.name}' with args: {context.tool_arguments} ---")
        user_input = input("type yes to continue...")
        if user_input.lower() != "yes":
            raise Exception("User did not confirm execution.")

    async def on_tool_end(self, context, agent, tool, result) -> None:
        """Called immediately after a local tool is invoked."""
        print(f"--- Hook: Tool '{tool.name}' ended with result: {result} ---")
