from typing_extensions import TypedDict
from typing import Annotated
from langgraph.graph.message import add_messages
from langgraph.graph import StateGraph, START
from langchain.chat_models import init_chat_model
from langchain_core.tools import tool
import requests
from langgraph.prebuilt import ToolNode, tools_condition
from dotenv import load_dotenv

load_dotenv()

# @tool() - This makes a tool for langchain - Give tool description in """ """
todos = []


@tool()
def add_todo(task: str):
    """Adds the input task to DB"""
    todos.append(task)
    return True


@tool()
def get_all_todos():
    """Returns all the todos present in DB"""
    return todos


@tool()
def get_weather(city: str):
    """This tool returns the weather data about the given city"""

    url = f"https://wttr.in/{city.lower()}?format=%C+%t"
    response = requests.get(url)

    if response.status_code == 200:
        return f"The weather in {city} is {response.text}"

    return "Something went wrong"


@tool()
def add_two_numbers(a: int, b: int):
    """This tool adds two numbers"""
    return a + b


# Define tools array containing all our tools
tools = [get_weather, add_two_numbers, add_todo, get_all_todos]


class State(TypedDict):
    messages: Annotated[list, add_messages]


llm = init_chat_model(model_provider="openai", model="gpt-4.1")


# Pass tools to llm
llm_with_tools = llm.bind_tools(tools)


# ---------------------------------Nodes-----------------------------
# Node 1
def chatbot(state: State):
    message = llm_with_tools.invoke(state["messages"])
    return {"messages": [message]}


# Node 2
tool_node = ToolNode(tools=tools)


graph_builder = StateGraph(State)

graph_builder.add_node("chatbot", chatbot)
graph_builder.add_node("tools", tool_node)


graph_builder.add_edge(START, "chatbot")

# If chatbot's last message is a tool call, tools_condition will directly take it to tool node
graph_builder.add_conditional_edges("chatbot", tools_condition)

graph_builder.add_edge("tools", "chatbot")


# graph_builder.add_edge("chatbot", END) ->  There is no END CALL required

graph = graph_builder.compile()


def main():
    while True:
        user_query = input("> ")

        _state = State(
            messages=[{"role": "user", "content": user_query}]
        )

        for event in graph.stream(_state, stream_mode="values"):
            # Shows only last message
            if "messages" in event:
                event["messages"][-1].pretty_print()


main()


# 2 Nodes - Chatbot and Tools
# Start from chatbot -> tool_condition -> Checks if msg require tool call or not
# -> If not -> Ai gives generic response -> END
# -> If msg require tool call -> REDIRECTS TO TOOL NODE (WHERE TOOL IS EXECUTED/CALLED) -> Return response to CHATBOT -> Returns response to User
