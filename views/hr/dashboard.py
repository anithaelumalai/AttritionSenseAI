import streamlit as st
from utils.analytics import compute_overall_dataset_metrics, create_risk_distribution_donut, create_attrition_by_department_chart
from utils.data_loader import load_employee_dataset
from utils.ml_pipeline import load_trained_model, NUMERICAL_FEATURES, CATEGORICAL_FEATURES
from utils.feedback import get_feedback_metrics, get_latest_feedback
import pandas as pd

def render_hr_dashboard():
    st.markdown("""
        <div style="background: linear-gradient(135deg, #0f172a 0%, #1e3a8a 100%); padding: 1.8rem; border-radius: 12px; color: white; margin-bottom: 2rem;">
            <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 0.6rem;">
                <div>
                    <h1 style="margin: 0; font-size: 2.1rem;">HR Intelligence & Executive Radar</h1>
                    <p style="margin: 0.5rem 0 0 0; opacity: 0.85; font-size: 1.05rem;">Workforce Attrition Risk Monitoring • Predictive AI Analytics</p>
                </div>
                <div style="background: rgba(255,255,255,0.15); padding: 0.5rem 1rem; border-radius: 8px; font-size: 0.9rem; border: 1px solid rgba(255,255,255,0.2);">
                    Live Workforce: <b>1,470 Employees</b>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    with st.spinner("Computing workforce risk indices..."):
        metrics = compute_overall_dataset_metrics()
        
    # Top Row: 6 KPI Cards
    k1, k2, k3, k4, k5, k6 = st.columns(6)
    with k1:
        st.metric("Total Workforce", f"{metrics['total_employees']:,}")
    with k2:
        st.metric("Avg Risk Score", f"{metrics['avg_risk_score']} / 100")
    with k3:
        st.metric("Historical Attrition", f"{metrics['historical_attrition_rate']}%", help="Historical attrition rate in baseline data")
    with k4:
        st.metric("High Risk (🚨)", f"{metrics['high_risk_count']}", f"{metrics['high_risk_pct']}%", delta_color="inverse")
    with k5:
        st.metric("Medium Risk (⚠️)", f"{metrics['med_risk_count']}", f"{metrics['med_risk_pct']}%", delta_color="off")
    with k6:
        st.metric("Low Risk (✅)", f"{metrics['low_risk_count']}", f"{metrics['low_risk_pct']}%", delta_color="normal")

    st.markdown("---")
    
    # Second Row: Visual Distribution Charts
    c_chart1, c_chart2 = st.columns([1, 1])
    with c_chart1:
        donut_fig = create_risk_distribution_donut(metrics)
        st.plotly_chart(donut_fig, use_container_width=True)
        
    with c_chart2:
        dept_fig = create_attrition_by_department_chart()
        st.plotly_chart(dept_fig, use_container_width=True)

    st.markdown("---")
    
    # Second Row (B): New Employee Feedback Section
    st.markdown("### 📩 New Employee Feedback")
    latest_fb = get_latest_feedback()
    fb_metrics = get_feedback_metrics()
    total_fb_count = fb_metrics.get("total_feedback", 0)

    if latest_fb:
        f_col1, f_col2 = st.columns([1, 2])
        with f_col1:
            st.metric("Total Submissions", f"{total_fb_count}")
            st.metric("Avg Org Job Satisfaction", f"{fb_metrics.get('avg_job_satisfaction', 0.0)} / 5.0")
            st.metric("Stay Intent Rate", f"{fb_metrics.get('stay_intent_pct', 0.0)}%")
        with f_col2:
            is_anon = latest_fb.get("is_anonymous", 0) == 1
            submitter_display = "Anonymous Employee (Identity Confidential)" if is_anon else f"Employee ID #{latest_fb.get('employee_id', 'N/A')}"
            submitted_time = latest_fb.get("created_at", "Recently")
            comments = latest_fb.get("comments", "").strip() or "No additional comments provided."
            raw_status = latest_fb.get("email_status", "Sent")
            if raw_status == "Sent":
                status_badge = '<span style="background: #dcfce7; color: #15803d; padding: 2px 8px; border-radius: 12px; font-weight: 600; font-size: 0.78rem; border: 1px solid #86efac;">✉️ Notification Sent to HR</span>'
            elif raw_status == "Not Configured":
                status_badge = '<span style="background: #fef9c3; color: #854d0e; padding: 2px 8px; border-radius: 12px; font-weight: 600; font-size: 0.78rem; border: 1px solid #fde047;">⚠️ Email Not Configured</span>'
            else:
                status_badge = f'<span style="background: #fee2e2; color: #991b1b; padding: 2px 8px; border-radius: 12px; font-weight: 600; font-size: 0.78rem; border: 1px solid #fca5a5;">❌ Notification {raw_status}</span>'

            st.markdown(f"""
                <div style="background: #f8fafc; border: 1px solid #cbd5e1; border-left: 5px solid #0284c7; border-radius: 8px; padding: 1.2rem; margin-bottom: 0.8rem;">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem; flex-wrap: wrap; gap: 0.4rem;">
                        <span style="font-weight: bold; color: #1e3a8a; font-size: 1.05rem;">Latest Submission from: {submitter_display}</span>
                        <div style="display: flex; align-items: center; gap: 0.4rem;">
                            {status_badge}
                            <span style="font-size: 0.8rem; color: #64748b; background: #e2e8f0; padding: 3px 8px; border-radius: 12px;">🕒 {submitted_time}</span>
                        </div>
                    </div>
                    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(130px, 1fr)); gap: 0.5rem; margin: 0.8rem 0; font-size: 0.85rem;">
                        <div style="background: white; padding: 0.4rem 0.6rem; border-radius: 4px; border: 1px solid #e2e8f0;">
                            <b>Job Sat:</b> {latest_fb.get('job_satisfaction', '-')}/5
                        </div>
                        <div style="background: white; padding: 0.4rem 0.6rem; border-radius: 4px; border: 1px solid #e2e8f0;">
                            <b>Work-Life:</b> {latest_fb.get('work_life_balance', '-')}/5
                        </div>
                        <div style="background: white; padding: 0.4rem 0.6rem; border-radius: 4px; border: 1px solid #e2e8f0;">
                            <b>Mgr Support:</b> {latest_fb.get('manager_support', '-')}/5
                        </div>
                        <div style="background: white; padding: 0.4rem 0.6rem; border-radius: 4px; border: 1px solid #e2e8f0;">
                            <b>Workload:</b> {latest_fb.get('workload', '-')}/5
                        </div>
                        <div style="background: white; padding: 0.4rem 0.6rem; border-radius: 4px; border: 1px solid #e2e8f0;">
                            <b>Growth:</b> {latest_fb.get('career_growth', '-')}/5
                        </div>
                        <div style="background: white; padding: 0.4rem 0.6rem; border-radius: 4px; border: 1px solid #e2e8f0;">
                            <b>Recognition:</b> {latest_fb.get('recognition', '-')}/5
                        </div>
                        <div style="background: white; padding: 0.4rem 0.6rem; border-radius: 4px; border: 1px solid #e2e8f0;">
                            <b>Compensation:</b> {latest_fb.get('compensation_satisfaction', '-')}/5
                        </div>
                        <div style="background: white; padding: 0.4rem 0.6rem; border-radius: 4px; border: 1px solid #e2e8f0;">
                            <b>Stay Intent:</b> {latest_fb.get('intention_to_stay', '-')}/5
                        </div>
                    </div>
                    <div style="font-size: 0.9rem; color: #334155; margin-top: 0.5rem;">
                        <b>Employee Comments:</b> <i>"{comments}"</i>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            if st.button("View Full Feedback Sentiment Analytics →", key="btn_dash_to_feedback"):
                st.session_state.active_page = "feedback_analytics"
                st.rerun()
    else:
        st.info("No employee feedback submissions received yet. Once employees submit feedback through their portal, latest summaries will appear here.")

    st.markdown("---")
    
    # Third Row: Priority High-Risk Intervention Queue
    st.markdown("### 🚨 Priority High-Risk Intervention Queue (Top At-Risk Employees)")
    st.write("Employees with elevated attrition risk probability. Click an employee to automatically load their complete profile and retention plan:")
    
    df = load_employee_dataset()
    pipeline, _ = load_trained_model()
    
    X = df[NUMERICAL_FEATURES + CATEGORICAL_FEATURES].copy()
    probs = pipeline.predict_proba(X)[:, 1]
    
    risk_df = pd.DataFrame({
        "EmployeeNumber": df["EmployeeNumber"],
        "Department": df["Department"],
        "JobRole": df["JobRole"],
        "OverTime": df["OverTime"],
        "JobSatisfaction": df["JobSatisfaction"],
        "YearsAtCompany": df["YearsAtCompany"],
        "RiskScore": (probs * 100.0).round(1),
        "AttritionProb": (probs * 100.0).round(1)
    })
    
    high_risk_table = risk_df.sort_values(by="RiskScore", ascending=False).head(10)
    
    # Display priority table
    st.dataframe(
        high_risk_table.rename(columns={
            "EmployeeNumber": "Employee ID",
            "JobRole": "Job Role",
            "OverTime": "OverTime",
            "JobSatisfaction": "Job Sat (1-4)",
            "YearsAtCompany": "Tenure (Yrs)",
            "RiskScore": "Risk Score / 100",
            "AttritionProb": "Attrition Prob %"
        }),
        use_container_width=True,
        hide_index=True
    )
    
    col_jump1, col_jump2 = st.columns([3, 1])
    with col_jump1:
        st.caption("💡 To perform deep-dive risk factor analysis, retention recommendation generation, and generate PDF reports, go to the Employee Search & Prediction page.")
    with col_jump2:
        if st.button("Go to Search & Prediction 🔎", key="btn_dash_to_search", use_container_width=True, type="primary"):
            st.session_state.active_page = "employee_search_prediction"
            st.rerun()
