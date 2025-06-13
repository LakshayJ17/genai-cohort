#  flake8: noqa

from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from openai import OpenAI
from dotenv import load_dotenv
from pydantic import BaseModel
from typing import Literal

load_dotenv()

client = OpenAI()


class ClassifyCrucialOver(BaseModel):
    is_critical_over: bool


class MatchState(TypedDict):
    match_context: str
    is_critical_over: bool | None
    selected_bowler: str | None


def analyze_match(state: MatchState):
    match_context = state["match_context"]

    SYSTEM_PROMPT = """
    You are a cricket strategist. Your job is to decide whether the final over is a pressure situation for the bowling team.
    Rules:
    - If runs needed <= 12 and balls left <= 6, mark it as a pressure situation.
    - Otherwise, it's not considered pressure.

    Return your answer strictly in JSON format:
    {
    "is_critical_over": true or false
    }
"""


    response = client.beta.chat.completions.parse(
        model="gpt-4.1-nano",
        response_format=ClassifyCrucialOver,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": match_context}
        ]
    )

    state["is_critical_over"] = response.choices[0].message.parsed.is_critical_over
    return state


def route_by_pressure(state: MatchState) -> Literal["critical_case", "normal_case"]:
    return "critical_case" if state["is_critical_over"] else "normal_case"


def critical_case(state: MatchState):
    state["selected_bowler"] = "Bumrah"
    return state


def normal_case(state: MatchState):
    state["selected_bowler"] = "Chahal"
    return state


graph_builder = StateGraph(MatchState)

graph_builder.add_node("analyze_match", analyze_match)
graph_builder.add_node("critical_case", critical_case)
graph_builder.add_node("normal_case", normal_case)

graph_builder.add_conditional_edges("analyze_match", route_by_pressure)

graph_builder.add_edge(START, "analyze_match")
graph_builder.add_edge("critical_case", END)
graph_builder.add_edge("normal_case", END)

graph = graph_builder.compile()


def main():
    context = input(
        "🏏 Enter match situation (e.g., 12 runs in 6 balls, spinner-friendly pitch): ")

    _state: MatchState = {
        "match_context": context,
        "is_critical_over": None,
        "selected_bowler": None
    }

    result = graph.invoke(_state)
    print("Response : ", result)
    print("✅ Final Decision: ", result["selected_bowler"])


main()
