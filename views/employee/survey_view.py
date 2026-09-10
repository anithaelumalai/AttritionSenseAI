import streamlit as st
from utils.auth import get_user_id
from utils.survey import save_survey, get_latest_survey

def render_survey_view():
    emp_id = get_user_id()
    
    st.markdown("""
        <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 1.5rem; flex-wrap: wrap; gap: 0.5rem;">
            <div>
                <h2 style="color: #1e3a8a; margin: 0;">📋 Optional Workplace Survey</h2>
                <p style="color: #64748b; margin: 0.2rem 0 0 0;">Help shape our team environment — completely voluntary & confidential</p>
            </div>
            <div style="background: #ecfdf5; color: #047857; padding: 0.4rem 0.8rem; border-radius: 20px; font-size: 0.85rem; font-weight: bold;">
                🌿 100% Optional
            </div>
        </div>
    """, unsafe_allow_html=True)

    st.info(
        "💡 **Note:** This survey is entirely voluntary. You may skip individual questions or skip the entire survey at any time. "
        "Unanswered fields are preserved as blank and will never negatively affect your standing or evaluations."
    )

    latest = get_latest_survey(emp_id)
    if latest:
        if latest.get("is_skipped") == 1:
            st.caption(f"ℹ️ You previously chose to skip this survey on {latest.get('created_at', 'recently')}. You can submit an update anytime.")
        else:
            st.caption(f"✅ Last response recorded on {latest.get('created_at', 'recently')}. You can submit updated answers below.")

    rating_options = [
        "Leave blank (No rating)",
        "1 - Significantly Needs Improvement",
        "2 - Below Expectations",
        "3 - Meets Expectations / Satisfactory",
        "4 - Exceeds Expectations / Strong",
        "5 - Exceptional / Best in Class"
    ]

    def parse_rating(selection: str):
        if not selection or selection.startswith("Leave blank"):
            return None
        return int(selection[0])

    with st.form("workplace_optional_survey_form"):
        st.markdown("#### Workplace Dimensions")
        
        c1, c2 = st.columns(2)
        with c1:
            q_env = st.selectbox(
                "1. Physical & Remote Work Environment",
                options=rating_options,
                index=0,
                help="Comfort, ergonomics, and work setup"
            )
            q_collab = st.selectbox(
                "2. Team Collaboration & Communication",
                options=rating_options,
                index=0,
                help="Team synergy, transparency, and cross-functional support"
            )
            q_culture = st.selectbox(
                "3. Culture & Values Alignment",
                options=rating_options,
                index=0,
                help="Sense of belonging and alignment with organizational mission"
            )

        with c2:
            q_growth = st.selectbox(
                "4. Learning & Growth Opportunities",
                options=rating_options,
                index=0,
                help="Access to training, mentorship, and career pathways"
            )
            q_tools = st.selectbox(
                "5. Tools, Technology & Resources",
                options=rating_options,
                index=0,
                help="Adequacy of software, hardware, and operational tools"
            )

        st.markdown("---")
        st.markdown("#### Open Ideas & Feedback (Optional)")
        suggestions = st.text_area(
            "What would make your workday even better?",
            placeholder="Share thoughts on workflows, wellness programs, tools, or culture...",
            height=100
        )

        b_col1, b_col2 = st.columns([1, 1])
        with b_col1:
            submit_btn = st.form_submit_button("📤 Submit Survey", type="primary", use_container_width=True)
        with b_col2:
            skip_btn = st.form_submit_button("⏭️ Skip Survey", type="secondary", use_container_width=True)

        if submit_btn:
            payload = {
                "work_environment": parse_rating(q_env),
                "team_collaboration": parse_rating(q_collab),
                "culture_alignment": parse_rating(q_culture),
                "growth_opportunities": parse_rating(q_growth),
                "tools_resources": parse_rating(q_tools),
                "suggestions": suggestions.strip() if suggestions.strip() else None
            }
            save_survey(emp_id, payload, is_skipped=False)
            st.success("✅ Survey submitted successfully! Thank you for sharing your valuable perspectives.")
            st.rerun()

        if skip_btn:
            save_survey(emp_id, {}, is_skipped=True)
            st.info("⏭️ Survey marked as skipped. You can revisit and submit at any time.")
            st.rerun()
