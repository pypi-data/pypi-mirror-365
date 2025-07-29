import os
import sys
from openai import OpenAI, OpenAIError
from dotenv import load_dotenv

ENV_PATH = os.path.expanduser("~/.fixcmd.env")
VERSION = "0.1.3"

def load_and_validate_api_key():
    load_dotenv(dotenv_path=ENV_PATH)
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return None, False
    try:
        client = OpenAI(api_key=api_key)
        client.models.list()
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
                    "Reply ONLY with the correct shell command in a single line. "
                    "If unsure, say 'I don't know'."
                )},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2
        )
        return response.choices[0].message.content.strip()
    except Exception:
        return None

def get_error_explanation(client, error_message):
    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": (
                    "You are a Linux assistant. Explain clearly what this terminal error means and how to fix it. "
                    "Use plain text only. Highlight commands by starting them with $. Do not use markdown."
                )},
                {"role": "user", "content": f"Error:\n{error_message}\nExplain and fix."}
            ],
            temperature=0.3
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"ERROR: GPT error: {e}"

def explain_command_usage(client, command):
    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": (
                    "You are a Linux terminal assistant. When a user provides a valid shell command, explain briefly what it does, and give a one-line example usage."
                )},
                {"role": "user", "content": f"What does this command do and give one example:\n{command}"}
            ],
            temperature=0.3
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return "ERROR: Could not get explanation or example."

def setup_api_key():
    print("🔧 SETUP: Enter your OpenAI API key")
    key = input("API key (starts with sk-): ").strip()
    if key.startswith("sk-"):
        os.makedirs(os.path.dirname(ENV_PATH), exist_ok=True)
        with open(ENV_PATH, "w") as f:
            f.write(f"OPENAI_API_KEY={key}\n")
        print(f"API key saved to {ENV_PATH}")
    else:
        print("ERROR: Invalid API key format.")

def main():
    if len(sys.argv) >= 2 and sys.argv[1] == "-setup":
        setup_api_key()
        return

    if len(sys.argv) >= 2 and sys.argv[1] == "-version":
        print(f"fixcmd version {VERSION}")
        return

    client, valid = load_and_validate_api_key()
    if not valid:
        print("ERROR: Invalid or missing OpenAI API key. Run `fixcmd -setup` to configure.")
        return

    if len(sys.argv) >= 3 and sys.argv[1] == "-ask":
        user_command = " ".join(sys.argv[2:])
        prompt = (
            f"The user asked about this shell command: '{user_command}'.\n"
            "1. If the command is valid, explain what it does, where it's commonly used, and give an example.\n"
            "2. If it's not valid or does not exist, suggest a similar existing command and explain that instead.\n"
            "Use plain text only. Do not use markdown. Use $ prefix for commands. Keep it concise but useful."
        )
        try:
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": (
                        "You are a Linux shell assistant. Help explain commands, detect typos, and suggest proper usage. "
                        "Reply in simple plain text. Highlight commands using $ prefix. Do not use markdown."
                    )},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.4
            )
            answer = response.choices[0].message.content.strip()
            print("\nExplanation:\n")
            for line in answer.splitlines():
                if line.strip().startswith("$"):
                    print(f"\033[92m{line}\033[0m")
                else:
                    print(line)
        except Exception as e:
            print(f"ERROR: GPT failed: {e}")
        return

    if len(sys.argv) >= 3 and sys.argv[1] == "-explain":
        error_message = " ".join(sys.argv[2:])
        explanation = get_error_explanation(client, error_message)
        print("\nExplanation:\n")
        for line in explanation.splitlines():
            if line.strip().startswith("$"):
                print(f"\033[92m{line}\033[0m")
            else:
                print(line)
        return

    if len(sys.argv) >= 3 and sys.argv[1] == "-fix":
        unsure_command = " ".join(sys.argv[2:])
        prompt = f"The user typed this unsure shell command:\n{unsure_command}\nWhat is the correct version?"
        response = get_command_suggestion(client, prompt)
        if not response or "i don't know" in response.lower():
            print("Could not fix that command.")
            return
        corrected = clean_command(response)
        usage_info = explain_command_usage(client, corrected)
        print(f"\nCorrected Command:\n  \033[92m{corrected}\033[0m\n")
        print(f"Usage & Example:\n{usage_info}\n")
        return

    if len(sys.argv) >= 2 and sys.argv[1] == "-help":
        print(f"""
📘 fixcmd - GPT-powered terminal assistant

Usage:
  fixcmd <invalid command>         - Auto-fix mistyped terminal commands
  fixcmd -fix "unsure command"     - Fix an unsure command and explain it
  fixcmd -ask "shell command"      - Explain or suggest the correct shell command
  fixcmd -explain "error message"  - Get explanation and fix for terminal errors
  fixcmd -setup                    - Setup your OpenAI API key
  fixcmd -version                  - Show version info
  fixcmd -help                     - Show this help message

Examples:
  fixcmd gti status
  fixcmd -fix "remove all jpgs"
  fixcmd -ask "rm -rf"
  fixcmd -explain "command not found"
""")
        return

    # Default fallback: try to fix mistyped command
    failed_command = " ".join(sys.argv[1:])
    prompt = f"The user typed this invalid shell command:\n{failed_command}\nWhat is the correct version?"
    response = get_command_suggestion(client, prompt)
    if not response:
        print(f"zsh: command not found: {failed_command}")
        return
    suggestion = clean_command(response)
    print(f"Invalid command:\n  \033[91m{failed_command}\033[0m\n")
    print(f"Suggested:\n  \033[92m{suggestion}\033[0m\n")

if __name__ == "__main__":
    main()
