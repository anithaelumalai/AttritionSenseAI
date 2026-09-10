import streamlit as st
from utils.auth import get_user_id
from utils.quiz import get_weekend_quiz_questions, save_quiz_score, get_employee_quiz_scores

def render_quiz_view():
    emp_id = get_user_id()
    
    st.markdown("""
        <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 1.5rem; flex-wrap: wrap; gap: 0.5rem;">
            <div>
                <h2 style="color: #1e3a8a; margin: 0;">🧠 Weekend Mind & Ergonomics Quiz</h2>
                <p style="color: #64748b; margin: 0.2rem 0 0 0;">Fun weekend trivia to boost workplace mindfulness & well-being</p>
            </div>
            <div style="background: #fdf2f8; color: #db2777; padding: 0.4rem 0.8rem; border-radius: 20px; font-size: 0.85rem; font-weight: bold;">
                🔒 Strictly Private to You
            </div>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("""
        <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-left: 4px solid #8b5cf6; padding: 1rem; border-radius: 8px; margin-bottom: 1.5rem;">
            <p style="margin: 0; color: #475569; font-size: 0.95rem;">
                🛡️ <strong>Privacy Protection Guarantee:</strong>
                Your answers and quiz scores are <strong>strictly private</strong>. 
                They are <em>never</em> shared with HR, managers, or colleagues, and are <em>never</em> used in AI attrition risk or growth status evaluations.
            </p>
        </div>
    """, unsafe_allow_html=True)

    questions = get_weekend_quiz_questions()
    
    # State tracking for quiz results
    state_key = f"quiz_submitted_{emp_id}"
    if state_key not in st.session_state:
        st.session_state[state_key] = False

    user_answers = {}
    with st.form("weekend_quiz_form"):
        for q in questions:
            st.markdown(f"**Question {q['id']}:** {q['question']}")
            ans = st.radio(
                label=f"q_{q['id']}_label",
                options=q["options"],
                index=0,
                key=f"quiz_q_{q['id']}",
                label_visibility="collapsed"
            )
            user_answers[q["id"]] = ans
            st.markdown("<div style='margin-bottom: 1rem;'></div>", unsafe_allow_html=True)

        submit_btn = st.form_submit_button("🎯 Submit Quiz Answers", type="primary", use_container_width=True)
        if submit_btn:
            st.session_state[state_key] = True

    if st.session_state[state_key]:
        score = 0
        total = len(questions)
        results_breakdown = []

        for q in questions:
            selected_text = user_answers.get(q["id"])
            correct_text = q["options"][q["answer_index"]]
            is_correct = (selected_text == correct_text)
            if is_correct:
                score += 1
            results_breakdown.append({
                "question": q["question"],
                "selected": selected_text,
                "correct": correct_text,
                "is_correct": is_correct,
                "explanation": q["explanation"]
            })

        # Save to database
        save_quiz_score(emp_id, score, total)

        pct = (score / total) * 100
        if pct >= 80:
            badge = "🌟 Outstanding! You have great mastery of cognitive ergonomics."
            badge_color = "#10b981"
        elif pct >= 60:
            badge = "🌿 Good job! Healthy habits build sustainable careers."
            badge_color = "#3b82f6"
        else:
            badge = "💡 Great learning effort! Every mindful practice counts."
            badge_color = "#f59e0b"

        st.markdown(f"""
            <div style="background: white; border: 2px solid {badge_color}; border-radius: 12px; padding: 1.5rem; text-align: center; margin: 1.5rem 0;">
                <h3 style="color: #1e293b; margin: 0 0 0.5rem 0;">Quiz Completed!</h3>
                <div style="font-size: 2.2rem; font-weight: 800; color: {badge_color}; margin-bottom: 0.5rem;">
                    {score} / {total} ({pct:.0f}%)
                </div>
                <p style="color: #475569; font-weight: 600; margin: 0;">{badge}</p>
            </div>
        """, unsafe_allow_html=True)

        st.markdown("### 📋 Review Answers & Explanations")
        for idx, res in enumerate(results_breakdown, 1):
            if res["is_correct"]:
                st.success(f"**Q{idx}: {res['question']}**\n\n✅ Your answer: *{res['selected']}*\n\n💡 {res['explanation']}")
            else:
                st.warning(f"**Q{idx}: {res['question']}**\n\n❌ Your answer: *{res['selected']}*\n\n✅ Correct answer: *{res['correct']}*\n\n💡 {res['explanation']}")

    # Past attempts
    past_scores = get_employee_quiz_scores(emp_id)
    if past_scores:
        st.markdown("---")
        st.markdown("#### 📜 Your Past Quiz History (Private)")
        for item in past_scores[:3]:
            st.caption(f"🗓️ {item.get('quiz_date', 'Recently')} — Score: {item.get('score')}/{item.get('total_questions')} ({item.get('category')})")
