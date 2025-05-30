import os
from dotenv import load_dotenv
from openai import OpenAI
from datetime import datetime
from random import random
# Load environment variables from the .env file
load_dotenv()

client = OpenAI(
    api_key=os.getenv("GEMINI_API_KEY"),
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

# Insert the current date and time into the system prompt
SYSTEM_PROMPT = f"""
You are a helpful AI assistant who is specialized in resolving user query.

You work on start, plan, action, observe mode.

For the given user query available tools, plan the step by step execution, based on the planning,
select the relevant tool from the available tool, and based on the tool selection you perform an action to call the tool

Wait for the observation and based on observation from tool call resolve the user query

Rules:
    1. Follow the strict JSON output as per schema.
    2. Always perform one step at a time and wait for the next input.
    3. Carefully analyse the user query,

    Available Tools :
    - "get_weather" : Takes a city name as an input 


"""

response = client.chat.completions.create(
    model="gemini-2.0-flash",
    messages=[
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": "What is date and time today?"}
    ]
)

print(response.choices[0].message.content)