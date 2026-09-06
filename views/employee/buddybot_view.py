import streamlit as st
from utils.auth import get_user_id
from utils.chatbot import (
    get_buddybot_response,
    save_chat_message,
    get_employee_chat_history,
    clear_employee_chat_history,
    get_gemini_api_key
)

def render_buddybot_view():
    emp_id = get_user_id()
    has_api = bool(get_gemini_api_key())
    
    mode_badge = "⚡ Gemini Generative AI" if has_api else "🌿 Contextual Workplace Companion"
    mode_color = "#4338ca" if has_api else "#0284c7"
    mode_bg = "#eef2ff" if has_api else "#e0f2fe"
    
    st.markdown(f"""
        <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 1rem; flex-wrap: wrap; gap: 0.5rem;">
            <div>
                <h2 style="color: #1e3a8a; margin: 0;">🤖 BuddyBot — Your Workplace Companion</h2>
                <p style="color: #64748b; margin: 0.2rem 0 0 0;">A private, supportive sounding board for daily work life, reflection, and de-stressing</p>
            </div>
            <div style="display: flex; flex-wrap: wrap; gap: 0.5rem;">
                <span style="background: {mode_bg}; color: {mode_color}; padding: 0.4rem 0.8rem; border-radius: 20px; font-size: 0.8rem; font-weight: bold;">
                    {mode_badge}
                </span>
                <span style="background: #f0fdf4; color: #166534; padding: 0.4rem 0.8rem; border-radius: 20px; font-size: 0.8rem; font-weight: bold;">
                    🛡️ 100% Private to You
                </span>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    if not has_api:
        st.caption("ℹ️ *Operating in offline contextual companion mode. Context tracking and non-repetitive dialogue active. (To enable cloud generative AI, add GEMINI_API_KEY to .env or Streamlit secrets).*")
    
    st.info("🔒 **Privacy Guarantee:** Your conversations with BuddyBot belong entirely to you. HR personnel and managers cannot access, view, or monitor your private chat messages.")
    
    # Initialize or load session chat history
    if f"chat_history_{emp_id}" not in st.session_state:
        stored_history = get_employee_chat_history(emp_id)
        if stored_history:
            st.session_state[f"chat_history_{emp_id}"] = stored_history
        else:
            # Friendly opening message
            welcome_msg = (
                f"Hello! I'm BuddyBot, your personal workplace buddy. "
                f"Whether you want to talk about a challenging day, celebrate a win, brainstorm ways to handle meeting overload, "
                f"or just take a relaxing breather—I'm here for you. How are you feeling today?"
            )
            st.session_state[f"chat_history_{emp_id}"] = [
                {"role": "assistant", "content": welcome_msg, "time": ""}
            ]
            save_chat_message(emp_id, "buddybot", welcome_msg)

    # Action bar
    col_l, col_r = st.columns([4, 1])
    with col_r:
        if st.button("🗑️ Clear Chat", use_container_width=True, help="Erase your conversation history"):
            clear_employee_chat_history(emp_id)
            st.session_state[f"chat_history_{emp_id}"] = []
            st.rerun()

    # Display conversation messages
    chat_container = st.container()
    with chat_container:
        for message in st.session_state[f"chat_history_{emp_id}"]:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

    # Chat input
    if prompt := st.chat_input("Type a message to BuddyBot (e.g. 'I had a really tiring day at work')..."):
        # 1. Display user message
        st.session_state[f"chat_history_{emp_id}"].append({"role": "user", "content": prompt})
        save_chat_message(emp_id, "user", prompt)
        
        with st.chat_message("user"):
            st.markdown(prompt)
            
        # 2. Generate and display assistant response
        with st.chat_message("assistant"):
            with st.spinner("BuddyBot is thinking..."):
                response_text = get_buddybot_response(
                    prompt,
                    emp_id,
                    st.session_state[f"chat_history_{emp_id}"]
                )
                st.markdown(response_text)
                
        # Save assistant message
        st.session_state[f"chat_history_{emp_id}"].append({"role": "assistant", "content": response_text})
        save_chat_message(emp_id, "buddybot", response_text)
