"""Page 8: AI Health Assistant."""

from __future__ import annotations

import streamlit as st
from plotly.io import from_json

from components.agent import run_assistant_turn
from styles import get_custom_css, page_header, empty_state

st.markdown(get_custom_css(), unsafe_allow_html=True)

token = st.session_state.get("access_token", "")
sandbox = st.session_state.get("sandbox_mode", False)
start = st.session_state.get("start_date", "")
end = st.session_state.get("end_date", "")

st.markdown(
    page_header("Assistant", "Ask questions about your health data"),
    unsafe_allow_html=True
)

# Capabilities
st.markdown("""
<div style="display: flex; gap: 0.75rem; margin-bottom: 1.5rem; flex-wrap: wrap;">
    <div style="background: #1C1C21; border: 1px solid rgba(255,255,255,0.06); border-radius: 8px; padding: 0.5rem 1rem; font-size: 0.8rem; color: #A1A1AA;">
        Oura metrics
    </div>
    <div style="background: #1C1C21; border: 1px solid rgba(255,255,255,0.06); border-radius: 8px; padding: 0.5rem 1rem; font-size: 0.8rem; color: #A1A1AA;">
        Lab results
    </div>
    <div style="background: #1C1C21; border: 1px solid rgba(255,255,255,0.06); border-radius: 8px; padding: 0.5rem 1rem; font-size: 0.8rem; color: #A1A1AA;">
        PubMed search
    </div>
    <div style="background: #1C1C21; border: 1px solid rgba(255,255,255,0.06); border-radius: 8px; padding: 0.5rem 1rem; font-size: 0.8rem; color: #A1A1AA;">
        Charts & analysis
    </div>
</div>
""", unsafe_allow_html=True)

if not token:
    st.markdown(
        empty_state("Connect your Oura account", "Authenticate to use the assistant.", "🔐"),
        unsafe_allow_html=True
    )
    st.stop()

if "assistant_messages" not in st.session_state:
    st.session_state.assistant_messages = []

# Clear chat button
col1, col2 = st.columns([6, 1])
with col2:
    if st.button("Clear", type="secondary", use_container_width=True):
        st.session_state.assistant_messages = []
        st.rerun()

# Empty state
if not st.session_state.assistant_messages:
    st.markdown("""
    <div style="text-align: center; padding: 3rem 2rem; color: #71717A;">
        <div style="font-size: 2rem; margin-bottom: 0.75rem; opacity: 0.5;">💬</div>
        <div style="font-size: 0.9rem;">Ask about your sleep, HRV, or activity trends</div>
    </div>
    """, unsafe_allow_html=True)

# Chat history
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

# Chat input
prompt = st.chat_input("Ask a question...")
if prompt:
    st.session_state.assistant_messages.append({"role": "user", "content": prompt})

    with st.chat_message("assistant"):
        with st.spinner(""):
            try:
                messages = [
                    {"role": m["role"], "content": m["content"]}
                    for m in st.session_state.assistant_messages
                ]
                charts_out = []
                text, _ = run_assistant_turn(
                    messages, token, sandbox,
                    start_date=start, end_date=end, charts_out=charts_out
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
                st.error(f"Error: {err}")
                st.session_state.assistant_messages.append({
                    "role": "assistant",
                    "content": f"Error: {err}"
                })

    st.rerun()
