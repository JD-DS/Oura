"""Page 9: Data Import — upload Excel/CSV and lab PDFs."""

from __future__ import annotations

import streamlit as st
import pandas as pd

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
from styles import (
    get_custom_css,
    main_header,
    section_header,
    info_box,
    success_box,
)

st.markdown(get_custom_css(), unsafe_allow_html=True)

start = st.session_state.get("start_date", "")
end = st.session_state.get("end_date", "")

st.markdown(
    main_header(
        "Import Health Data",
        "Upload external data from fitness apps, nutrition trackers, and lab results"
    ),
    unsafe_allow_html=True
)

st.markdown("""
<div style="
    display: flex;
    gap: 1rem;
    margin-bottom: 1.5rem;
">
    <div style="
        flex: 1;
        background: rgba(108, 99, 255, 0.1);
        border: 1px solid rgba(108, 99, 255, 0.2);
        border-radius: 10px;
        padding: 1rem;
    ">
        <div style="font-size: 1.5rem; margin-bottom: 0.5rem;">📊</div>
        <div style="font-size: 0.85rem; font-weight: 500; color: #E0E0E0;">Excel / CSV</div>
        <div style="font-size: 0.75rem; color: #9CA3AF; margin-top: 0.25rem;">Activity, steps, calories, workouts</div>
    </div>
    <div style="
        flex: 1;
        background: rgba(78, 205, 196, 0.1);
        border: 1px solid rgba(78, 205, 196, 0.2);
        border-radius: 10px;
        padding: 1rem;
    ">
        <div style="font-size: 1.5rem; margin-bottom: 0.5rem;">🧪</div>
        <div style="font-size: 0.85rem; font-weight: 500; color: #E0E0E0;">Lab Results</div>
        <div style="font-size: 0.75rem; color: #9CA3AF; margin-top: 0.25rem;">Blood panels from PDFs</div>
    </div>
    <div style="
        flex: 1;
        background: rgba(102, 187, 106, 0.1);
        border: 1px solid rgba(102, 187, 106, 0.2);
        border-radius: 10px;
        padding: 1rem;
    ">
        <div style="font-size: 1.5rem; margin-bottom: 0.5rem;">💾</div>
        <div style="font-size: 0.85rem; font-weight: 500; color: #E0E0E0;">Local Storage</div>
        <div style="font-size: 0.75rem; color: #9CA3AF; margin-top: 0.25rem;">All data stays on your machine</div>
    </div>
</div>
""", unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["📊 Excel / CSV", "🧪 Lab Results (PDF)", "📋 View Imported Data"])

with tab1:
    st.markdown(section_header("Upload Activity Data"), unsafe_allow_html=True)
    st.markdown("""
    <p style="color: #9CA3AF; font-size: 0.9rem; margin-bottom: 1rem;">
        Upload spreadsheets with columns like <code>date</code>, <code>steps</code>, <code>calories</code>, <code>workouts</code>.
        The parser will auto-detect common column names.
    </p>
    """, unsafe_allow_html=True)
    
    uploaded = st.file_uploader(
        "Choose Excel or CSV file",
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
            st.markdown(
                success_box(f"✓ Parsed <strong>{len(df)}</strong> rows ({df['date'].min()} to {df['date'].max()})"),
                unsafe_allow_html=True
            )
            
            with st.expander("Preview data", expanded=True):
                st.dataframe(df.head(20), use_container_width=True, hide_index=True)
            
            if st.button("💾 Save to local database", type="primary", use_container_width=True):
                try:
                    conn = get_activity_store(DATA_DIR_ABSOLUTE)
                    n = save_activity_rows(conn, df, source=filename)
                    conn.close()
                    st.success(f"Saved {n} rows successfully!")
                    st.balloons()
                except Exception as e:
                    st.error(str(e))

with tab2:
    st.markdown(section_header("Upload Blood Panel PDFs"), unsafe_allow_html=True)
    st.markdown("""
    <p style="color: #9CA3AF; font-size: 0.9rem; margin-bottom: 1rem;">
        Upload lab result PDFs with table layouts. The parser extracts test names, values, units, and reference ranges.
    </p>
    """, unsafe_allow_html=True)
    
    pdf_uploaded = st.file_uploader(
        "Choose PDF file",
        type=["pdf"],
        key="pdf_upload",
    )
    
    panel_date = st.text_input(
        "Panel date (optional)",
        placeholder="YYYY-MM-DD — leave blank to auto-detect",
        help="If your PDF doesn't contain a clear date, specify it here"
    )
    
    if pdf_uploaded:
        bytes_data = pdf_uploaded.read()
        filename = pdf_uploaded.name or "upload"
        results, errors = parse_lab_pdf(bytes_data, filename=filename, panel_date=panel_date or None)
        
        if errors:
            for e in errors:
                st.warning(e)
        
        if results:
            st.markdown(
                success_box(f"✓ Extracted <strong>{len(results)}</strong> biomarker results"),
                unsafe_allow_html=True
            )
            
            preview = pd.DataFrame(results)
            with st.expander("Preview results", expanded=True):
                st.dataframe(preview, use_container_width=True, hide_index=True)
            
            if st.button("💾 Save to local database", type="primary", key="save_labs", use_container_width=True):
                try:
                    conn = get_lab_store(DATA_DIR_ABSOLUTE)
                    n = save_lab_results(conn, results)
                    conn.close()
                    st.success(f"Saved {n} lab results successfully!")
                    st.balloons()
                except Exception as e:
                    st.error(str(e))
        elif not errors:
            st.markdown(
                info_box("No results extracted. The PDF format may not be supported. Try a PDF with clear table layout."),
                unsafe_allow_html=True
            )

with tab3:
    st.markdown(section_header("Imported Data Browser"), unsafe_allow_html=True)
    
    if start and end:
        st.markdown(f"**Date range:** {start} to {end}")
        
        st.markdown("#### Activity Data", unsafe_allow_html=True)
        try:
            imported = query_activity(DATA_DIR_ABSOLUTE, start, end)
            if imported.empty:
                st.markdown(
                    info_box("No imported activity data for this date range."),
                    unsafe_allow_html=True
                )
            else:
                st.dataframe(imported, use_container_width=True, hide_index=True)
        except Exception as e:
            st.error(str(e))
        
        st.markdown("#### Lab Results", unsafe_allow_html=True)
        try:
            from src.health_import import query_lab_results
            labs = query_lab_results(DATA_DIR_ABSOLUTE, start, end)
            if labs.empty:
                st.markdown(
                    info_box("No lab results for this date range."),
                    unsafe_allow_html=True
                )
            else:
                st.dataframe(labs, use_container_width=True, hide_index=True)
        except Exception as e:
            st.error(str(e))
    else:
        st.markdown(
            info_box("Select a date range in the sidebar to view imported data."),
            unsafe_allow_html=True
        )

st.markdown("<hr>", unsafe_allow_html=True)
st.caption(f"📁 Data storage path: `{DATA_DIR_ABSOLUTE}`")
