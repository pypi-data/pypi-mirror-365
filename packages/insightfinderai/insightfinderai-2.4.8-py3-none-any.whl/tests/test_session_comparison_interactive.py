
#!/usr/bin/env python3
"""
Interactive testing script for model comparison functionality
"""
import os
import sys
from typing import List

# Add the parent directory to the path so we can import the SDK
sys.path.insert(0, '/home/mustafa/Documents/LLMLabsSDK/chatgpt_sdk')

from insightfinderai import Client

def load_prompts_from_file(filename: str) -> List[str]:
    """Load prompts from a text file, one prompt per line."""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            prompts = [line.strip() for line in f.readlines() if line.strip()]
        return prompts
    except FileNotFoundError:
        print(f"❌ Error: File '{filename}' not found.")
        return []
    except Exception as e:
        print(f"❌ Error reading file: {str(e)}")
        return []

def get_prompts_from_user() -> List[str]:
    """Get prompts from user input."""
    print("\n📝 Enter your prompts (one per line). Type 'DONE' on a new line when finished:")
    prompts = []
    while True:
        prompt = input(">>> ").strip()
        if prompt.upper() == 'DONE':
            break
        if prompt:
            prompts.append(prompt)
    return prompts

def interactive_comparison():
    """Run interactive model comparison."""
    print("=" * 80)
    print("🤖 INTERACTIVE MODEL COMPARISON TOOL")
    print("=" * 80)
    
    # Initialize client
    try:
        client = Client(
            session_name="llm-eval-test",  # Use existing session
            username="mustafa",
            api_key="47b73a737d8a806ef37e1c6d7245b0671261faea",
            url="https://ai-stg.insightfinder.com"
        )
        print("✅ Client initialized successfully!")
    except Exception as e:
        print(f"❌ Failed to initialize client: {str(e)}")
        return
    
    while True:
        print("\n" + "─" * 60)
        print("🔄 NEW COMPARISON")
        print("─" * 60)
        
        # Get session names
        print("\n📋 Enter the two models/sessions to compare:")
        session1 = input("🔹 Session 1 name: ").strip()
        if not session1:
            print("❌ Session 1 name cannot be empty!")
            continue
            
        session2 = input("🔹 Session 2 name: ").strip()
        if not session2:
            print("❌ Session 2 name cannot be empty!")
            continue
            
        if session1 == session2:
            print("❌ Session names must be different!")
            continue
        
        # Get prompts
        print(f"\n📄 How would you like to provide prompts?")
        print("1. Load from file")
        print("2. Enter manually")
        
        choice = input("Choose option (1 or 2): ").strip()
        
        prompts = []
        if choice == "1":
            filename = input("\n📁 Enter filename (with path if needed): ").strip()
            if filename:
                prompts = load_prompts_from_file(filename)
        elif choice == "2":
            prompts = get_prompts_from_user()
        else:
            print("❌ Invalid choice!")
            continue
            
        if not prompts:
            print("❌ No prompts provided! Please try again.")
            continue
        
        print(f"\n📊 Loaded {len(prompts)} prompts:")
        for i, prompt in enumerate(prompts, 1):
            preview = prompt[:50] + "..." if len(prompt) > 50 else prompt
            print(f"  {i}. {preview}")
        
        # # Confirm before running
        # confirm = input(f"\n🚀 Run comparison between '{session1}' and '{session2}'? (y/n): ").strip().lower()
        # if confirm not in ['y', 'yes']:
        #     print("⏭️  Comparison skipped.")
        #     continue
        
        # Run comparison
        try:
            print(f"\n⏳ Running comparison...")
            print(f"   • Session 1: {session1}")
            print(f"   • Session 2: {session2}")
            print(f"   • Prompts: {len(prompts)}")
            print("   • Please wait...")
            
            comparison_result = client.compare_models(
                session1_name=session1,
                session2_name=session2,
                prompts=prompts,
                # stream=True
            )
            
            print("\n🎉 Comparison completed!")
            print("\n" + "=" * 120)
            print("RESULTS:")
            print("=" * 120)
            print(comparison_result)
            
        except Exception as e:
            print(f"\n❌ Error during comparison: {str(e)}")
            print("Please check your session names and try again.")
        
        # Ask if user wants to continue
        print("\n" + "─" * 60)
        continue_choice = input("🔄 Do you want to run another comparison? (y/n): ").strip().lower()
        if continue_choice not in ['y', 'yes']:
            break
    
    print("\n👋 Thank you for using the Interactive Model Comparison Tool!")
    print("=" * 80)

if __name__ == "__main__":
    try:
        interactive_comparison()
    except KeyboardInterrupt:
        print("\n\n⏹️  Interrupted by user. Goodbye!")
    except Exception as e:
        print(f"\n❌ Unexpected error: {str(e)}")
    finally:
        print("🔚 Exiting...")