import os

import google.generativeai as genai
from dotenv import load_dotenv

from .database import Base, engine
from .tools import search_knowledge_base

load_dotenv()

# Ensure tables are created
Base.metadata.create_all(engine)

# Configure Gemini
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Initialize Agent
model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    tools=[search_knowledge_base],
    system_instruction="You are a research assistant. Use the search_knowledge_base tool to verify facts before answering."
)

def run_agent():
    chat = model.start_chat(enable_automatic_function_calling=True)
    print("Agent Online. Type 'exit' to quit.")

    while True:
        user_input = input("You: ")
        if user_input.lower() == 'exit':
            break

        response = chat.send_message(user_input)
        print(f"Gemini: {response.text}")

if __name__ == "__main__":
    run_agent()
