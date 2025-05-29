import os
import json
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables from the .env file
load_dotenv()

client = OpenAI(
    api_key=os.getenv("GEMINI_API_KEY"),
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

# CHAIN OF THOUGHTS PROMPTING
SYSTEM_PROMPT = """
    You are an helpful AI assistant who is specialized in resolving user query.
    For the given user input, analyse the input and break down the problem step by step.

    The steps are you get a user input, you analyse, you think, you think again, and think for several times and then return the output with an explanation. 

    Follow the steps in sequence that is "analyse", "think", "output", "validate" and finally "result".

    Rules:
    1. Follow the strict JSON output as per schema.
    2. Always perform one step at a time and wait for the next input.
    3. Carefully analyse the user query,

    Output Format:
    {{ "step": "string", "content": "string" }}

    Example:
    Input: What is 2 + 2
    Output: {{ "step": "analyse", "content": "Alight! The user is interest in maths query and he is asking a basic arthematic operation" }}
    Output: {{ "step": "think", "content": "To perform this addition, I must go from left to right and add all the operands." }}
    Output: {{ "step": "output", "content": "4" }}
    Output: {{ "step": "validate", "content": "Seems like 4 is correct ans for 2 + 2" }}
    Output: {{ "step": "result", "content": "2 + 2 = 4 and this is calculated by adding all numbers" }}

    Example:
    Input: What is 2 + 2 * 5 / 3
    Output: {{ "step": "analyse", "content": "Alight! The user is interest in maths query and he is asking a basic arthematic operations" }}
    Output: {{ "step": "think", "content": "To perform this addition, I must use BODMAS rule" }}
    Output: {{ "step": "validate", "content": "Correct, using BODMAS is the right approach here" }}
    Output: {{ "step": "think", "content": "First I need to solve division that is 5 / 3 which gives 1.66666666667" }}
    Output: {{ "step": "validate", "content": "Correct, using BODMAS the division must be performed" }}
    Output: {{ "step": "think", "content": "Now as I have already solved 5 / 3 now the equation looks lik 2 + 2 * 1.6666666666667" }}
    Output: {{ "step": "validate", "content": "Yes, The new equation is absolutely correct" }}
    Output: {{ "step": "validate", "think": "The equation now is 2 + 3.33333333333" }}
    and so on.....

"""

# response = client.chat.completions.create(
#     model="gemini-2.0-flash",
#     response_format={"type" : "json_object"},
#     messages=[
#         {"role": "assistant", "content": SYSTEM_PROMPT},
#         {"role": "user", "content":"What is 5 /2 * 3 to the power 4" },
#         {"role": "assistant", "content":json.dumps({"step": "analyse","content": "The user wants me to evaluate a mathematical expression involving division, multiplication, and exponentiation. I need to remember the order of operations (PEMDAS/BODMAS) to solve it correctly."}) },
#         {"role": "assistant", "content":json.dumps({"step": "think", "content": "Okay, according to the order of operations, I should handle the exponent first, then division and multiplication from left to right."}) },

#     ]
# )

# print("AI responded with : ", response.choices[0].message.content)

messages = [
    {"role" : "system", "content" : SYSTEM_PROMPT}
]

query = input("> ")
messages.append({"role" : "user", "content": query})

while True:
    response = client.chat.completions.create(
        model="gemini-2.0-flash",
        response_format={"type": "json_object"},
        messages=messages
    )

    messages.append({ "role": "assistant", "content": response.choices[0].message.content })
    parsed_response = json.loads(response.choices[0].message.content)

    # if parsed_response.get("step") == "think":
    #     # Make a Claude API Call and append the result as validate
    #     messages.append({ "role": "assistant", "content": "<>" })
    #     continue

    if parsed_response.get("step") != "result":
        print("          🧠:", parsed_response.get("content"))
        continue

    print("🤖:", parsed_response.get("content"))
    break

# Make COT model + article 