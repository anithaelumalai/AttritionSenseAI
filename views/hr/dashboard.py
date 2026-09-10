import streamlit as st
import pandas as pd
from utils.analytics import (
    compute_overall_dataset_metrics,
    create_risk_distribution_donut,
    create_attrition_by_department_chart
)
from utils.feedback import get_feedback_metrics, get_latest_feedback
from utils.ai_analysis import (
    get_workforce_ai_analysis,
    record_priority_retention_alert,
    GROWTH_STATUS_HIGH,
    GROWTH_STATUS_STABLE,
    GROWTH_STATUS_SUPPORT,
    RISK_HIGH,
    RISK_MEDIUM,
    RISK_LOW,
    PRIORITY_RETENTION_LABEL
)

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
    
    with st.spinner("Computing workforce risk indices & AI evaluations..."):
        metrics = compute_overall_dataset_metrics()
        workforce_df = get_workforce_ai_analysis()
        
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

    # =========================================================================
    # PHASE 6: PRIORITY RETENTION ALERT CENTER
    # =========================================================================
    st.markdown("### ⚠️ Priority Retention Alert Center")
    st.markdown("""
        <p style="color: #64748b; margin-top: -0.5rem;">
            Proactive retention alerts triggered <strong>exclusively</strong> when 
            <span style="color: #0369a1; font-weight: 600;">High Growth Potential</span> coincides with 
            <span style="color: #dc2626; font-weight: 600;">High Risk</span>. 
            All other combinations are classified as <em>No Priority Retention</em>.
        </p>
    """, unsafe_allow_html=True)

    priority_df = workforce_df[workforce_df["IsPriorityRetention"] == True].copy()
    priority_count = len(priority_df)

    p_col1, p_col2, p_col3 = st.columns([1, 1, 2])
    with p_col1:
        st.metric("Priority Retention Cases", f"{priority_count}", f"{(priority_count/len(workforce_df)*100):.1f}% of workforce", delta_color="inverse")
    with p_col2:
        high_growth_count = len(workforce_df[workforce_df["GrowthStatus"] == GROWTH_STATUS_HIGH])
        st.metric("High Growth Potential Total", f"{high_growth_count}", "Talent Asset Pool")
    with p_col3:
        st.markdown(f"""
            <div style="background: #fef2f2; border: 1px solid #fecaca; border-left: 4px solid #ef4444; border-radius: 8px; padding: 0.8rem 1rem;">
                <p style="margin: 0; color: #991b1b; font-size: 0.88rem; font-weight: 600;">
                    🛡️ Immediate Retention Protocol:
                </p>
                <p style="margin: 0.2rem 0 0 0; color: #7f1d1d; font-size: 0.82rem;">
                    Identified {priority_count} critical personnel. Dispatch proactive stay interviews, review compensation competitiveness, and mitigate workload bottlenecks.
                </p>
            </div>
        """, unsafe_allow_html=True)

    # Top Priority Retention Cards
    st.markdown("#### 🎯 Priority Retention Action List")
    top_priority_cards = priority_df.sort_values(by="RiskScore", ascending=False).head(5)
    
    card_cols = st.columns(min(len(top_priority_cards), 5) or 1)
    for idx, (_, row) in enumerate(top_priority_cards.iterrows()):
        with card_cols[idx]:
            emp_id = row["EmployeeNumber"]
            st.markdown(f"""
                <div style="background: white; border: 1px solid #e2e8f0; border-top: 3px solid #ef4444; border-radius: 8px; padding: 0.8rem; box-shadow: 0 1px 3px rgba(0,0,0,0.05); margin-bottom: 0.5rem;">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.3rem;">
                        <span style="font-weight: 700; color: #1e3a8a; font-size: 0.9rem;">#{emp_id}</span>
                        <span style="background: #fee2e2; color: #991b1b; padding: 1px 6px; border-radius: 10px; font-size: 0.72rem; font-weight: 700;">Priority</span>
                    </div>
                    <div style="font-size: 0.8rem; color: #475569; font-weight: 600; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">{row['JobRole']}</div>
                    <div style="font-size: 0.75rem; color: #64748b;">{row['Department']}</div>
                    <hr style="margin: 0.4rem 0; border: 0; border-top: 1px solid #f1f5f9;" />
                    <div style="display: flex; justify-content: space-between; font-size: 0.76rem;">
                        <span style="color: #64748b;">Risk:</span>
                        <span style="color: #dc2626; font-weight: 700;">{row['RiskScore']}/100</span>
                    </div>
                    <div style="display: flex; justify-content: space-between; font-size: 0.76rem;">
                        <span style="color: #64748b;">Confidence:</span>
                        <span style="color: #0369a1; font-weight: 600;">{row['ConfidenceFormatted']}</span>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            if st.button("Notify HR ✉️", key=f"btn_notify_pr_{emp_id}", use_container_width=True):
                res = record_priority_retention_alert(
                    emp_id,
                    GROWTH_STATUS_HIGH,
                    RISK_HIGH,
                    {
                        "department": row["Department"],
                        "job_role": row["JobRole"],
                        "confidence": row["PredictionConfidence"],
                        "probability": row["AttritionProbability"]
                    }
                )
                if res["status"] == "duplicate":
                    st.warning(f"⚠️ {res['message']}")
                elif res["status"] == "sent":
                    st.success(f"✅ {res['message']}")
                else:
                    st.info(f"ℹ️ {res['message']}")

    st.markdown("---")

    # =========================================================================
    # PHASE 6: FULL WORKFORCE AI ANALYSIS ROSTER (ALL 1,470 EMPLOYEES)
    # =========================================================================
    st.markdown("### 🌐 Complete Workforce AI Roster (All 1,470 Employees)")
    st.caption("Comprehensive decision-support analysis for every verified employee in the organization.")

    # Multi-facet Filters
    flt_col1, flt_col2, flt_col3, flt_col4, flt_col5 = st.columns(5)
    with flt_col1:
        search_query = st.text_input("🔍 Search Employee ID:", placeholder="e.g. 102", key="wf_search")
    with flt_col2:
        dept_options = ["All"] + sorted(workforce_df["Department"].unique().tolist())
        selected_dept = st.selectbox("Department:", dept_options, key="wf_dept")
    with flt_col3:
        growth_options = ["All", GROWTH_STATUS_HIGH, GROWTH_STATUS_STABLE, GROWTH_STATUS_SUPPORT]
        selected_growth = st.selectbox("Growth Status:", growth_options, key="wf_growth")
    with flt_col4:
        risk_options = ["All", RISK_HIGH, RISK_MEDIUM, RISK_LOW]
        selected_risk = st.selectbox("Attrition Risk:", risk_options, key="wf_risk")
    with flt_col5:
        priority_options = ["All", "Priority Retention Only", "No Priority Retention"]
        selected_priority = st.selectbox("Priority Retention:", priority_options, key="wf_priority")

    # Apply Filters
    filtered_wf = workforce_df.copy()
    if search_query.strip():
        filtered_wf = filtered_wf[filtered_wf["EmployeeNumber"].astype(str).str.contains(search_query.strip())]
    if selected_dept != "All":
        filtered_wf = filtered_wf[filtered_wf["Department"] == selected_dept]
    if selected_growth != "All":
        filtered_wf = filtered_wf[filtered_wf["GrowthStatus"] == selected_growth]
    if selected_risk != "All":
        filtered_wf = filtered_wf[filtered_wf["AttritionRisk"] == selected_risk]
    if selected_priority == "Priority Retention Only":
        filtered_wf = filtered_wf[filtered_wf["IsPriorityRetention"] == True]
    elif selected_priority == "No Priority Retention":
        filtered_wf = filtered_wf[filtered_wf["IsPriorityRetention"] == False]

    st.write(f"Displaying **{len(filtered_wf):,}** of **1,470** employees:")

    # Display Table with exact required columns
    display_table = filtered_wf[[
        "EmployeeNumber",
        "Name",
        "Department",
        "JobRole",
        "GrowthStatus",
        "AttritionRisk",
        "ConfidenceFormatted",
        "PriorityRetention"
    ]].rename(columns={
        "EmployeeNumber": "Employee ID",
        "Name": "Name",
        "Department": "Department",
        "JobRole": "Job Role",
        "GrowthStatus": "Growth Status",
        "AttritionRisk": "Attrition Risk",
        "ConfidenceFormatted": "Confidence",
        "PriorityRetention": "Priority Retention"
    })

    st.dataframe(
        display_table,
        use_container_width=True,
        hide_index=True,
        height=380
    )

    st.markdown("---")

    # Second Row (B): Employee Feedback Section
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

    col_jump1, col_jump2 = st.columns([3, 1])
    with col_jump1:
        st.caption("💡 To perform deep-dive risk factor analysis, retention recommendation generation, and generate PDF reports, go to the Employee Search & Prediction page.")
    with col_jump2:
        if st.button("Go to Search & Prediction 🔎", key="btn_dash_to_search", use_container_width=True, type="primary"):
            st.session_state.active_page = "employee_search_prediction"
            st.rerun()
