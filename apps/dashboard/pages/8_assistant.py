"""Page 8: AI Health Assistant -- conversational agent with Oura data and PubMed."""

from __future__ import annotations

import streamlit as st
from plotly.io import from_json

from components.agent import run_assistant_turn
from styles import (
    get_custom_css,
    page_header,
    empty_state,
    neon_badge,
)

st.markdown(get_custom_css(), unsafe_allow_html=True)

token = st.session_state.get("access_token", "")
sandbox = st.session_state.get("sandbox_mode", False)
start = st.session_state.get("start_date", "")
end = st.session_state.get("end_date", "")

st.markdown(
    page_header("Assistant", "Ask questions about your health data"),
    unsafe_allow_html=True
)

# Capability badges
badges = [
    ("Oura Data", "cyan"),
    ("PubMed", "magenta"),
    ("Statistics", "amber"),
    ("Lab Results", "green"),
]
badge_html = " ".join([neon_badge(text, color) for text, color in badges])
st.markdown(f"<div style='margin-bottom: 1.5rem;'>{badge_html}</div>", unsafe_allow_html=True)

if not token:
    st.markdown(
        empty_state(
            "Authentication required",
            "Connect to Oura to use the AI assistant.",
            "◇"
        ),
        unsafe_allow_html=True
    )
    st.stop()

if "assistant_messages" not in st.session_state:
    st.session_state.assistant_messages = []

col1, col2 = st.columns([1, 5])
with col1:
    if st.button("Clear", type="secondary", use_container_width=True):
        st.session_state.assistant_messages = []
        st.rerun()

# Show empty state if no messages
if not st.session_state.assistant_messages:
    st.markdown(
        empty_state(
            "Start a conversation",
            "Ask about your sleep, activity, HRV, or research from PubMed.",
            "◇"
        ),
        unsafe_allow_html=True
    )

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

prompt = st.chat_input("Ask about your health data...")
if prompt:
    st.session_state.assistant_messages.append({"role": "user", "content": prompt})

    with st.chat_message("assistant"):
        with st.spinner("Analyzing..."):
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
