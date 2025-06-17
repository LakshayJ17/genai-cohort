#  flake8: noqa

from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from openai import OpenAI
from dotenv import load_dotenv
from pydantic import BaseModel
from typing import Literal

load_dotenv()

client = OpenAI()


class State(TypedDict):
    match_context: str
    is_critical_over: bool | None
    selected_bowler: str | None


class ClassifyCrucialOver(BaseModel):
    is_critical_over: bool


def analyze_match(state: State):
    match_context = state["match_context"]

    SYSTEM_PROMPT = """
    You are a Cricket Strategist. You will given a match situation and Your job is to decide whether the current over is Crucial Over or Not from perspective of Bowling Team.

    Return the response in specified JSON BOOLEAN only
    """

    response = client.beta.chat.completions.parse(
        model="gpt-4.1",
        response_format=ClassifyCrucialOver,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content":  match_context}
        ]
    )

    is_critical_over = response.choices[0].message.parsed.is_critical_over

    state["is_critical_over"] = is_critical_over

    return state


def route_query(state: State) -> Literal["critical_over", "normal_over"]:
    is_critical = state["is_critical_over"]

    if is_critical:
        return "critical_over"
    return "normal_over"


def critical_over(state: State):
    state["selected_bowler"] = "Bumrah"
    return state


def normal_over(state: State):
    state["selected_bowler"] = "Kuldeep"
    return state


graph_builder = StateGraph(State)

graph_builder.add_node("analyze_match", analyze_match)
graph_builder.add_node("critical_over", critical_over)
graph_builder.add_node("normal_over", normal_over)


graph_builder.add_edge(START, "analyze_match")
graph_builder.add_conditional_edges("analyze_match", route_query)
graph_builder.add_edge("critical_over", END)
graph_builder.add_edge("normal_over", END)

graph = graph_builder.compile()


def main():
    context = input("Enter the match situation (e.g 12 runs in 6 balls) : ")

    _state: State = {
        "match_context": context,
        "is_critical_over": None,
        "selected_bowler": None
    }

    result = graph.invoke(_state)
    print("Response : ", result)
    print("✅ Final Decision: ", result["selected_bowler"])


main()
