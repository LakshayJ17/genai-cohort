#  flake8: noqa

from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from openai import OpenAI
from dotenv import load_dotenv
from pydantic import BaseModel
from typing import Literal

load_dotenv()

client = OpenAI()


# pydantic is like zod (in python)
class ClassifyMessageResponse(BaseModel):
    is_coding_question: bool


class CodeAccuracyResponse(BaseModel):
    accuracy_percentage: str


class State(TypedDict):
    user_query: str
    llm_result: str | None
    accuracy_percentage: str | None
    is_coding_question: bool | None


def classify_message(state: State):
    query = state["user_query"]

    SYSTEM_PROMPT = """
    You are an AI assistant. Your job is to detect if the user's query is related to coding question or not. 
    Return the response in specified JSON boolean only
    """

    response = client.beta.chat.completions.parse(
        model='gpt-4.1-nano',
        response_format=ClassifyMessageResponse,  # Model will give response in boolean
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": query}
        ]
    )

    is_coding_question = response.choices[0].message.parsed.is_coding_question
    state["is_coding_question"] = is_coding_question

    print("CLASSIFY MESSAGE")

    return state


def route_query(state: State) -> Literal["general_query", "coding_query"]:
    is_coding = state["is_coding_question"]

    if is_coding:
        return "coding_query"
    return "general_query"


def general_query(state: State):
    query = state["user_query"]

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {"role": "user", "content":  query}
        ]
    )

    state["llm_result"] = response.choices[0].message.content

    print("GENERAL QUERY")
    return state


def coding_query(state: State):
    query = state["user_query"]

    SYSTEM_PROMPT = """
    You are an Expert Coding Agent
    """

    response = client.chat.completions.create(
        model="gpt-4.1",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content":  query}
        ]
    )

    state["llm_result"] = response.choices[0].message.content

    print("CODING QUERY")
    return state


def coding_validate_query(state: State):
    query = state["user_query"]

    llm_code = state["llm_result"]

    SYSTEM_PROMPT = f"""
    You are an expert in calculating accuracy of the code according to the question.
    Return percentage of accuracy
    
    User Query : {query}
    Code: {llm_code}
    """

    response = client.beta.chat.completions.parse(
        model='gpt-4.1',
        response_format=CodeAccuracyResponse,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": query}
        ]
    )

    state["accuracy_percentage"] = response.choices[0].message.parsed.accuracy_percentage

    print("ACCURACY CHECK")
    return state


graph_builder = StateGraph(State)

# Nodes

graph_builder.add_node("classify_message", classify_message)
graph_builder.add_node("route_query", route_query)
graph_builder.add_node("general_query", general_query)
graph_builder.add_node("coding_query", coding_query)
graph_builder.add_node("coding_validate_query", coding_validate_query)

graph_builder.add_edge(START, "classify_message")
graph_builder.add_conditional_edges("classify_message", route_query)
graph_builder.add_edge("general_query", END)
graph_builder.add_edge("coding_query", "coding_validate_query")
graph_builder.add_edge("coding_validate_query", END)

graph = graph_builder.compile()


def main():
    query = input("> ")

    _state: State = {
        "user_query": query,
        "accuracy_percentage": None,
        "is_coding_question": False,
        "llm_result": None
    }

    # response = graph.invoke(_state)
    # print("Response : ", response)

    for event in graph.stream(_state):
        print("Event", event)


main()
