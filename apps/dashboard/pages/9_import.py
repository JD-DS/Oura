"""Page 9: Data Import — upload Excel/CSV and lab PDFs."""

from __future__ import annotations

import streamlit as st

from config import DATA_DIR_ABSOLUTE
from src.health_import import (
    parse_excel,
    parse_lab_pdf,
    get_activity_store,
    get_lab_store,
    save_activity_rows,
    save_lab_results,
    query_activity,
)

st.set_page_config(page_title="Data Import", page_icon="📥", layout="wide")

start = st.session_state.get("start_date", "")
end = st.session_state.get("end_date", "")

st.header("Import External Health Data")
st.caption(f"Storage path: `{DATA_DIR_ABSOLUTE}`")

tab1, tab2, tab3 = st.tabs(["Excel / CSV", "Lab Results (PDF)", "Imported Data"])

with tab1:
    st.markdown("Upload activity/nutrition data (date, steps, calories, workouts).")
    uploaded = st.file_uploader(
        "Choose Excel or CSV",
        type=["xlsx", "xls", "csv"],
        key="excel_upload",
    )
    if uploaded:
        bytes_data = uploaded.read()
        filename = uploaded.name or "upload"
        df, errors = parse_excel(bytes_data, filename=filename)
        if errors:
            for e in errors:
                st.warning(e)
        if not df.empty:
            st.success(f"Parsed {len(df)} rows ({df['date'].min()} to {df['date'].max()})")
            st.dataframe(df.head(20), use_container_width=True)
            if st.button("Save activity data"):
                try:
                    conn = get_activity_store(DATA_DIR_ABSOLUTE)
                    n = save_activity_rows(conn, df, source=filename)
                    conn.close()
                    st.success(f"Saved {n} rows.")
                except Exception as e:
                    st.error(str(e))

with tab2:
    st.markdown("Upload blood panel PDFs. Common formats (table layout) are supported.")
    pdf_uploaded = st.file_uploader(
        "Choose PDF",
        type=["pdf"],
        key="pdf_upload",
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
            st.success(f"Extracted {len(results)} results")
            import pandas as pd
            preview = pd.DataFrame(results)
            st.dataframe(preview, use_container_width=True)
            if st.button("Save lab results"):
                try:
                    conn = get_lab_store(DATA_DIR_ABSOLUTE)
                    n = save_lab_results(conn, results)
                    conn.close()
                    st.success(f"Saved {n} lab results.")
                except Exception as e:
                    st.error(str(e))
        elif not errors:
            st.info("No results extracted. Try a different PDF or check the format.")

with tab3:
    if start and end:
        st.subheader("Activity data")
        try:
            imported = query_activity(DATA_DIR_ABSOLUTE, start, end)
            if imported.empty:
                st.info("No imported activity data for this range.")
            else:
                st.dataframe(imported, use_container_width=True)
        except Exception as e:
            st.error(str(e))
        st.subheader("Lab results")
        try:
            from src.health_import import query_lab_results
            labs = query_lab_results(DATA_DIR_ABSOLUTE, start, end)
            if labs.empty:
                st.info("No lab results for this range.")
            else:
                st.dataframe(labs, use_container_width=True)
        except Exception as e:
            st.error(str(e))
