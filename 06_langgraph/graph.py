# flake8: noqa
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI()

# Defined a state containing query and llm result
class State(TypedDict):
    query: str
    llm_result: str | None


# Node
def chat_bot(state: State):
    query = state["query"]

    llm_response = client.chat.completions.create(
        model='gpt-4.1-mini',
        messages=[
            {"role": "user", "content": query}
        ]
    )

    result = llm_response.choices[0].message.content
    state["llm_result"] = result

    return state

# Building the graph
graph_builder = StateGraph(State)

graph_builder.add_node("chat_bot", chat_bot)

graph_builder.add_edge(START, "chat_bot")
graph_builder.add_edge("chat_bot", END)

graph = graph_builder.compile()


def main():
    user = input("> ")

    # INVOKE GRAPH
    _state = {
        "query": user,
        "llm_result": None
    }

    graph_result = graph.invoke(_state)

    print("Graph result : ", graph_result)


main()


# Make a state - store user query
# Make graph - State is passed at each node ( state is ip and op for each node )
# Returns a final updated state


# User enters a query.
# Query is wrapped in a state and passed to LangGraph.
# Graph starts at START, goes to chat_bot.
# chat_bot calls GPT model, gets a response, updates state.
# Graph ends at END, returns the final state.
# Final state (with response) is printed.

