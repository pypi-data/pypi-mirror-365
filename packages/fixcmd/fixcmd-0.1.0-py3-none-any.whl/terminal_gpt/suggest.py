import os
import sys
from openai import OpenAI, OpenAIError
from dotenv import load_dotenv, set_key, find_dotenv

ENV_PATH = os.path.expanduser("~/.fixcmd.env")

def load_and_validate_api_key():
    load_dotenv(dotenv_path=ENV_PATH)
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return None, False
    try:
        client = OpenAI(api_key=api_key)
        client.models.list()  # Test call
        return client, True
    except OpenAIError:
        return None, False

def clean_command(text):
    for line in text.splitlines():
        line = line.strip()
        if line.startswith(("git ", "ls ", "cd ", "sudo ", "./", "echo ", "python ", "npm ", "curl ")):
            return line
    if ":" in text:
        return text.split(":", 1)[-1].strip()
    return text.strip()

def get_command_suggestion(client, prompt):
    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": (
                    "You are a helpful Linux assistant. "
                    "You answer ONLY with the correct shell command in a single line — no explanation. "
                    "If you don't know, reply 'I don't know'."
                )},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return None

def get_error_explanation(client, error_message):
    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": (
                    "You're a helpful Linux assistant. "
                    "When a user provides a terminal error message, explain what it means and how to fix it. "
                    "Keep the explanation short and clear."
                )},
                {"role": "user", "content": f"I got this error:\n\n{error_message}\n\nExplain what it means and how I can fix it."}
            ],
            temperature=0.3
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"❌ GPT error: {e}"

def ask_user_and_prefill(suggestion):
    print(f"🤖 Command: \033[92m{suggestion}\033[0m")

def setup_api_key():
    print("🔑 Setup: Enter your OpenAI API key")
    key = input("OpenAI API key (starts with sk-): ").strip()
    if key.startswith("sk-"):
        os.makedirs(os.path.dirname(ENV_PATH), exist_ok=True)
        with open(ENV_PATH, "w") as f:
            f.write(f"OPENAI_API_KEY={key}\n")
        print(f"✅ API key saved to {ENV_PATH}")
    else:
        print("❌ Invalid API key format.")

def main():
    if len(sys.argv) >= 2 and sys.argv[1] == "-setup":
        setup_api_key()
        return

    client, valid = load_and_validate_api_key()
    if not valid:
        print("❌ Invalid or missing OpenAI API key. Run `fixcmd -setup` to configure.")
        return

    if len(sys.argv) >= 3 and sys.argv[1] == "-ask":
        question = " ".join(sys.argv[2:])
        response = get_command_suggestion(client, question)
        if not response or "i don't know" in response.lower():
            print("🤖 I don't know.")
            return
        cleaned = clean_command(response)
        ask_user_and_prefill(cleaned)
        return

    if len(sys.argv) >= 2 and sys.argv[1] == "-help":
        print("""
📘 fixcmd - GPT-powered terminal assistant

Usage:
  fixcmd <invalid command>         - Auto-fix mistyped terminal commands
  fixcmd -ask "your question"      - Ask GPT to generate a valid shell command
  fixcmd -explain "error message"  - Get explanation and fix for terminal errors
  fixcmd -setup                    - Setup your OpenAI API key
  fixcmd -help                     - Show this help message

Examples:
  fixcmd gti status
  fixcmd -ask "how to push to GitHub?"
  fixcmd -explain "fatal: not a git repository"

Note: API key is stored in ~/.fixcmd.env
""")
        return

    if len(sys.argv) >= 3 and sys.argv[1] == "-explain":
        error_message = " ".join(sys.argv[2:])
        explanation = get_error_explanation(client, error_message)
        print("\n📘 Explanation:\n")
        print(explanation)
        return

    if len(sys.argv) < 2:
        print("Usage:\n  fixcmd <invalid command>\n  fixcmd -ask \"your question\"\n  fixcmd -explain \"error message\"\n  fixcmd -setup")
        return

    failed_command = " ".join(sys.argv[1:])
    prompt = f"The user typed this invalid shell command:\n{failed_command}\nWhat is the correct version?"
    response = get_command_suggestion(client, prompt)
    if not response:
        print(f"zsh: command not found: {failed_command}")
        return

    suggestion = clean_command(response)
    ask_user_and_prefill(suggestion)

if __name__ == "__main__":
    main()
