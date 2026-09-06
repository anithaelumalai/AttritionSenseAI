import streamlit as st
from utils.auth import get_user_id
from utils.data_loader import get_employee_by_id

def render_employee_profile():
    emp_id = get_user_id()
    emp = get_employee_by_id(emp_id)
    
    st.markdown(f"""
        <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 1.5rem; flex-wrap: wrap; gap: 0.5rem;">
            <div>
                <h2 style="color: #1e3a8a; margin: 0;">👤 My Employee Profile</h2>
                <p style="color: #64748b; margin: 0.2rem 0 0 0;">Verified workplace records for Employee #{emp_id}</p>
            </div>
            <div style="background: #e0f2fe; color: #0369a1; padding: 0.4rem 0.8rem; border-radius: 20px; font-size: 0.85rem; font-weight: bold;">
                🔒 Official HR Record (Read-Only)
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    if not emp:
        st.error(f"Unable to load employee details for Employee #{emp_id}.")
        return

    # Section 1: Core Organization Data
    st.markdown("#### 🏢 Organizational Information")
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f"**Employee ID:** `{emp.get('EmployeeNumber')}`")
        st.markdown(f"**Department:** {emp.get('Department')}")
    with c2:
        st.markdown(f"**Job Role:** {emp.get('JobRole')}")
        st.markdown(f"**Job Level:** Level {emp.get('JobLevel')}")
    with c3:
        st.markdown(f"**Age:** {emp.get('Age')} years")
        st.markdown(f"**Gender:** {emp.get('Gender')}")
    with c4:
        st.markdown(f"**Marital Status:** {emp.get('MaritalStatus')}")
        st.markdown(f"**Business Travel:** {emp.get('BusinessTravel')}")

    st.markdown("---")
    
    # Section 2: Compensation & Tenure
    st.markdown("#### 💼 Compensation & Tenure History")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        monthly_inc = emp.get('MonthlyIncome', 0)
        st.metric("Monthly Income", f"${monthly_inc:,}")
        st.metric("Total Working Years", f"{emp.get('TotalWorkingYears', 0)} yrs")
    with col2:
        st.metric("Percent Salary Hike", f"{emp.get('PercentSalaryHike', 0)}%")
        st.metric("Years at Company", f"{emp.get('YearsAtCompany', 0)} yrs")
    with col3:
        st.metric("Stock Option Level", f"Level {emp.get('StockOptionLevel', 0)}")
        st.metric("Years in Current Role", f"{emp.get('YearsInCurrentRole', 0)} yrs")
    with col4:
        st.metric("OverTime Status", str(emp.get('OverTime', 'No')))
        st.metric("With Current Manager", f"{emp.get('YearsWithCurrManager', 0)} yrs")

    st.markdown("---")
    
    # Section 3: Engagement & Workplace Climate
    st.markdown("#### 🌱 Engagement & Workplace Ratings")
    s1, s2, s3, s4 = st.columns(4)
    
    def format_rating(val):
        labels = {1: "1 - Low", 2: "2 - Medium", 3: "3 - High", 4: "4 - Very High"}
        return labels.get(val, f"{val}/4")
        
    with s1:
        st.metric("Job Satisfaction", format_rating(emp.get('JobSatisfaction', 3)))
    with s2:
        st.metric("Environment Satisfaction", format_rating(emp.get('EnvironmentSatisfaction', 3)))
    with s3:
        st.metric("Work-Life Balance", format_rating(emp.get('WorkLifeBalance', 3)))
    with s4:
        st.metric("Job Involvement", format_rating(emp.get('JobInvolvement', 3)))

    st.markdown("---")
    
    # Additional Context
    st.markdown("#### 📍 Commute & Development")
    d1, d2, d3 = st.columns(3)
    with d1:
        st.markdown(f"**Distance from Home:** {emp.get('DistanceFromHome', 0)} miles")
        st.markdown(f"**Education Level:** {emp.get('Education', 1)} ({emp.get('EducationField', 'General')})")
    with d2:
        st.markdown(f"**Prior Companies Worked:** {emp.get('NumCompaniesWorked', 0)}")
        st.markdown(f"**Trainings Last Year:** {emp.get('TrainingTimesLastYear', 0)} completed")
    with d3:
        st.markdown(f"**Years Since Last Promotion:** {emp.get('YearsSinceLastPromotion', 0)} years")
        st.markdown(f"**Relationship Satisfaction:** {emp.get('RelationshipSatisfaction', 3)} / 4")
        
    st.info("🔒 Note: To maintain data integrity and automated ML objectivity, employee attributes are synchronized directly from authorized HR systems and cannot be modified manually.")
