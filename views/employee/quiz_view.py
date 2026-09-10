import streamlit as st
from utils.auth import get_user_id
from utils.quiz import (
    get_available_weeks,
    get_quiz_for_week,
    get_current_week_number,
    save_weekly_quiz_submission,
    get_employee_quiz_scores,
    get_employee_completed_weeks
)

def render_quiz_view():
    emp_id = get_user_id()
    
    st.markdown("""
        <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 1.2rem; flex-wrap: wrap; gap: 0.5rem;">
            <div>
                <h2 style="color: #1e3a8a; margin: 0; font-size: 1.7rem;">🧠 Weekend Professional & Mindful Quiz</h2>
                <p style="color: #64748b; margin: 0.2rem 0 0 0; font-size: 0.95rem;">Practical scenarios on communication, teamwork, problem-solving & sustainable balance</p>
            </div>
            <div style="background: #fdf2f8; color: #db2777; padding: 0.4rem 0.9rem; border-radius: 20px; font-size: 0.85rem; font-weight: bold;">
                🔒 Strictly Private to You
            </div>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("""
        <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-left: 4px solid #8b5cf6; padding: 0.9rem 1.1rem; border-radius: 8px; margin-bottom: 1.5rem;">
            <p style="margin: 0; color: #475569; font-size: 0.92rem; line-height: 1.4;">
                🛡️ <strong>100% Privacy Guarantee:</strong>
                Your weekly quiz answers and scores are <strong>strictly confidential to you</strong>.
                They are <em>never</em> shared with HR or managers, and are <em>never</em> used to evaluate employee performance, attrition risk, growth status, or recommendations.
            </p>
        </div>
    """, unsafe_allow_html=True)

    available_weeks = get_available_weeks()
    current_cal_week = get_current_week_number()
    completed_weeks = get_employee_completed_weeks(emp_id)

    # Week Selection Controls
    col_w1, col_w2 = st.columns([2, 1])
    with col_w1:
        week_labels = []
        for w in available_weeks:
            prefix = f"Week {w}"
            if w in completed_weeks:
                prev_score = completed_weeks[w]["score"]
                prev_tot = completed_weeks[w]["total_questions"]
                week_labels.append(f"{prefix} — Completed ({prev_score}/{prev_tot}) ✅")
            elif w == current_cal_week:
                week_labels.append(f"{prefix} — Current Week 🌟")
            else:
                week_labels.append(f"{prefix}")
                
        def format_week_choice(w: int) -> str:
            idx = available_weeks.index(w)
            return week_labels[idx]

        selected_week = st.selectbox(
            "Select Quiz Week:",
            options=available_weeks,
            index=available_weeks.index(current_cal_week) if current_cal_week in available_weeks else 0,
            format_func=format_week_choice,
            help="Every week features 10 fresh, practical scenario-based workplace questions."
        )

    with col_w2:
        if selected_week in completed_weeks:
            prior = completed_weeks[selected_week]
            st.caption(f"Completed on **{prior.get('quiz_date', 'Recently')[:10]}** with score **{prior.get('score')}/{prior.get('total_questions')}**")
            if st.button("Retake This Week's Quiz 🔄", key=f"btn_retake_w_{selected_week}", use_container_width=True):
                st.session_state[f"quiz_submitted_{emp_id}_w_{selected_week}"] = False
                st.rerun()

    quiz_package = get_quiz_for_week(selected_week)
    questions = quiz_package["questions"]
    total_q = len(questions)

    st.markdown(f"""
        <div style="background: white; border: 1px solid #e2e8f0; border-radius: 10px; padding: 1.2rem; margin-bottom: 1.5rem; box-shadow: 0 1px 3px rgba(0,0,0,0.03);">
            <h3 style="color: #1e3a8a; margin: 0 0 0.3rem 0; font-size: 1.25rem;">{quiz_package['title']}</h3>
            <p style="color: #64748b; margin: 0; font-size: 0.95rem;">{quiz_package['description']}</p>
        </div>
    """, unsafe_allow_html=True)

    submission_state_key = f"quiz_submitted_{emp_id}_w_{selected_week}"
    if submission_state_key not in st.session_state:
        st.session_state[submission_state_key] = False

    user_answers = {}
    
    # Render Quiz Form with 10 questions and interactive clues
    with st.form(f"weekly_quiz_form_w_{selected_week}"):
        for idx, q in enumerate(questions, 1):
            st.markdown(f"""
                <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 8px; padding: 1.2rem 1.4rem; margin-bottom: 1.2rem; box-shadow: 0 1px 2px rgba(0,0,0,0.04);">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.6rem;">
                        <span style="font-size: 0.85rem; font-weight: 700; color: #0284c7; text-transform: uppercase; letter-spacing: 0.05em;">Question {idx} of {total_q}</span>
                    </div>
                    <div style="font-size: 1.05rem; font-weight: 600; color: #0f172a; line-height: 1.45; margin-bottom: 0.8rem;">
                        {q['question']}
                    </div>
                </div>
            """, unsafe_allow_html=True)

            # Option selection
            ans = st.radio(
                label=f"q_label_{selected_week}_{q['id']}",
                options=q["options"],
                index=0,
                key=f"ans_w_{selected_week}_{q['id']}",
                label_visibility="collapsed"
            )
            user_answers[q["id"]] = ans

            # Interactive Clue Expander
            with st.expander(f"💡 Need a Clue for Question {idx}? (Click to reveal)", expanded=False):
                st.markdown(f"""
                    <div style="background: #fefce8; border-left: 3px solid #eab308; padding: 0.6rem 0.9rem; border-radius: 4px; font-size: 0.9rem; color: #713f12;">
                        <strong>Thinking Clue:</strong> {q['clue']}
                    </div>
                """, unsafe_allow_html=True)

            st.markdown("<div style='margin-bottom: 1.5rem;'></div>", unsafe_allow_html=True)

        submit_btn = st.form_submit_button(
            f"🎯 Submit Week {selected_week} Quiz Answers",
            type="primary",
            use_container_width=True
        )
        if submit_btn:
            st.session_state[submission_state_key] = True

    # Review & Score Screen
    if st.session_state[submission_state_key]:
        score = 0
        results_breakdown = []
        answers_dict = {}
        correct_dict = {}

        for q in questions:
            selected_text = user_answers.get(q["id"])
            correct_text = q["options"][q["answer_index"]]
            is_correct = (selected_text == correct_text)
            if is_correct:
                score += 1

            answers_dict[q["id"]] = selected_text
            correct_dict[q["id"]] = correct_text

            results_breakdown.append({
                "id": q["id"],
                "question": q["question"],
                "selected": selected_text,
                "correct": correct_text,
                "is_correct": is_correct,
                "explanation": q["explanation"]
            })

        # Persist score and answers safely to database
        save_weekly_quiz_submission(
            employee_id=emp_id,
            week=selected_week,
            score=score,
            total_questions=total_q,
            answers=answers_dict,
            correct_answers=correct_dict,
            category=quiz_package["title"]
        )

        pct = (score / total_q) * 100
        if pct >= 80:
            badge = "🌟 Exceptional! You demonstrate exemplary workplace judgment, communication, and emotional agility."
            badge_color = "#10b981"
        elif pct >= 60:
            badge = "🌿 Solid effort! Strong grasp of collaborative problem-solving and healthy work habits."
            badge_color = "#0284c7"
        else:
            badge = "💡 Valuable learning experience! Reflect on the explanations below to refine your teamwork toolkit."
            badge_color = "#f59e0b"

        score_card_html = (
            f'<div style="background: white; border: 2px solid {badge_color}; border-radius: 12px; padding: 1.8rem; text-align: center; margin: 1.8rem 0; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);">'
            f'<h3 style="color: #1e293b; margin: 0 0 0.4rem 0;">Week {selected_week} Quiz Complete!</h3>'
            f'<div style="font-size: 2.5rem; font-weight: 800; color: {badge_color}; margin-bottom: 0.5rem;">'
            f'{score} / {total_q} ({pct:.0f}%)'
            f'</div>'
            f'<p style="color: #475569; font-weight: 600; font-size: 1.05rem; margin: 0;">{badge}</p>'
            f'</div>'
        )
        st.markdown(score_card_html, unsafe_allow_html=True)

        st.markdown("### 📋 Detailed Question Review & Key Takeaways")
        for idx, res in enumerate(results_breakdown, 1):
            if res["is_correct"]:
                st.success(f"**Question {idx}:** {res['question']}\n\n✅ **Your Answer:** {res['selected']}\n\n💡 **Practical Takeaway:** {res['explanation']}")
            else:
                st.warning(f"**Question {idx}:** {res['question']}\n\n❌ **Your Choice:** {res['selected']}\n\n✅ **Best Practice:** {res['correct']}\n\n💡 **Practical Takeaway:** {res['explanation']}")

    # Past Quiz History
    all_past_scores = get_employee_quiz_scores(emp_id)
    if all_past_scores:
        st.markdown("---")
        st.markdown("#### 📜 Your Private Quiz History")
        for item in all_past_scores[:5]:
            wk = item.get("week", 1)
            st.caption(f"🗓️ Week {wk} — {item.get('quiz_date', 'Recently')[:10]} | Score: **{item.get('score')}/{item.get('total_questions')}** ({item.get('category', 'General')})")
