from deepagents.sub_agent import create_task_tool
from deepagents.model import model
from deepagents.tools import write_todos, write_file, read_file, ls, edit_file
from deepagents.state import DeepAgentState

from langgraph.prebuilt import create_react_agent

base_prompt = """You have access to a number of standard tools

## `write_todos`

You have access to the `write_todos` tools to help you manage and plan tasks. Use these tools VERY frequently to ensure that you are tracking your tasks and giving the user visibility into your progress.
These tools are also EXTREMELY helpful for planning tasks, and for breaking down larger complex tasks into smaller steps. If you do not use this tool when planning, you may forget to do important tasks - and that is unacceptable.

It is critical that you mark todos as completed as soon as you are done with a task. Do not batch up multiple tasks before marking them as completed.
## `task`

- When doing web search, prefer to use the `task` tool in order to reduce context usage."""


def create_deep_agent(tools, prompt_prefix, state_schema=None, subagents=None):
    prompt = prompt_prefix + base_prompt
    built_in_tools = [write_todos, write_file, read_file, ls, edit_file]
    task_tool = create_task_tool(tools + built_in_tools, prompt_prefix, subagents)
    all_tools = built_in_tools + tools + [task_tool]
    return create_react_agent(
        model,
        prompt=prompt,
        tools=all_tools,
        state_schema=state_schema or DeepAgentState,
    )
