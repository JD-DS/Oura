"""Page 9: Data Import — upload Excel/CSV and lab PDFs."""

from __future__ import annotations

import streamlit as st
import pandas as pd

from config import DATA_DIR_ABSOLUTE
from health_import import (
    parse_excel,
    parse_lab_pdf,
    get_activity_store,
    get_lab_store,
    save_activity_rows,
    save_lab_results,
    query_activity,
    query_lab_results,
)
from styles import (
    get_custom_css,
    page_header,
    section_header,
    info_card,
    success_card,
)

theme_mode = st.session_state.get("theme_mode", "minimal")
st.markdown(get_custom_css(theme_mode), unsafe_allow_html=True)

start = st.session_state.get("start_date", "")
end = st.session_state.get("end_date", "")

st.markdown(
    page_header("Import", "Upload external health data", theme_mode),
    unsafe_allow_html=True
)

st.caption(f"Storage: `{DATA_DIR_ABSOLUTE}`")

tab1, tab2, tab3 = st.tabs(["Activity Data", "Lab Results", "View Imported"])

with tab1:
    st.markdown(section_header("Excel / CSV Upload", theme_mode), unsafe_allow_html=True)
    st.caption("Upload activity/nutrition data (date, steps, calories, workouts)")
    
    uploaded = st.file_uploader(
        "Choose file",
        type=["xlsx", "xls", "csv"],
        key="excel_upload",
        label_visibility="collapsed",
    )
    if uploaded:
        bytes_data = uploaded.read()
        filename = uploaded.name or "upload"
        df, errors = parse_excel(bytes_data, filename=filename)
        if errors:
            for e in errors:
                st.warning(e)
        if not df.empty:
            st.markdown(
                success_card(f"Parsed {len(df)} rows ({df['date'].min()} to {df['date'].max()})", theme_mode),
                unsafe_allow_html=True
            )
            st.dataframe(df.head(20), use_container_width=True, hide_index=True)
            if st.button("Save activity data", type="primary"):
                try:
                    conn = get_activity_store(DATA_DIR_ABSOLUTE)
                    n = save_activity_rows(conn, df, source=filename)
                    conn.close()
                    st.success(f"Saved {n} rows")
                except Exception as e:
                    st.error(str(e))

with tab2:
    st.markdown(section_header("Lab PDF Upload", theme_mode), unsafe_allow_html=True)
    st.caption("Upload blood panel PDFs (table layout supported)")
    
    pdf_uploaded = st.file_uploader(
        "Choose PDF",
        type=["pdf"],
        key="pdf_upload",
        label_visibility="collapsed",
    )
    panel_date = st.text_input("Panel date (YYYY-MM-DD)", placeholder="Leave blank to auto-detect")
    
    if pdf_uploaded:
        bytes_data = pdf_uploaded.read()
        filename = pdf_uploaded.name or "upload"
        results, errors = parse_lab_pdf(bytes_data, filename=filename, panel_date=panel_date or None)
        if errors:
            for e in errors:
                st.warning(e)
        if results:
            st.markdown(
                success_card(f"Extracted {len(results)} results", theme_mode),
                unsafe_allow_html=True
            )
            preview = pd.DataFrame(results)
            st.dataframe(preview, use_container_width=True, hide_index=True)
            if st.button("Save lab results", type="primary"):
                try:
                    conn = get_lab_store(DATA_DIR_ABSOLUTE)
                    n = save_lab_results(conn, results)
                    conn.close()
                    st.success(f"Saved {n} lab results")
                except Exception as e:
                    st.error(str(e))
        elif not errors:
            st.markdown(
                info_card("No results extracted. Try a different PDF or check the format.", theme_mode),
                unsafe_allow_html=True
            )

with tab3:
    if start and end:
        st.markdown(section_header("Activity Data", theme_mode), unsafe_allow_html=True)
        try:
            imported = query_activity(DATA_DIR_ABSOLUTE, start, end)
            if imported.empty:
                st.markdown(
                    info_card("No imported activity data for this range.", theme_mode),
                    unsafe_allow_html=True
                )
            else:
                st.dataframe(imported, use_container_width=True, hide_index=True)
        except Exception as e:
            st.error(str(e))
        
        st.markdown(section_header("Lab Results", theme_mode), unsafe_allow_html=True)
        try:
            labs = query_lab_results(DATA_DIR_ABSOLUTE, start, end)
            if labs.empty:
                st.markdown(
                    info_card("No lab results for this range.", theme_mode),
                    unsafe_allow_html=True
                )
            else:
                st.dataframe(labs, use_container_width=True, hide_index=True)
        except Exception as e:
            st.error(str(e))
    else:
        st.markdown(
            info_card("Select a date range in the sidebar to view imported data.", theme_mode),
            unsafe_allow_html=True
        )
