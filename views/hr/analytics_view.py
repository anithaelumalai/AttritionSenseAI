import streamlit as st
from utils.analytics import (
    create_attrition_by_department_chart,
    create_attrition_by_job_role_chart,
    create_attrition_by_overtime_chart,
    create_attrition_by_satisfaction_chart,
    create_income_distribution_chart,
    create_tenure_promotion_chart
)
from utils.data_loader import load_employee_dataset
import plotly.express as px
import pandas as pd

def render_hr_analytics():
    st.markdown("""
        <div style="margin-bottom: 1.5rem;">
            <h2 style="color: #1e3a8a; margin: 0;">📊 Deep-Dive Workforce Attrition Analytics</h2>
            <p style="color: #64748b; margin: 0.2rem 0 0 0;">Multi-dimensional diagnostic insights into workforce turnover trends and drivers</p>
        </div>
    """, unsafe_allow_html=True)
    
    df = load_employee_dataset()
    
    tab1, tab2, tab3, tab4 = st.tabs([
        "🏢 Department & Job Roles",
        "⏰ Overtime & Workload",
        "🌱 Satisfaction & Climate",
        "💰 Compensation, Tenure & Age"
    ])
    
    with tab1:
        st.markdown("### Organizational Attrition by Structure")
        col1, col2 = st.columns([1, 1])
        with col1:
            st.plotly_chart(create_attrition_by_department_chart(df), use_container_width=True)
        with col2:
            st.plotly_chart(create_attrition_by_job_role_chart(df), use_container_width=True)
            
        st.markdown("#### Key Structural Takeaways:")
        st.write("""
            - **Sales Representatives** and **Laboratory Technicians** historically display higher turnover propensity.
            - **Research & Development** maintains the highest absolute headcount retention due to specialized project alignment.
        """)

    with tab2:
        st.markdown("### Impact of Overtime & Travel on Retention")
        col_ot1, col_ot2 = st.columns([1, 1])
        with col_ot1:
            st.plotly_chart(create_attrition_by_overtime_chart(df), use_container_width=True)
        with col_ot2:
            travel_attr = df.groupby(["BusinessTravel", "Attrition"]).size().reset_index(name="Count")
            travel_fig = px.bar(
                travel_attr,
                x="BusinessTravel",
                y="Count",
                color="Attrition",
                barmode="group",
                color_discrete_map={"Yes": "#e63946", "No": "#2a9d8f"},
                title="Attrition by Business Travel Frequency"
            )
            st.plotly_chart(travel_fig, use_container_width=True)
            
        st.warning("⚠️ **Overtime Driver Alert:** Employees working overtime exhibit more than triple the attrition probability of their non-overtime peers.")

    with tab3:
        st.markdown("### Job Satisfaction & Workplace Environment")
        col_sat1, col_sat2 = st.columns([1, 1])
        with col_sat1:
            st.plotly_chart(create_attrition_by_satisfaction_chart(df), use_container_width=True)
        with col_sat2:
            env_df = df.groupby("EnvironmentSatisfaction")["Attrition"].apply(lambda x: (x == "Yes").mean() * 100.0).reset_index(name="Rate")
            env_df["EnvLabel"] = env_df["EnvironmentSatisfaction"].map({1: "1 - Low", 2: "2 - Medium", 3: "3 - High", 4: "4 - Very High"})
            env_fig = px.bar(
                env_df,
                x="EnvLabel",
                y="Rate",
                color="Rate",
                color_continuous_scale=["#2a9d8f", "#e63946"],
                title="Attrition Rate by Environment Satisfaction (%)"
            )
            st.plotly_chart(env_fig, use_container_width=True)

    with tab4:
        st.markdown("### Financial & Tenure Dynamics")
        col_f1, col_f2 = st.columns([1, 1])
        with col_f1:
            st.plotly_chart(create_income_distribution_chart(df), use_container_width=True)
        with col_f2:
            st.plotly_chart(create_tenure_promotion_chart(df), use_container_width=True)
            
        # Age group chart
        df["AgeGroup"] = pd.cut(df["Age"], bins=[17, 29, 39, 49, 65], labels=["18-29", "30-39", "40-49", "50+"])
        age_attr = df.groupby(["AgeGroup", "Attrition"], observed=False).size().reset_index(name="Count")
        age_fig = px.bar(
            age_attr,
            x="AgeGroup",
            y="Count",
            color="Attrition",
            barmode="group",
            color_discrete_map={"Yes": "#e63946", "No": "#2a9d8f"},
            title="Attrition by Age Demographics"
        )
        st.plotly_chart(age_fig, use_container_width=True)
