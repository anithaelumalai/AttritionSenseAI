import streamlit as st
from utils.auth import get_user_id
from utils.exit_feedback import save_exit_feedback, get_exit_feedback_for_employee

def render_exit_feedback_view():
    emp_id = get_user_id()
    
    st.markdown("""
        <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 1.5rem; flex-wrap: wrap; gap: 0.5rem;">
            <div>
                <h2 style="color: #1e3a8a; margin: 0;">🚪 Optional Exit Feedback</h2>
                <p style="color: #64748b; margin: 0.2rem 0 0 0;">Confidential reflections and suggestions for career transitions</p>
            </div>
            <div style="background: #f1f5f9; color: #475569; padding: 0.4rem 0.8rem; border-radius: 20px; font-size: 0.85rem; font-weight: bold;">
                🤝 Optional & Respectful
            </div>
        </div>
    """, unsafe_allow_html=True)

    st.info(
        "💡 **Optional Process:** Filling out exit feedback is entirely voluntary. "
        "Your perspectives help improve workplace culture and support future team members. "
        "You may skip this form entirely or omit any question without hesitation."
    )

    prior_entry = get_exit_feedback_for_employee(emp_id)
    if prior_entry:
        if prior_entry.get("is_skipped") == 1:
            st.caption(f"ℹ️ You previously chose to skip this form on {prior_entry.get('created_at', 'recently')}.")
        else:
            st.caption(f"✅ Exit feedback was submitted on {prior_entry.get('created_at', 'recently')}.")

    rating_options = [
        "Leave blank (No rating)",
        "1 - Significantly Below Expectations",
        "2 - Below Expectations",
        "3 - Met Expectations / Satisfactory",
        "4 - Above Expectations / Fulfilling",
        "5 - Outstanding / Exceptional"
    ]

    def parse_rating(selection: str):
        if not selection or selection.startswith("Leave blank"):
            return None
        return int(selection[0])

    reason_options = [
        "Leave blank (Unspecified)",
        "Career Opportunity & Professional Growth",
        "Compensation, Equity & Benefits",
        "Work-Life Balance & Schedule Flexibility",
        "Relocation / Personal Life Change",
        "Organizational / Team Alignment",
        "Entrepreneurship / Further Education",
        "Other"
    ]

    handover_options = [
        "Leave blank (Unspecified)",
        "Completed & Fully Documented",
        "In Progress / Currently Transitioning",
        "Scheduled with Successor / Team Lead",
        "Not Applicable"
    ]

    with st.form("exit_feedback_form"):
        st.markdown("#### 1. Transition Details")
        c1, c2 = st.columns(2)
        with c1:
            q_reason = st.selectbox("Primary factor prompting transition:", options=reason_options, index=0)
            q_exp = st.selectbox("Overall company experience rating:", options=rating_options, index=0)
        with c2:
            q_rec = st.selectbox("Likelihood to recommend company to a peer:", options=rating_options, index=0)
            q_handover = st.selectbox("Handover / knowledge transfer status:", options=handover_options, index=0)

        st.markdown("---")
        st.markdown("#### 2. Confidential Departing Thoughts & Suggestions")
        detailed_feedback = st.text_area(
            "What advice or constructive recommendations would you leave for the leadership team?",
            placeholder="Share honest thoughts on team dynamics, management, tools, or recognition...",
            height=120
        )

        b_col1, b_col2 = st.columns([1, 1])
        with b_col1:
            submit_btn = st.form_submit_button("📤 Submit Exit Feedback", type="primary", use_container_width=True)
        with b_col2:
            skip_btn = st.form_submit_button("⏭️ Skip Exit Feedback", type="secondary", use_container_width=True)

        if submit_btn:
            payload = {
                "primary_reason": None if q_reason.startswith("Leave blank") else q_reason,
                "experience_rating": parse_rating(q_exp),
                "recommend_company": parse_rating(q_rec),
                "handover_status": None if q_handover.startswith("Leave blank") else q_handover,
                "detailed_feedback": detailed_feedback.strip() if detailed_feedback.strip() else None
            }
            save_exit_feedback(emp_id, payload, is_skipped=False)
            st.success("✅ Exit feedback submitted safely. We sincerely thank you for your contributions and wish you the best in your next chapter!")
            st.rerun()

        if skip_btn:
            save_exit_feedback(emp_id, {}, is_skipped=True)
            st.info("⏭️ Exit feedback marked as skipped. Thank you!")
            st.rerun()
