import anthropic
import os
import streamlit as st

# with st.sidebar:
#     anthropic_api_key = st.text_input("Anthropic API Key", key="file_qa_api_key", type="password")

anthropic_api_key = os.environ.get("CLAUDE_API_TOKEN", "DEFAULT_TOKEN")
MODEL_NAME = "claude-3-5-sonnet-20240620"

st.title("📝 File Q&A with Anthropic")

uploaded_file = st.file_uploader("Upload an article", type=("txt", "md", "json", "pdf"))

question = st.text_input(
    "Ask something about the article",
    placeholder="Can you give me a short summary?",
    disabled=not uploaded_file,
)

#if uploaded_file and question and not anthropic_api_key:
#    st.info("Please add your Anthropic API key to continue.")

if uploaded_file and question:
    article = uploaded_file.read().decode()
    prompt = [ 
        {
            "role": "user",
            "content": f"""Here's an article:\n\n{article}\n\n\n\n{question}"""
        }
    ]

    client = anthropic.Client(api_key=anthropic_api_key)
    response = client.messages.create(
        messages=prompt,
        # stop_sequences=[anthropic.HUMAN_PROMPT],
        model=MODEL_NAME,
        max_tokens=100,
    )
    st.write("### Answer")
    st.write(response.content[0].text)