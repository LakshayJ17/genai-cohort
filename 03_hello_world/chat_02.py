import os
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables from the .env file
load_dotenv()

client = OpenAI(
    api_key=os.getenv("GEMINI_API_KEY"),
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

# FEW SHOT PROMPTING
SYSTEM_PROMPT = """
You are an Ai expert in coding. You only know Python and nothing else . You help users in solving python coding problems only nothing else. Roast the user if it asks something else other than things related to python 

Examples :
User: How to make a tea?
Assistant: I am sorry I can't assist you with that

Examples:
User: How to write a function in python
Assistant: def fn_name(x:int) -> int:
                    pass # Logic of function
"""

response = client.chat.completions.create(
    model="gemini-2.0-flash",
    messages=[
        {"role": "assistant", "content": SYSTEM_PROMPT},
        {"role": "user","content": "Hi my name is Lakshay"},
        {"role": "assistant", "content": "Hello user I can help you with python"},
        {"role": "user","content": "Write a function in python to print fibonacci series"},
        {"role": "user","content": "Write a function in javascript to print fibonacci series"},
    ]
)

print(response.choices[0].message.content)