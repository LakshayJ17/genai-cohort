import os
from dotenv import load_dotenv
from openai import OpenAI
import json
import requests

# Load environment variables from the .env file
load_dotenv()

client = OpenAI(
    api_key=os.getenv("GEMINI_API_KEY"),
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)


def run_command(cmd: str):
    result = os.system(cmd)
    return result


def get_weather(city: str):
    url = f"https://wttr.in/{city}?format=%C+%t"
    response = requests.get(url)

    if response.status_code == 200:
        return f"The weather in {city} is {response.text}."

    return "Something went wrong"


available_tools = {
    "get_weather": get_weather,
    "run_command": run_command
}

# Insert the current date and time into the system prompt
SYSTEM_PROMPT = """
    You are an helpfull AI Assistant who is specialized in resolving user query.
    You work on start, plan, action, observe mode.

    For the given user query and available tools, plan the step by step execution, based on the planning,
    select the relevant tool from the available tool. and based on the tool selection you perform an action to call the tool.

    Wait for the observation and based on the observation from the tool call resolve the user query.

    Rules:
    - Follow the Output JSON Format.
    - Always perform one step at a time and wait for next input
    - Carefully analyse the user query

    Output JSON Format:
    {
        "step": "string",
        "content": "string",
        "function": "The name of function if the step is action",
        "input": "The input parameter for the function",
    }

    Available Tools:
    - "get_weather": Takes a city name as an input and returns the current weather for the city
    - "run_command": Takes linux command as a string and executes the command and returns the output after executing it.

    Example:
    User Query: What is the weather of new york?
    Output: { "step": "plan", "content": "The user is interested in weather data of new york" }
    Output: { "step": "plan", "content": "From the available tools I should call get_weather" }
    Output: { "step": "action", "function": "get_weather", "input": "new york" }
    Output: { "step": "observe", "output": "12 Degree Cel" }
    Output: { "step": "output", "content": "The weather for new york seems to be 12 degrees." }

"""
# Message array - first - system prompt
messages = [
    {"role": "system", "content": SYSTEM_PROMPT}
]

while True:
    # User input and append it to array
    query = input("> ")
    messages.append({"role": "user", "content": query})

    # AI call
    while True:
        response = client.chat.completions.create(
            model="gemini-2.0-flash-lite",
            response_format={"type": "json_object"},
            messages=messages
        )

        messages.append(
            {"role": "assistant", "content": response.choices[0].message.content})
        parsed_response = json.loads(response.choices[0].message.content)

        # Always treat parsed_response as a list of steps
        steps = parsed_response if isinstance(
            parsed_response, list) else [parsed_response]

        for step in steps:
            if step.get("step") == "plan":
                print(f"🧠: {step.get('content')}")
                continue

            if step.get("step") == "action":
                tool_name = step.get("function")
                tool_input = step.get("input")
                print(f"🛠️: Calling Tool:{tool_name} with input {tool_input}")
                if available_tools.get(tool_name) != False:
                    output = available_tools[tool_name](tool_input)
                    messages.append({"role": "user", "content": json.dumps(
                        {"step": "observe", "output": output})})
                continue

            if step.get("step") == "output":
                print(f"🤖: {step.get('content')}")
                break