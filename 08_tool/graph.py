#  flake8: noqa

from typing_extensions import TypedDict
from typing import Annotated
from langgraph.graph.message import add_messages
from langgraph.graph import StateGraph, START, END\
from langchain_core.tools import tool


@tool
def get_weather(city: str):
    

class State(TypedDict):
    messages: Annotated[list, add_messages]


def chatbot(state: State):
    pass


graph_builder = StateGraph(State)

graph_builder.add_node("chatbot", chatbot)

graph_builder.add_edge(START, "chatbot")
graph_builder.add_edge("chatbot", END)

graph = graph_builder.compile()

def main():
    user_query = input("> ")
    
    state = State(
        messages=[{"role" : "user", "content": user_query}]
    )
    
    
