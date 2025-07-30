
from insightfinderai import Client

client = Client(
    session_name="llm-eval-test",  # Default session 
    username="mustafa",
    api_key="47b73a737d8a806ef37e1c6d7245b0671261faea",
    url="https://ai-stg.insightfinder.com"
)
    
    # Define test prompts
test_prompts = [
    "what is 1 + 2?",
    "what is 2 + 3?"
]

comparison_result = client.compare_models("anthropic-test", "gpt-model-test", test_prompts)
print(comparison_result)