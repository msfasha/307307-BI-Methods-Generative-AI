from google import genai
from google.genai import types

# Choose a model. E.g. “gemini-2.5-flash” or whichever you have access to. :contentReference[oaicite:1]{index=1}
MODEL = "gemini-2.5-flash"

def ask_agent(prompt: str) -> str:

    # Initialize the client with your API key
    client = genai.Client(api_key="")

    response = client.models.generate_content(
        model=MODEL,
        contents=prompt
    )
    # The client returns a structure; here we extract the generated text
    return response.text or ""

def run_agent():
    print("Agent ready. Type 'exit' to quit.")
    while True:
        user = input("You: ")
        if user.strip().lower() == "exit":
            break
        reply = ask_agent(user)
        print("Agent:", reply)

if __name__ == "__main__":
    run_agent()