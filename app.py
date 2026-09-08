import streamlit as st
import os
import sys

# Ensure project root is in sys.path
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from utils.database import init_database, seed_users_if_needed
from utils.auth import init_session, is_authenticated, is_employee, is_hr, logout_session, get_user_id

# 1. Page Configuration
st.set_page_config(
    page_title="AttritionSense AI",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Global Styles
st.markdown("""
    <style>
        .main-header {
            font-size: 1.8rem;
            font-weight: 700;
            color: #1e3a8a;
            margin-bottom: 0.5rem;
        }
        .stButton>button, .stDownloadButton>button {
            border-radius: 6px;
            font-weight: 500;
            min-height: 44px;
        }
        .css-1d391kg, .css-12oz5g7 {
            padding-top: 2rem;
        }
        [data-testid="stSidebar"] {
            background-color: #f8fafc;
            border-right: 1px solid #e2e8f0;
        }

        /* Responsive Layout & Container Rules */
        html, body, [data-testid="stAppViewContainer"] {
            max-width: 100vw !important;
            overflow-x: hidden !important;
        }

        /* Prevent unwanted horizontal overflow on dataframes & plots */
        .stPlotlyChart, div[data-testid="stDataFrame"], .stTable {
            max-width: 100% !important;
            overflow-x: auto !important;
            -webkit-overflow-scrolling: touch;
        }

        /* Mobile Adjustments (iPhone, Android, Tablets <= 768px) */
        @media (max-width: 768px) {
            /* Maximize usable horizontal width */
            .main .block-container {
                padding-left: 0.75rem !important;
                padding-right: 0.75rem !important;
                padding-top: 1rem !important;
                padding-bottom: 2rem !important;
                max-width: 100% !important;
            }

            /* Responsive stacking for multi-column grids */
            [data-testid="stHorizontalBlock"] {
                flex-wrap: wrap !important;
                gap: 0.5rem !important;
            }
            [data-testid="stHorizontalBlock"] > div[data-testid="column"] {
                min-width: 260px !important;
                flex: 1 1 260px !important;
            }
            /* Hide empty spacer columns on mobile screens */
            div[data-testid="column"]:empty {
                display: none !important;
            }

            /* Touch target sizes & input ergonomics */
            .stButton>button, .stDownloadButton>button {
                min-height: 48px !important;
                font-size: 1rem !important;
                width: 100% !important;
            }
            input[type="text"], input[type="password"], textarea, select {
                font-size: 16px !important; /* Prevents auto-zoom in iOS Safari */
            }

            /* Sliders full width without horizontal clipping */
            .stSlider {
                padding-left: 0.2rem !important;
                padding-right: 0.2rem !important;
            }

            /* Responsive typography scaling */
            h1 { font-size: 1.6rem !important; }
            h2 { font-size: 1.35rem !important; }
            h3 { font-size: 1.15rem !important; }

            /* Metrics cards */
            [data-testid="stMetric"] {
                padding: 0.5rem !important;
            }
        }
    </style>
""", unsafe_allow_html=True)

# 2. Database & Data Setup on Startup
def startup_system():
    init_database()
    seed_users_if_needed()
    return True

startup_system()

# 3. Session State Initialization
init_session()

# Import view renderers
from views.employee.login import render_employee_login
from views.employee.dashboard import render_employee_dashboard
from views.employee.profile import render_employee_profile
from views.employee.buddybot_view import render_buddybot_view
from views.employee.games_view import render_games_view
from views.employee.feedback_view import render_feedback_view
from views.employee.personal_info_view import render_personal_info_view

from views.hr.login import render_hr_login
from views.hr.dashboard import render_hr_dashboard
from views.hr.search_prediction import render_employee_search_prediction
from views.hr.analytics_view import render_hr_analytics
from views.hr.feedback_analytics import render_feedback_analytics
from views.hr.history_view import render_prediction_history
from views.hr.reports_view import render_hr_reports
from views.hr.about_view import render_about_view

# ==============================================================================
# LANDING PAGE (WHEN NOT AUTHENTICATED)
# ==============================================================================
def render_landing():
    st.markdown("""
        <div style="text-align: center; padding: 2rem 1rem 1.5rem 1rem;">
            <div style="font-size: 3.2rem; margin-bottom: 0.5rem;">🏢</div>
            <h1 style="color: #1e3a8a; font-size: 2.5rem; font-weight: 800; margin-bottom: 0.5rem;">
                AttritionSense AI
            </h1>
            <p style="color: #475569; font-size: 1.15rem; max-width: 750px; margin: 0 auto 1.5rem auto;">
                Intelligent Employee Attrition Prediction & Retention Recommendation System
            </p>
            <div style="display: inline-block; background: #e0f2fe; color: #0284c7; padding: 0.4rem 1.2rem; border-radius: 20px; font-weight: 600; font-size: 0.85rem;">
                Dual-Role Enterprise Architecture • 100% Role-Based Access Control
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
            <div style="border: 2px solid #e2e8f0; border-radius: 12px; padding: 1.8rem; background: white; text-align: center; min-height: 280px; height: auto; display: flex; flex-direction: column; justify-content: space-between; margin-bottom: 0.8rem;">
                <div>
                    <div style="font-size: 3rem; margin-bottom: 0.5rem;">👤</div>
                    <h2 style="color: #1e3a8a; margin: 0;">Employee Portal</h2>
                    <p style="color: #64748b; font-size: 0.95rem; margin-top: 0.8rem;">
                        Your confidential workplace companion. Access your personal profile, chat with <b>BuddyBot</b>, enjoy relaxing <b>Mini Games</b>, and share feedback with leadership.
                    </p>
                </div>
            </div>
        """, unsafe_allow_html=True)
        if st.button("Enter Employee Portal Login →", key="btn_portal_emp", use_container_width=True, type="primary"):
            st.session_state.active_page = "employee_login"
            st.rerun()

    with col2:
        st.markdown("""
            <div style="border: 2px solid #e2e8f0; border-radius: 12px; padding: 1.8rem; background: white; text-align: center; min-height: 280px; height: auto; display: flex; flex-direction: column; justify-content: space-between; margin-bottom: 0.8rem;">
                <div>
                    <div style="font-size: 3rem; margin-bottom: 0.5rem;">🛡️</div>
                    <h2 style="color: #1e3a8a; margin: 0;">HR & Leadership Portal</h2>
                    <p style="color: #64748b; font-size: 0.95rem; margin-top: 0.8rem;">
                        Authorized executive suite. Automated employee search, <b>Random Forest ML</b> prediction, risk scoring, prescriptive retention recommendations, deep analytics, and <b>PDF reports</b>.
                    </p>
                </div>
            </div>
        """, unsafe_allow_html=True)
        if st.button("Enter HR & Leadership Login →", key="btn_portal_hr", use_container_width=True):
            st.session_state.active_page = "hr_login"
            st.rerun()

    st.markdown("---")
    st.markdown("""
        <div style="text-align: center; color: #94a3b8; font-size: 0.85rem;">
            AttritionSense AI Platform • Powered by Scikit-learn, Random Forest & Streamlit • Strict Enterprise Privacy Safeguards
        </div>
    """, unsafe_allow_html=True)

# ==============================================================================
# MAIN ROUTING ENGINE (STRICT ROLE-BASED ACCESS CONTROL)
# ==============================================================================

if not is_authenticated():
    # Hide sidebar for unauthenticated users
    st.markdown("<style>[data-testid='stSidebar'] {display: none;}</style>", unsafe_allow_html=True)
    
    if st.session_state.active_page == "employee_login":
        render_employee_login()
    elif st.session_state.active_page == "hr_login":
        render_hr_login()
    else:
        render_landing()

elif is_employee():
    # --------------------------------------------------------------------------
    # EMPLOYEE SIDEBAR NAVIGATION
    # --------------------------------------------------------------------------
    emp_id = get_user_id()
    
    with st.sidebar:
        st.markdown(f"""
            <div style="padding: 0.8rem 0; border-bottom: 1px solid #e2e8f0; margin-bottom: 1rem;">
                <h3 style="color: #1e3a8a; margin: 0; font-size: 1.3rem;">AttritionSense AI</h3>
                <div style="font-size: 0.85rem; color: #0284c7; font-weight: 600;">👤 Employee Portal</div>
                <div style="font-size: 0.8rem; color: #64748b;">Logged in: <b>Employee #{emp_id}</b></div>
            </div>
        """, unsafe_allow_html=True)
        
        emp_nav_options = {
            "employee_dashboard": "🏠 My Dashboard",
            "employee_profile": "👤 My Profile",
            "buddybot": "🤖 BuddyBot",
            "games": "🎮 Mini Games",
            "feedback": "💬 Employee Feedback",
            "personal_info": "📊 My Personal Information"
        }
        
        # Ensure active_page is an allowed employee view
        if st.session_state.active_page not in emp_nav_options:
            st.session_state.active_page = "employee_dashboard"
            
        current_index = list(emp_nav_options.keys()).index(st.session_state.active_page)
        
        selected_nav = st.radio(
            "Navigation",
            options=list(emp_nav_options.keys()),
            format_func=lambda k: emp_nav_options[k],
            index=current_index,
            label_visibility="collapsed"
        )
        
        if selected_nav != st.session_state.active_page:
            st.session_state.active_page = selected_nav
            st.rerun()
            
        st.markdown("---")
        if st.button("🚪 Logout", use_container_width=True):
            logout_session()
            st.rerun()
            
    # Render Protected Employee Views
    if st.session_state.active_page == "employee_dashboard":
        render_employee_dashboard()
    elif st.session_state.active_page == "employee_profile":
        render_employee_profile()
    elif st.session_state.active_page == "buddybot":
        render_buddybot_view()
    elif st.session_state.active_page == "games":
        render_games_view()
    elif st.session_state.active_page == "feedback":
        render_feedback_view()
    elif st.session_state.active_page == "personal_info":
        render_personal_info_view()

elif is_hr():
    # --------------------------------------------------------------------------
    # HR SIDEBAR NAVIGATION
    # --------------------------------------------------------------------------
    hr_user = get_user_id()
    
    with st.sidebar:
        st.markdown(f"""
            <div style="padding: 0.8rem 0; border-bottom: 1px solid #e2e8f0; margin-bottom: 1rem;">
                <h3 style="color: #1e3a8a; margin: 0; font-size: 1.3rem;">AttritionSense AI</h3>
                <div style="font-size: 0.85rem; color: #b91c1c; font-weight: 600;">🛡️ HR & Executive Suite</div>
                <div style="font-size: 0.8rem; color: #64748b;">Authorized User: <b>{hr_user}</b></div>
            </div>
        """, unsafe_allow_html=True)
        
        hr_nav_options = {
            "hr_dashboard": "🏠 HR Dashboard",
            "employee_search_prediction": "🔎 Employee Search & Prediction",
            "analytics": "📊 Analytics",
            "feedback_analytics": "💬 Feedback Analytics",
            "prediction_history": "📜 Prediction History",
            "reports": "📄 Reports",
            "about": "ℹ️ About"
        }
        
        # Ensure active_page is an allowed HR view
        if st.session_state.active_page not in hr_nav_options:
            st.session_state.active_page = "hr_dashboard"
            
        current_index = list(hr_nav_options.keys()).index(st.session_state.active_page)
        
        selected_nav = st.radio(
            "Navigation",
            options=list(hr_nav_options.keys()),
            format_func=lambda k: hr_nav_options[k],
            index=current_index,
            label_visibility="collapsed"
        )
        
        if selected_nav != st.session_state.active_page:
            st.session_state.active_page = selected_nav
            st.rerun()
            
        st.markdown("---")
        if st.button("🚪 Logout", use_container_width=True):
            logout_session()
            st.rerun()

    # Render Protected HR Views
    if st.session_state.active_page == "hr_dashboard":
        render_hr_dashboard()
    elif st.session_state.active_page == "employee_search_prediction":
        render_employee_search_prediction()
    elif st.session_state.active_page == "analytics":
        render_hr_analytics()
    elif st.session_state.active_page == "feedback_analytics":
        render_feedback_analytics()
    elif st.session_state.active_page == "prediction_history":
        render_prediction_history()
    elif st.session_state.active_page == "reports":
        render_hr_reports()
    elif st.session_state.active_page == "about":
        render_about_view()

else:
    # Fallback safety guard for invalid session states
    logout_session()
    st.rerun()
