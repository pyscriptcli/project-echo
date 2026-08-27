import streamlit as st
import requests
import json

def query_global_team_archive(question: str, archive_records: list, chat_history: list) -> str:
    api_key = str(st.secrets.get("DEEPSEEK_API_KEY", "")).strip()
    if not api_key:
        return "⚠️ DeepSeek API Key is missing in Streamlit Secrets."

    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    archive_context = json.dumps(archive_records, indent=1)

    system_prompt = (
        "You are Echo Global, an executive AI analyst for PRIME Philippines. "
        "Answer user questions accurately by synthesizing past meeting records, deadlines, and assigned persons-in-charge. "
        "Format responses in concise, professional corporate English with clean markdown bullet points."
    )

    messages = [{"role": "system", "content": f"{system_prompt}\n\nArchives:\n{archive_context[:28000]}"}]
    for msg in chat_history[-6:]:
        messages.append({"role": msg["role"], "content": msg["content"]})
    messages.append({"role": "user", "content": question})

    try:
        resp = requests.post(
            "https://api.deepseek.com/chat/completions",
            headers=headers,
            json={"model": "deepseek-chat", "messages": messages, "temperature": 0.2, "max_tokens": 750},
            timeout=60
        )
        if resp.status_code == 200:
            return resp.json()["choices"][0]["message"]["content"].strip()
        return f"⚠️ API Error ({resp.status_code}): {resp.text}"
    except Exception as e:
        return f"⚠️ Connection error: {e}"
