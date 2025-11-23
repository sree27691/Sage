import json
import os

def check_config():
    config_path = os.path.join(os.path.dirname(__file__), "config/models_config.json")
    with open(config_path, "r") as f:
        config = json.load(f)
    
    print("--- Sage Assistant Model Configuration ---")
    print(f"{'Agent':<25} | {'Model':<30}")
    print("-" * 60)
    
    llm_models = config.get("llm_models", {})
    for agent, model in llm_models.items():
        print(f"{agent:<25} | {model:<30}")
        
    print("\n--- Embedding Models ---")
    embedding_models = config.get("embedding_models", {})
    for usage, model in embedding_models.items():
        print(f"{usage:<25} | {model:<30}")

if __name__ == "__main__":
    check_config()
