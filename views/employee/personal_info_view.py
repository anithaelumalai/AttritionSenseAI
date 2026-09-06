import streamlit as st
from utils.auth import get_user_id
from utils.data_loader import get_employee_by_id

def render_personal_info_view():
    emp_id = get_user_id()
    emp = get_employee_by_id(emp_id)
    
    st.markdown("""
        <div style="margin-bottom: 1.5rem;">
            <h2 style="color: #1e3a8a; margin: 0;">📊 My Personal Wellness & Engagement Space</h2>
            <p style="color: #64748b; margin: 0.2rem 0 0 0;">Empowering tips and healthy habit reflections tailored for your daily balance</p>
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("### 🌿 Daily Work-Life Check-In")
        wlb_val = emp.get("WorkLifeBalance", 3) if emp else 3
        
        if wlb_val <= 2:
            st.warning("⚠️ **Balance Alert:** Your recorded work-life balance suggests you may be running on low reserves. Remember that taking short daily pauses protects your creativity and long-term vitality.")
        else:
            st.success("✨ **Healthy Equilibrium:** Your recorded balance indicators look steady! Keep maintaining firm boundaries between deep focus and unwinding time.")

        st.markdown("#### 🎯 Daily Sustainable Work Checklist")
        st.checkbox("Set an explicit end-of-workday shutdown time", value=True)
        st.checkbox("Blocked off 30 mins for uninterrupted deep work", value=False)
        st.checkbox("Drank at least 2 liters of water throughout the day", value=False)
        st.checkbox("Took a brief 5-minute stretch away from the monitor", value=False)
        st.checkbox("Celebrated at least one small win today", value=False)

    with col2:
        st.markdown("### 💡 Career Growth & Reflection")
        st.markdown("""
            Building a fulfilling career is a marathon, not a sprint. Consider these reflective questions for your upcoming 1-on-1:
            
            1. **High-Energy Tasks:** Which projects over the last month felt most energizing?
            2. **Skill Curiosity:** What is one new technical or leadership capability you want to build this quarter?
            3. **Friction Reducers:** What is one routine operational blocker your team could simplify?
        """)
        
        st.markdown("#### 📞 Workplace Support Resources")
        st.info("""
            - **BuddyBot:** Available 24/7 in your sidebar for friendly chat and sounding-board reflections.
            - **Employee Assistance Program (EAP):** Confidential wellness consultations.
            - **HR Talent Development:** Open office hours every alternating Thursday.
        """)
