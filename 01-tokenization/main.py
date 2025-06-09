import tiktoken

enc = tiktoken.encoding_for_model("gpt-4o")

text = "Hello first class of genai"
token = enc.encode(text)

print("Tokens :" , token)

tokens = [13225, 1577, 744, 328, 3645, 1361]
dec = enc.decode(tokens)

print("Decoded text : ", dec)