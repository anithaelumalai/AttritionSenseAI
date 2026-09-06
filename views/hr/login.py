import streamlit as st
from utils.auth import authenticate_hr, login_session

def render_hr_login():
    st.markdown("""
        <div style="text-align: center; margin-bottom: 2rem;">
            <div style="font-size: 3rem;">🛡️</div>
            <h2 style="color: #1e3a8a; margin-bottom: 0.2rem;">HR & Leadership Portal Login</h2>
            <p style="color: #64748b;">Authorized administrative access to predictive analytics, workforce risk radar, and reports</p>
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.form("hr_login_form"):
            st.markdown("### HR Credentials")
            username = st.text_input("HR Username / ID", placeholder="e.g. admin or hr_manager", help="Enter authorized HR administrator username")
            password = st.text_input("Password", type="password", placeholder="Enter your password", help="Default password is admin123")
            
            submitted = st.form_submit_button("Log In to HR Portal", use_container_width=True, type="primary")
            
            if submitted:
                if not username.strip():
                    st.error("Please enter your HR Username.")
                elif not password:
                    st.error("Please enter your password.")
                else:
                    success, user_dict, message = authenticate_hr(username, password)
                    if success:
                        login_session(user_dict)
                        st.success("Authorization confirmed! Redirecting to HR Dashboard...")
                        st.rerun()
                    else:
                        st.error(message)
                        
        st.info("💡 **Pre-seeded Admin Access:** Username `admin` | Password `admin123` (or `hr_manager` / `hr123`).")
        
        if st.button("← Back to Role Selection", use_container_width=True):
            st.session_state.active_page = "landing"
            st.rerun()
