import os
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

# Get the Gemini API key from environment variables
api_key = os.getenv("GEMINI_API_KEY")

# If the API key is not set, show an error and exit the script
if not api_key:
    print("Please set the GEMINI_API_KEY environment variable.")
    exit()

# Configure the Gemini API with the retrieved API key
genai.configure(api_key=api_key)

# Generate an embedding for the input text using the embedding model
result = genai.embed_content(
    model="models/embedding-001",                                  # Specify the embedding model
    content="First genai class - getting vector embeddings"        # Input text to be embedded
)

# Print the embedding vector (list of floats)
print(result['embedding'])
