
import os
import streamlit as st
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

st.set_page_config(page_title="MAYÃ VIADO", page_icon="LOGO.png")
st.image("LOGO.png", width=120)
st.title("VIADO VOTA NO LULA")
st.caption("Atendimento inteligente da sua loja online")

api_key = os.getenv("GEMINI_API_KEY") or st.secrets.get("GEMINI_API_KEY")

if not api_key:
    st.error("Configure GEMINI_API_KEY no arquivo .env.")
    st.stop()

client = genai.Client(api_key=api_key)

SYSTEM_PROMPT = """
Você é o ShopAI, assistente virtual de uma loja online.
Seja simpático, educado e objetivo.
Ajude clientes com produtos, pedidos, entregas e trocas.
Não invente preços, estoques ou informações de pedidos.
"""

if "messages" not in st.session_state:
    st.session_state.messages = []

with st.sidebar:
    st.header("ShopAI")
    if st.button("Nova conversa"):
        st.session_state.messages = []
        st.rerun()

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

if prompt := st.chat_input("Como podemos ajudar?"):
    st.session_state.messages.append({
        "role": "user",
        "content": prompt
    })

    with st.chat_message("user"):
        st.write(prompt)

    with st.chat_message("assistant"):
        try:
            historico = [
                types.Content(
                    role="model" if m["role"] == "assistant" else "user",
                    parts=[types.Part.from_text(text=m["content"])]
                )
                for m in st.session_state.messages
            ]

            resposta = client.models.generate_content(
                model="gemini-3.5-flash-lite",
                contents=historico,
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_PROMPT
                )
            )

            texto = resposta.text or "Não consegui responder."
            st.write(texto)

            st.session_state.messages.append({
                "role": "assistant",
                "content": texto
            })

        except Exception as e:
            st.error(f"Erro ao consultar o Gemini: {e}")
