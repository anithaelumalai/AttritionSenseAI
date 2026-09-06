import streamlit as st
import pandas as pd
from utils.history import get_all_prediction_history

def render_prediction_history():
    st.markdown("""
        <div style="margin-bottom: 1.5rem;">
            <h2 style="color: #1e3a8a; margin: 0;">📜 Machine Learning Prediction History</h2>
            <p style="color: #64748b; margin: 0.2rem 0 0 0;">Historical audit log of all employee attrition risk evaluations</p>
        </div>
    """, unsafe_allow_html=True)
    
    df_hist = get_all_prediction_history(limit=500)
    
    if df_hist.empty:
        st.info("No prediction history recorded yet. Predictions run in the 'Employee Search & Prediction' tab will appear here automatically.")
        return

    # Filter controls
    f_col1, f_col2, f_col3 = st.columns([1, 1, 2])
    with f_col1:
        risk_filter = st.selectbox("Filter by Risk Level:", ["All", "HIGH RISK", "MEDIUM RISK", "LOW RISK"])
    with f_col2:
        search_emp = st.text_input("Filter by Employee ID:", placeholder="e.g. 1")
        
    filtered = df_hist.copy()
    if risk_filter != "All":
        filtered = filtered[filtered["risk_level"] == risk_filter]
    if search_emp.strip():
        filtered = filtered[filtered["employee_id"].astype(str).str.contains(search_emp.strip())]

    st.write(f"Displaying **{len(filtered)}** evaluations:")
    
    # Table view
    display_cols = ["created_at", "employee_id", "risk_level", "risk_score", "prediction", "probability"]
    
    st.dataframe(
        filtered[display_cols].rename(columns={
            "created_at": "Evaluation Timestamp",
            "employee_id": "Employee ID",
            "risk_level": "Risk Level",
            "risk_score": "Risk Score (0-100)",
            "prediction": "Prediction Class",
            "probability": "Attrition Probability"
        }),
        use_container_width=True,
        hide_index=True
    )
    
    # CSV Download
    csv_data = filtered.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="⬇️ Export Filtered History to CSV",
        data=csv_data,
        file_name="AttritionSense_Prediction_History.csv",
        mime="text/csv"
    )
