import streamlit as st
from utils.auth import get_user_id
from utils.data_loader import get_employee_by_id

def render_employee_dashboard():
    emp_id = get_user_id()
    emp_data = get_employee_by_id(emp_id)
    
    dept = emp_data.get("Department", "General") if emp_data else "General"
    role = emp_data.get("JobRole", "Team Member") if emp_data else "Team Member"
    
    st.markdown(f"""
        <div style="background: linear-gradient(135deg, #1e3a8a 0%, #0284c7 100%); padding: 1.8rem; border-radius: 12px; color: white; margin-bottom: 2rem;">
            <h1 style="margin: 0; font-size: 2rem;">Welcome Back, Employee #{emp_id}! 👋</h1>
            <p style="margin: 0.5rem 0 0 0; opacity: 0.9; font-size: 1.1rem;">{role} • {dept} Department</p>
            <p style="margin: 0.5rem 0 0 0; font-size: 0.95rem; opacity: 0.8;">Your personal workplace wellness and engagement sanctuary. Everything here is for your support and relaxation.</p>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### 🌟 Choose Your Activity Today")
    st.write("All activities are completely optional and self-paced. Take a moment for yourself:")
    
    c1, c2, c3 = st.columns(3)
    
    with c1:
        st.markdown("""
            <div style="border: 1px solid #e2e8f0; border-radius: 10px; padding: 1.3rem; background: white; text-align: center; min-height: 210px; height: auto; display: flex; flex-direction: column; justify-content: space-between; margin-bottom: 0.6rem;">
                <div>
                    <div style="font-size: 2.6rem; margin-bottom: 0.4rem;">🤖</div>
                    <h3 style="color: #1e3a8a; margin: 0; font-size: 1.2rem;">BuddyBot</h3>
                    <p style="color: #64748b; font-size: 0.9rem; margin-top: 0.4rem;">
                        Friendly conversation, workplace reflection, de-stressing, and supportive dialogue. Completely private.
                    </p>
                </div>
            </div>
        """, unsafe_allow_html=True)
        if st.button("Open BuddyBot 💬", key="btn_dash_buddybot", use_container_width=True, type="primary"):
            st.session_state.active_page = "buddybot"
            st.rerun()

    with c2:
        st.markdown("""
            <div style="border: 1px solid #e2e8f0; border-radius: 10px; padding: 1.3rem; background: white; text-align: center; min-height: 210px; height: auto; display: flex; flex-direction: column; justify-content: space-between; margin-bottom: 0.6rem;">
                <div>
                    <div style="font-size: 2.6rem; margin-bottom: 0.4rem;">🎮</div>
                    <h3 style="color: #1e3a8a; margin: 0; font-size: 1.2rem;">Mini Games</h3>
                    <p style="color: #64748b; font-size: 0.9rem; margin-top: 0.4rem;">
                        Take a quick, guilt-free mental break with Memory Match, guided breathing, and word scramble puzzles.
                    </p>
                </div>
            </div>
        """, unsafe_allow_html=True)
        if st.button("Play Mini Games 🎯", key="btn_dash_games", use_container_width=True):
            st.session_state.active_page = "games"
            st.rerun()

    with c3:
        st.markdown("""
            <div style="border: 1px solid #e2e8f0; border-radius: 10px; padding: 1.3rem; background: white; text-align: center; min-height: 210px; height: auto; display: flex; flex-direction: column; justify-content: space-between; margin-bottom: 0.6rem;">
                <div>
                    <div style="font-size: 2.6rem; margin-bottom: 0.4rem;">💬</div>
                    <h3 style="color: #1e3a8a; margin: 0; font-size: 1.2rem;">Employee Feedback</h3>
                    <p style="color: #64748b; font-size: 0.9rem; margin-top: 0.4rem;">
                        Share your authentic workplace experience with HR. Option to submit completely anonymously.
                    </p>
                </div>
            </div>
        """, unsafe_allow_html=True)
        if st.button("Share Feedback 📝", key="btn_dash_feedback", use_container_width=True):
            st.session_state.active_page = "feedback"
            st.rerun()

    st.markdown("---")
    
    # Quick Profile Snapshot
    st.markdown("### 📋 Quick Profile Overview")
    col_a, col_b, col_c, col_d = st.columns(4)
    with col_a:
        st.metric("Years at Company", f"{emp_data.get('YearsAtCompany', 0)} years")
    with col_b:
        st.metric("Work-Life Balance", f"{emp_data.get('WorkLifeBalance', 3)} / 4")
    with col_c:
        st.metric("Job Satisfaction", f"{emp_data.get('JobSatisfaction', 3)} / 4")
    with col_d:
        st.metric("Job Level", f"Level {emp_data.get('JobLevel', 1)}")
        
    if st.button("View Full Profile Details →", key="btn_dash_profile"):
        st.session_state.active_page = "employee_profile"
        st.rerun()
