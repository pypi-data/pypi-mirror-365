from insightfinderai import Client
# Initialize the client
client = Client(
    session_name="session-management-test",
    url="https://ai-stg.insightfinder.com",
    username="mustafa",
    api_key="47b73a737d8a806ef37e1c6d7245b0671261faea"
)

print("=== Session Management Demo ===\n")

# Example 1: List supported models
print("1. Listing supported models:")
print("-" * 40)
models = client.list_supported_models()
for i, model in enumerate(models, 1):
    print(f"  {i:2d}. {model}")
print(f"\nTotal models available: {len(models)}")

print("\n" + "="*60 + "\n")

# Example 2: Create a new session
print("2. Creating a new session:")
print("-" * 40)
try:
    success = client.create_session(
        model_name="my-test-session-gpt4o",
        model_type="OpenAI",
        model_version="gpt-4o",
        description="Test session for GPT-4o model",
        shared=True
    )
    if success:
        print("✅ Session created successfully!")
    else:
        print("❌ Failed to create session")
except Exception as e:
    print(f"❌ Error creating session: {e}")

print("\n" + "="*60 + "\n")

# Example 3: Try to create session with invalid model
print("3. Testing validation with invalid model:")
print("-" * 40)
try:
    success = client.create_session(
        model_name="invalid-session",
        model_type="InvalidType",
        model_version="invalid-version"
    )
except ValueError as e:
    print(f"✅ Validation working correctly: {e}")

print("\n" + "="*60 + "\n")

# Example 4: Delete the session
print("4. Deleting the test session:")
print("-" * 40)
try:
    success = client.delete_session("my-test-session-gpt4o")
    if success:
        print("✅ Session deleted successfully!")
    else:
        print("❌ Failed to delete session")
except Exception as e:
    print(f"❌ Error deleting session: {e}")

print("\n" + "="*60 + "\n")

# Example 5: Create session with different model
print("5. Creating session with Meta LLaMA model:")
print("-" * 40)
try:
    success = client.create_session(
        model_name="llama-test-session",
        model_type="Meta LLaMA",
        model_version="Llama-3.1-8B-Instruct",
        description="Test session for LLaMA model"
    )
    if success:
        print("✅ LLaMA session created successfully!")
    else:
        print("❌ Failed to create LLaMA session")
except Exception as e:
    print(f"❌ Error creating LLaMA session: {e}")

print("\nSession management demo completed!")
