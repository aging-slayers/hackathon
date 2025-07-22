import anthropic
from openai import OpenAI
import os

LLAMA3_API = "http://80.209.242.40:8000/v1"
LLAMA3_KEY = "dummy-key2"
LLAMA3_MODEL = "llama-3.3-70b-instruct"

llama_params = {
        "max_tokens": 1024,
        "temperature": 0.8
    }

CLAUDE_KEY = os.environ.get("CLAUDE_API_TOKEN", "")
CLAUDE_MODEL = "claude-sonnet-4-20250514"

client = OpenAI(
    base_url = LLAMA3_API,
    api_key = LLAMA3_KEY
)

def query_llama(query: str) -> str:
    response = client.chat.completions.create(
        model=LLAMA3_MODEL,
        messages=[
            {"role": "user", "content": query}
        ],
        **llama_params
    )

    res = response.choices[0].message.content
    return res

def query_claude(query: str) -> str:
    client = anthropic.Anthropic(api_key=CLAUDE_KEY)
    
    response = client.messages.create(
        model=CLAUDE_MODEL,
        max_tokens=1024,
        messages=[
            {"role": "user", "content": query}
        ]
    )

    res = response.content[0].text
    return res

if __name__ == "__main__":
    query = "Describe all possible combinations of rapamycin with other substances and its effent on longevity and aging processes. Return a succint answer in a bullted list"
    ret = query_llama(query)
    print("LLaMA output:")
    print(ret)

    ret = query_claude(query)
    print("Claude output:")
    print(ret)