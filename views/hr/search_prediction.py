import streamlit as st
import pandas as pd
from utils.data_loader import get_all_employee_ids, get_employee_by_id, validate_employee_id
from utils.prediction import predict_employee_attrition
from utils.recommendation import generate_retention_recommendations
from utils.pdf_report import generate_pdf_report
from utils.history import save_prediction_record

def render_employee_search_prediction():
    st.markdown("""
        <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 1.5rem; flex-wrap: wrap; gap: 0.5rem;">
            <div>
                <h2 style="color: #1e3a8a; margin: 0;">🔎 Employee Search & AI Attrition Prediction</h2>
                <p style="color: #64748b; margin: 0.2rem 0 0 0;">Automatic employee record retrieval, ML risk scoring, factor attribution, and retention planning</p>
            </div>
            <div style="background: #e0f2fe; color: #0284c7; padding: 0.4rem 0.8rem; border-radius: 20px; font-size: 0.85rem; font-weight: bold;">
                ⚡ Zero Manual ML Feature Entry
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    all_emp_ids = get_all_employee_ids()
    
    # Selection Controls
    col_ctrl1, col_ctrl2 = st.columns([2, 1])
    with col_ctrl1:
        # Provide both dropdown selector and manual input
        selected_id = st.selectbox(
            "Select Employee ID (from verified dataset):",
            options=all_emp_ids,
            index=0,
            help="Choose from actual EmployeeNumber records in employees.csv"
        )
    with col_ctrl2:
        custom_id_input = st.text_input("Or enter specific Employee ID:", placeholder="e.g. 1, 4, 10, 2068")
        if custom_id_input.strip():
            if validate_employee_id(custom_id_input.strip()):
                selected_id = int(custom_id_input.strip())
            else:
                st.error(f"Employee ID '{custom_id_input}' is not present in the dataset.")

    # Automatically load employee data
    emp_record = get_employee_by_id(selected_id)
    if not emp_record:
        st.error(f"Employee #{selected_id} record could not be loaded.")
        return

    # Display Automatically Loaded Employee Details
    st.markdown(f"### 📋 Verified Employee Profile: #{selected_id}")
    
    p1, p2, p3, p4 = st.columns(4)
    with p1:
        st.markdown(f"**Department:** {emp_record.get('Department')}")
        st.markdown(f"**Job Role:** {emp_record.get('JobRole')}")
        st.markdown(f"**Job Level:** Level {emp_record.get('JobLevel')}")
    with p2:
        st.markdown(f"**Age / Gender:** {emp_record.get('Age')} / {emp_record.get('Gender')}")
        st.markdown(f"**Monthly Income:** ${emp_record.get('MonthlyIncome', 0):,}")
        st.markdown(f"**Percent Salary Hike:** {emp_record.get('PercentSalaryHike')}%")
    with p3:
        st.markdown(f"**OverTime:** `{emp_record.get('OverTime')}`")
        st.markdown(f"**Job Satisfaction:** {emp_record.get('JobSatisfaction')}/4")
        st.markdown(f"**Environment Sat:** {emp_record.get('EnvironmentSatisfaction')}/4")
    with p4:
        st.markdown(f"**Years at Company:** {emp_record.get('YearsAtCompany')} yrs")
        st.markdown(f"**Years in Current Role:** {emp_record.get('YearsInCurrentRole')} yrs")
        st.markdown(f"**Years Since Last Promo:** {emp_record.get('YearsSinceLastPromotion')} yrs")

    st.markdown("---")
    
    # Prediction Section
    st.markdown("### 🤖 Random Forest Attrition Prediction & Risk Evaluation")
    
    col_action1, col_action2 = st.columns([1, 3])
    with col_action1:
        run_prediction = st.button("Generate ML Prediction & Retention Plan ⚡", type="primary", use_container_width=True)
    
    # Store or compute prediction in session state for this employee
    pred_key = f"pred_result_{selected_id}"
    if run_prediction or pred_key not in st.session_state:
        with st.spinner("Analyzing ML risk factors and computing Random Forest probabilities..."):
            pred_result = predict_employee_attrition(emp_record)
            recs = generate_retention_recommendations(emp_record, pred_result["risk_factors"])
            
            # Save prediction history automatically
            save_prediction_record(
                employee_id=str(selected_id),
                prediction=pred_result["prediction"],
                probability=pred_result["attrition_probability"],
                risk_score=pred_result["risk_score"],
                risk_level=pred_result["risk_level"],
                risk_factors=pred_result["risk_factors"],
                recommendations=recs,
                growth_status=pred_result.get("growth_status"),
                confidence=pred_result.get("confidence"),
                priority_retention=1 if pred_result.get("is_priority_retention") else 0
            )
            
            st.session_state[pred_key] = {
                "prediction": pred_result,
                "recommendations": recs
            }
            
    cached = st.session_state[pred_key]
    pred = cached["prediction"]
    recs = cached["recommendations"]

    # Render Risk Level Banner
    risk_level = pred["risk_level"]
    risk_score = pred["risk_score"]
    prob_pct = round(pred["attrition_probability"] * 100, 1)
    color = pred["color_hex"]
    growth_status = pred.get("growth_status", "Stable Contributor")
    confidence = pred.get("confidence", 85.0)
    is_priority = pred.get("is_priority_retention", False)
    
    st.markdown(f"""
        <div style="background-color: {color}15; border: 2px solid {color}; border-radius: 10px; padding: 1.2rem; margin: 1rem 0; display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 0.8rem;">
            <div>
                <div style="font-size: 0.85rem; font-weight: bold; text-transform: uppercase; color: {color};">Executive Risk Assessment</div>
                <div style="font-size: 1.8rem; font-weight: bold; color: {color};">{risk_level} — {pred['prediction']}</div>
                <div style="font-size: 0.95rem; color: #475569; margin-top: 0.2rem;">
                    Risk Score: <b>{risk_score} / 100</b> | Attrition Probability: <b>{prob_pct}%</b> | Confidence: <b>{confidence}%</b>
                </div>
            </div>
            <div style="display: flex; align-items: center; gap: 0.8rem; flex-wrap: wrap;">
                <div style="background: white; border: 1px solid #cbd5e1; padding: 0.4rem 0.8rem; border-radius: 8px; text-align: center;">
                    <div style="font-size: 0.72rem; color: #64748b; font-weight: bold; text-transform: uppercase;">Growth Status</div>
                    <div style="font-size: 0.95rem; font-weight: bold; color: #0284c7;">{growth_status}</div>
                </div>
                {'<div style="background: #ef4444; color: white; padding: 0.5rem 1rem; border-radius: 20px; font-weight: bold; font-size: 0.85rem;">⚠️ Priority Retention</div>' if is_priority else ''}
                <div style="background: {color}; color: white; padding: 0.5rem 1.2rem; border-radius: 25px; font-weight: bold; font-size: 1.1rem;">
                    {risk_score}/100
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    # Two Columns: Risk Drivers & Targeted Recommendations
    r_col1, r_col2 = st.columns([1, 1])
    
    with r_col1:
        st.markdown("#### 🚨 Detected Attrition Risk Drivers")
        factors = pred["risk_factors"]
        if factors:
            for f in factors:
                badge_bg = "#fee2e2" if f["severity"] == "High" else "#fef3c7" if f["severity"] == "Medium" else "#f1f5f9"
                badge_fg = "#991b1b" if f["severity"] == "High" else "#92400e" if f["severity"] == "Medium" else "#475569"
                st.markdown(f"""
                    <div style="border-left: 4px solid {badge_fg}; background: #f8fafc; padding: 0.8rem 1rem; border-radius: 4px; margin-bottom: 0.7rem;">
                        <div style="display: flex; justify-content: space-between;">
                            <strong style="color: #1e293b;">{f['factor']}</strong>
                            <span style="background: {badge_bg}; color: {badge_fg}; font-size: 0.75rem; font-weight: bold; padding: 2px 8px; border-radius: 12px;">{f['severity']}</span>
                        </div>
                        <p style="margin: 0.3rem 0 0 0; color: #64748b; font-size: 0.85rem;">{f['detail']}</p>
                    </div>
                """, unsafe_allow_html=True)
        else:
            st.success("✅ No critical attrition drivers identified for this employee. Engagement indicators remain healthy.")

    with r_col2:
        st.markdown("#### 💡 Prescriptive Retention Action Plan")
        if recs:
            for r in recs:
                st.markdown(f"""
                    <div style="border: 1px solid #e2e8f0; background: white; padding: 0.8rem 1rem; border-radius: 6px; margin-bottom: 0.7rem;">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <span style="font-size: 0.8rem; color: #0284c7; font-weight: bold; text-transform: uppercase;">{r['category']}</span>
                            <span style="font-size: 0.75rem; color: #64748b; background: #f1f5f9; padding: 2px 6px; border-radius: 4px;">{r['priority']}</span>
                        </div>
                        <strong style="color: #0f172a; font-size: 0.95rem;">{r['title']}</strong>
                        <p style="margin: 0.3rem 0 0.3rem 0; color: #475569; font-size: 0.85rem;">{r['action']}</p>
                        <div style="font-size: 0.75rem; color: #94a3b8;"><b>Responsible:</b> {r['owner']}</div>
                    </div>
                """, unsafe_allow_html=True)
        else:
            st.info("Continue standard quarterly development touchpoints and peer recognition.")

    st.markdown("---")
    
    # PDF Report Generation & Download
    st.markdown("### 📄 Executive PDF Assessment Report")
    st.write("Generate a formal, publication-ready PDF dossier containing the employee profile, ML risk breakdown, and sign-off block for HR records:")
    
    pdf_bytes = generate_pdf_report(emp_record, pred, recs)
    
    st.download_button(
        label=f"⬇️ Download Official PDF Report (Employee #{selected_id})",
        data=pdf_bytes,
        file_name=f"AttritionSense_Report_Emp_{selected_id}.pdf",
        mime="application/pdf",
        type="primary"
    )
