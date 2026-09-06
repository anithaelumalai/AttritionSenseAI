import streamlit as st
from utils.auth import get_user_id
from utils.feedback import save_employee_feedback

def render_feedback_view():
    emp_id = get_user_id()
    
    st.markdown("""
        <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 1.5rem; flex-wrap: wrap; gap: 0.5rem;">
            <div>
                <h2 style="color: #1e3a8a; margin: 0;">💬 Employee Feedback & Voice</h2>
                <p style="color: #64748b; margin: 0.2rem 0 0 0;">Help leadership build a healthier, more supportive workplace culture</p>
            </div>
            <div style="background: #eef2ff; color: #4338ca; padding: 0.4rem 0.8rem; border-radius: 20px; font-size: 0.85rem; font-weight: bold;">
                📬 Direct HR Channel
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    st.write(
        "Please rate your workplace experience across the 8 key dimensions below. "
        "Your candid feedback helps HR identify organizational bottlenecks and provide positive improvements."
    )
    
    with st.form("employee_feedback_form"):
        st.markdown("#### 1. Core Experience Ratings (1 = Very Low / Dissatisfied, 5 = Excellent / Highly Satisfied)")
        
        c1, c2 = st.columns(2)
        with c1:
            q1 = st.slider("1. Overall Job Satisfaction", min_value=1, max_value=5, value=4, help="How content are you with your daily responsibilities?")
            q2 = st.slider("2. Work-Life Balance", min_value=1, max_value=5, value=3, help="Ability to balance professional duties with personal life")
            q3 = st.slider("3. Manager Support & Empathy", min_value=1, max_value=5, value=4, help="How supportive, communicative, and fair is your manager?")
            q4 = st.slider("4. Workload Manageability", min_value=1, max_value=5, value=3, help="Is your current workload reasonable and sustainable?")
        with c2:
            q5 = st.slider("5. Career Growth Opportunities", min_value=1, max_value=5, value=3, help="Opportunities for learning, promotions, and skill development")
            q6 = st.slider("6. Recognition & Appreciation", min_value=1, max_value=5, value=4, help="Feeling valued for your contributions and milestones")
            q7 = st.slider("7. Compensation & Benefits Satisfaction", min_value=1, max_value=5, value=3, help="Competitiveness and fairness of your total rewards")
            q8 = st.slider("8. Intention to Stay with Company", min_value=1, max_value=5, value=4, help="Likelihood of continuing your career here over the next 12 months")
            
        st.markdown("---")
        st.markdown("#### 2. Open Comments & Workplace Suggestions")
        comments = st.text_area(
            "What could we improve to make your work life better? (Optional)",
            placeholder="Share any thoughts on team culture, workload, flexibility, tools, or recognition...",
            height=120
        )
        
        st.markdown("---")
        st.markdown("#### 3. Privacy & Anonymity Preferences")
        is_anonymous = st.checkbox(
            "🔒 Submit Anonymously (Do NOT attach my Employee ID to this feedback)",
            value=False,
            help="When checked, HR will receive only the aggregate ratings and comments without any identifier."
        )
        
        if is_anonymous:
            st.caption("🛡️ Anonymity active: Your Employee ID will be stripped before submission.")
        else:
            st.caption(f"👤 Submitting as Employee ID #{emp_id}. HR will be able to follow up on your feedback directly.")
            
        submitted = st.form_submit_button("Submit Workplace Feedback", type="primary", use_container_width=True)
        
        if submitted:
            # Validate ratings
            ratings = [q1, q2, q3, q4, q5, q6, q7, q8]
            if not all(isinstance(r, int) and 1 <= r <= 5 for r in ratings):
                st.error("Please provide a valid rating between 1 and 5 for all categories.")
            else:
                feedback_payload = {
                    "employee_id": emp_id,
                    "is_anonymous": is_anonymous,
                    "job_satisfaction": q1,
                    "work_life_balance": q2,
                    "manager_support": q3,
                    "workload": q4,
                    "career_growth": q5,
                    "recognition": q6,
                    "compensation_satisfaction": q7,
                    "intention_to_stay": q8,
                    "comments": comments.strip() if comments else ""
                }
                
                with st.spinner("Submitting feedback and processing notification..."):
                    success, msg = save_employee_feedback(feedback_payload)
                    if success:
                        st.success("✅ Feedback submitted successfully.")
                        if "not configured" in msg.lower():
                            st.warning("Feedback saved successfully, but HR email notification is not configured.")
                        elif "failed" in msg.lower() or "could not be dispatched" in msg.lower():
                            st.warning(f"Feedback saved successfully, but {msg}")
                        else:
                            st.info(f"📧 {msg}")
                    else:
                        st.error(f"Failed to submit feedback: {msg}")
