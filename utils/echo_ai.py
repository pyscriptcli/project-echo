import streamlit as st
import requests
import json
from utils.db import fetch_echo_context

def query_global_team_archive(question: str, archive_records: list, chat_history: list) -> str:
    api_key = str(st.secrets.get("DEEPSEEK_API_KEY", "")).strip()
    if not api_key:
        return "⚠️ DeepSeek API Key is missing in Streamlit Secrets."
    
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    archive_context = json.dumps(archive_records, indent=1)
    
    # 1. Fetch Live Context from Supabase
    context_data = fetch_echo_context()
    
    # 2. Format it for the AI
    team_list = ", ".join(context_data.get('team', []))
    jargon_list = "\n".join([f"- {k}: {v}" for k, v in context_data.get('jargon', {}).items()])
    projects = ", ".join(context_data.get('projects', []))
    
    context_string = f"""
    ECHO KNOWLEDGE BASE (SOURCE OF TRUTH):
    ---------------------------------------
    TEAM MEMBERS: {team_list}
    ACTIVE PROJECTS: {projects}
    TECHNICAL JARGON:
    {jargon_list}
    
    INSTRUCTION: Use this knowledge base to correct proper nouns, acronyms, and project names in the archives. 
    If the archive says 'Cool Berneties' but the Knowledge Base says 'Kubernetes', you MUST use 'Kubernetes'.
    """

    system_prompt = (
        "You are Echo Global, an executive AI analyst for PRIME Philippines. "
        "Answer user questions accurately by synthesizing past meeting records, deadlines, and assigned persons-in-charge. "
        "Format responses in concise, professional corporate English with clean markdown bullet points."
        f"\n\n{context_string}\n"
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
