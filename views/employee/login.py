import streamlit as st
from utils.auth import authenticate_employee, login_session
from utils.data_loader import get_employee_by_id

def render_employee_login():
    st.markdown("""
        <div style="text-align: center; margin-bottom: 2rem;">
            <div style="font-size: 3rem;">👤</div>
            <h2 style="color: #1e3a8a; margin-bottom: 0.2rem;">Employee Portal Login</h2>
            <p style="color: #64748b;">Access your personal workplace companion, BuddyBot, relaxation games, and feedback</p>
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.form("employee_login_form"):
            st.markdown("### Enter Credentials")
            emp_id = st.text_input("Employee ID / Number", placeholder="e.g. 1, 2, 4, 5...", help="Enter your numerical Employee ID")
            password = st.text_input("Password", type="password", placeholder="Enter your password", help="Default password is emp123")
            
            submitted = st.form_submit_button("Log In to Employee Portal", use_container_width=True, type="primary")
            
            if submitted:
                if not emp_id.strip():
                    st.error("Please enter your Employee ID.")
                elif not password:
                    st.error("Please enter your password.")
                else:
                    success, user_dict, message = authenticate_employee(emp_id, password)
                    if success:
                        emp_data = get_employee_by_id(emp_id)
                        login_session(user_dict, employee_data=emp_data)
                        st.success("Login successful! Redirecting to Employee Portal...")
                        st.rerun()
                    else:
                        st.error(message)
                        
        st.info("💡 **Quick Test Hint:** Use Employee ID `1` (or `2`, `4`, `5`) with password `emp123`.")
        
        if st.button("← Back to Role Selection", use_container_width=True):
            st.session_state.active_page = "landing"
            st.rerun()
