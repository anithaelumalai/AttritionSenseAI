import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from utils.feedback import get_feedback_records, get_feedback_metrics

def render_feedback_analytics():
    st.markdown("""
        <div style="margin-bottom: 1.5rem;">
            <h2 style="color: #1e3a8a; margin: 0;">💬 Employee Feedback & Sentiment Analytics</h2>
            <p style="color: #64748b; margin: 0.2rem 0 0 0;">Aggregated workplace sentiment insights from submitted employee feedback</p>
        </div>
    """, unsafe_allow_html=True)
    
    st.info("🔒 **Strict Privacy Policy:** All ratings and open responses reflect solely voluntary submissions through the Employee Feedback portal. Individual private BuddyBot conversations, Mind-Free Game activities, and Weekend Quiz scores are strictly protected and never shown here.")

    metrics = get_feedback_metrics()
    df_feedback = get_feedback_records()
    
    if metrics["total_feedback"] == 0:
        st.warning("No employee feedback has been submitted yet. Once employees submit feedback through their portal, aggregated analytics will populate automatically.")
        return

    # Top KPI Cards
    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.metric("Total Submissions", f"{metrics['total_feedback']}")
    with k2:
        st.metric("Stay Intent Rate", f"{metrics['stay_intent_pct']}%", help="% of respondents rating intention to stay >= 4/5")
    with k3:
        st.metric("Confidential Submissions", f"{metrics['anonymous_count']}", f"{(metrics['anonymous_count']/metrics['total_feedback']*100):.0f}% Anonymous")
    with k4:
        st.metric("Identified Submissions", f"{metrics['identified_count']}", f"{(metrics['identified_count']/metrics['total_feedback']*100):.0f}% Identified")

    st.markdown("---")
    
    # 8-Dimension Radar & Bar Charts
    c_left, c_right = st.columns([1, 1])
    
    categories = [
        "Job Satisfaction", "Work-Life Balance", "Manager Support",
        "Workload", "Career Growth", "Recognition", "Compensation", "Stay Intent"
    ]
    scores = [
        metrics["avg_job_satisfaction"], metrics["avg_work_life_balance"],
        metrics["avg_manager_support"], metrics["avg_workload"],
        metrics["avg_career_growth"], metrics["avg_recognition"],
        metrics["avg_compensation"], metrics["avg_intention_to_stay"]
    ]
    
    with c_left:
        st.markdown("### 🕸️ 8-Dimension Sentiment Radar")
        fig_radar = go.Figure()
        fig_radar.add_trace(go.Scatterpolar(
            r=scores + [scores[0]],
            theta=categories + [categories[0]],
            fill='toself',
            fillcolor='rgba(2, 132, 199, 0.25)',
            line=dict(color='#0284c7', width=2),
            name="Org Average"
        ))
        fig_radar.update_layout(
            polar=dict(
                radialaxis=dict(visible=True, range=[0, 5])
            ),
            showlegend=False,
            margin=dict(l=40, r=40, t=20, b=20)
        )
        st.plotly_chart(fig_radar, use_container_width=True)

    with c_right:
        st.markdown("### 📊 Dimension Scores (Out of 5)")
        df_bars = pd.DataFrame({"Dimension": categories, "Score": scores})
        fig_bar = px.bar(
            df_bars,
            x="Score",
            y="Dimension",
            orientation="h",
            color="Score",
            color_continuous_scale=["#e63946", "#f4a261", "#2a9d8f"],
            range_x=[0, 5],
            text="Score"
        )
        fig_bar.update_layout(
            xaxis_title="Average Rating (1-5)",
            yaxis_title="",
            margin=dict(l=20, r=20, t=20, b=20)
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    st.markdown("---")
    
    # Common Concerns & Qualitative Insights
    st.markdown("### 💬 Common Concerns & Employee Comments")
    comments_df = df_feedback[df_feedback["comments"].str.strip().fillna("") != ""].copy()
    
    if comments_df.empty:
        st.caption("No written comments provided in submissions yet.")
    else:
        for _, row in comments_df.head(5).iterrows():
            is_anon = row.get("is_anonymous", 0) == 1
            submitter_label = "Anonymous Employee (Confidential)" if is_anon else f"Employee ID #{row.get('employee_id', 'N/A')}"
            ts = row.get("created_at", "")
            comm = row.get("comments", "").strip()
            wlb_val = row.get("work_life_balance", "-")
            load_val = row.get("workload", "-")
            sat_val = row.get("job_satisfaction", "-")
            
            st.markdown(f"""
                <div style="background: #ffffff; border: 1px solid #e2e8f0; border-left: 4px solid #f59e0b; border-radius: 6px; padding: 0.9rem 1.1rem; margin-bottom: 0.6rem;">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <b style="color: #1e293b;">{submitter_label}</b>
                        <span style="font-size: 0.75rem; color: #64748b;">🕒 {ts}</span>
                    </div>
                    <p style="margin: 0.4rem 0; color: #334155; font-size: 0.92rem;">"{comm}"</p>
                    <div style="font-size: 0.78rem; color: #64748b;">
                        <b>Satisfaction:</b> {sat_val}/5 | <b>Work-Life Balance:</b> {wlb_val}/5 | <b>Workload:</b> {load_val}/5
                    </div>
                </div>
            """, unsafe_allow_html=True)

    st.markdown("---")
    
    # Full Submissions Log
    st.markdown("### 📝 Full Employee Feedback Audit Log")
    
    display_df = df_feedback.copy()
    display_df["Employee ID"] = display_df.apply(
        lambda row: "Anonymous" if row["is_anonymous"] == 1 else f"Emp #{row['employee_id']}",
        axis=1
    )
    
    if "email_status" not in display_df.columns:
        display_df["email_status"] = "Sent"
    else:
        display_df["email_status"] = display_df["email_status"].fillna("Sent")

    cols_to_show = [
        "created_at", "Employee ID", "email_status", "job_satisfaction", "work_life_balance",
        "manager_support", "workload", "career_growth", "recognition",
        "compensation_satisfaction", "intention_to_stay", "comments"
    ]
    
    st.dataframe(
        display_df[cols_to_show].rename(columns={
            "created_at": "Timestamp",
            "email_status": "Email Status",
            "job_satisfaction": "Job Sat",
            "work_life_balance": "WLB",
            "manager_support": "Mgr Supp",
            "workload": "Workload",
            "career_growth": "Growth",
            "recognition": "Recog",
            "compensation_satisfaction": "Comp",
            "intention_to_stay": "Stay",
            "comments": "Employee Comments"
        }),
        use_container_width=True,
        hide_index=True
    )
