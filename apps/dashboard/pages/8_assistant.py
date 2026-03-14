"""Page 8: AI Health Assistant -- conversational agent with Oura data and PubMed."""

from __future__ import annotations

import streamlit as st
from plotly.io import from_json

from components.agent import run_assistant_turn

st.set_page_config(page_title="AI Assistant", page_icon="🤖", layout="wide")

token = st.session_state.get("access_token", "")
sandbox = st.session_state.get("sandbox_mode", False)
start = st.session_state.get("start_date", "")
end = st.session_state.get("end_date", "")

st.header("AI Health Assistant")
st.markdown(
    "Ask questions about your Oura data, explore research from PubMed, "
    "or request statistical analysis. The assistant has access to your health metrics "
    "for the selected date range."
)

if not token:
    st.warning("Authenticate with Oura to use the AI assistant.")
    st.stop()

if "assistant_messages" not in st.session_state:
    st.session_state.assistant_messages = []

if st.button("Clear chat", type="secondary"):
    st.session_state.assistant_messages = []
    st.rerun()

for msg in st.session_state.assistant_messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        for chart in msg.get("charts", []):
            fig_json = chart.get("fig_json")
            if fig_json:
                try:
                    fig = from_json(fig_json)
                    st.plotly_chart(fig, use_container_width=True)
                except Exception:
                    pass

prompt = st.chat_input("Ask about your health data, e.g. 'How was my sleep this week?'")
if prompt:
    st.session_state.assistant_messages.append({"role": "user", "content": prompt})

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                messages = [{"role": m["role"], "content": m["content"]} for m in st.session_state.assistant_messages]
                charts_out = []
                text, _ = run_assistant_turn(
                    messages, token, sandbox, start_date=start, end_date=end, charts_out=charts_out
                )
                st.markdown(text)
                for chart in charts_out:
                    try:
                        fig = from_json(chart["fig_json"])
                        st.plotly_chart(fig, use_container_width=True)
                    except Exception:
                        pass
                st.session_state.assistant_messages.append({
                    "role": "assistant",
                    "content": text,
                    "charts": charts_out,
                })
            except Exception as e:
                err = str(e)
                st.error(err)
                st.session_state.assistant_messages.append({"role": "assistant", "content": f"Error: {err}"})

    st.rerun()
