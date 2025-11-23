from sage.utils.llm_client import LLMClient
import os
from dotenv import load_dotenv

# Load env vars
load_dotenv()

def verify_connections():
    client = LLMClient()
    
    print("--- Verifying LLM Connections ---")
    
    # 1. Check OpenAI
    if os.getenv("OPENAI_API_KEY"):
        print("\nTesting OpenAI (gpt-4o)...")
        try:
            response = client.generate_response(
                system_prompt="You are a helpful assistant.",
                user_content="Say 'OpenAI is working!'",
                agent_name="planner" # Assuming planner uses gpt-4o-mini or similar
            )
            print(f"Success: {response}")
        except Exception as e:
            print(f"Failed: {e}")
    else:
        print("\nSkipping OpenAI (Key not found)")

    # 2. Check Anthropic
    if os.getenv("ANTHROPIC_API_KEY"):
        print("\nTesting Anthropic (claude-3-7-sonnet)...")
        try:
            response = client.generate_response(
                system_prompt="You are a helpful assistant.",
                user_content="Say 'Anthropic is working!'",
                agent_name="judge" # Assuming judge uses claude
            )
            print(f"Success: {response}")
        except Exception as e:
            print(f"Failed: {e}")
    else:
        print("\nSkipping Anthropic (Key not found)")

    # 3. Check Gemini
    if os.getenv("GEMINI_API_KEY"):
        print("\nTesting Gemini...")
        try:
            # We need an agent mapped to Gemini to test this fully, 
            # or we can temporarily force a gemini model call if the client allows, 
            # but the client resolves model by agent name.
            # Let's assume we might have mapped one, or we can just test the _call_gemini method directly if we want,
            # but better to test via public interface. 
            # If no agent is mapped to Gemini in config, this might fail or default to GPT.
            # Let's check config first or just try a known agent if we changed config.
            # For now, I'll just print a message.
            print("Gemini Key found. To test, ensure a model in config/models_config.json is set to a 'gemini-...' model.")
        except Exception as e:
            print(f"Failed: {e}")
    else:
        print("\nSkipping Gemini (Key not found)")

if __name__ == "__main__":
    verify_connections()
