import os

import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=api_key)

class ConversationAgent:
    def __init__(self):
        self.model = genai.GenerativeModel('gemini-flash-latest')
        self.conversation_history = []

    def chat(self, user_message):
        self.conversation_history.append({"role": "user", "content": user_message})
        full_context = self._build_context()
                # Get response from Gemini
        print("🤔 Agent is thinking...")
        response = self.model.generate_content(full_context)
        agent_response = response.text

        # Add agent response to history
        self.conversation_history.append({
            "role": "agent",
            "content": agent_response
        })

        print(f"🤖 Agent: {agent_response}")

        return agent_response

    def _build_context(self):
        """Build conversation context from history"""
        context = ""
        for message in self.conversation_history:
            if message["role"] == "user":
                context += f"User: {message['content']}\n"
            else:
                context += f"Agent: {message['content']}\n"
        return context

    def show_history(self):
        """Display the entire conversation history"""
        print("\n📜 Conversation History:")
        print("=" * 50)
        for i, message in enumerate(self.conversation_history, 1):
            role = "👤 You" if message["role"] == "user" else "🤖 Agent"
            print(f"{i}. {role}: {message['content'][:100]}...")
        print("=" * 50)

if __name__ == "__main__":
    agent = ConversationAgent()

    # Have a conversation
    agent.chat("My name is Alex")
    agent.chat("What's my name?")  # Agent should remember!
    agent.chat("I'm learning about AI agents")
    agent.chat("What am I learning about?")  # Should remember this too!

    # Show full history
    agent.show_history()
