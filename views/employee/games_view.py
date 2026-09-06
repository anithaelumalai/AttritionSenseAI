import streamlit as st
import random
import time

def render_games_view():
    st.markdown("""
        <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 1.5rem; flex-wrap: wrap; gap: 0.5rem;">
            <div>
                <h2 style="color: #1e3a8a; margin: 0;">🎮 Wellness Break — Mini Games</h2>
                <p style="color: #64748b; margin: 0.2rem 0 0 0;">Quick, refreshing mental breaks to recharge focus and decompress</p>
            </div>
            <div style="background: #fdf2f8; color: #9d174d; padding: 0.4rem 0.8rem; border-radius: 20px; font-size: 0.85rem; font-weight: bold;">
                ☕ Guilt-Free Rest Zone
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    st.info("🧘 **Wellness Notice:** These mini-games are provided strictly for your personal relaxation, short pauses, and mental wellness. Game performance and participation are never tracked, graded, or linked to HR evaluations or attrition risk scores.")

    game_tab1, game_tab2, game_tab3 = st.tabs([
        "🃏 Memory Card Match",
        "🫁 Focus Breathing Sanctuary",
        "🔤 Workplace Word Scramble"
    ])

    # -------------------------------------------------------------
    # GAME 1: Memory Card Match
    # -------------------------------------------------------------
    with game_tab1:
        st.markdown("### 🃏 Memory Card Match")
        st.write("Flip pairs to find all matching wellness icons. Match all 6 pairs in as few moves as possible!")
        
        # Initialize memory game state
        if "mem_deck" not in st.session_state:
            icons = ["🌱", "☕", "🎯", "🚀", "💡", "🧘"]
            deck = icons * 2
            random.shuffle(deck)
            st.session_state.mem_deck = deck
            st.session_state.mem_revealed = [False] * 12
            st.session_state.mem_matched = [False] * 12
            st.session_state.mem_flipped = []  # Indices of currently flipped cards
            st.session_state.mem_moves = 0
            
        c_left, c_right = st.columns([3, 1])
        with c_left:
            st.write(f"**Moves:** {st.session_state.mem_moves} | **Matched:** {sum(st.session_state.mem_matched)//2} / 6 pairs")
        with c_right:
            if st.button("🔄 Restart Game", key="btn_mem_restart"):
                icons = ["🌱", "☕", "🎯", "🚀", "💡", "🧘"]
                deck = icons * 2
                random.shuffle(deck)
                st.session_state.mem_deck = deck
                st.session_state.mem_revealed = [False] * 12
                st.session_state.mem_matched = [False] * 12
                st.session_state.mem_flipped = []
                st.session_state.mem_moves = 0
                st.rerun()

        # Render 4x3 card grid
        cols_per_row = 4
        for r in range(3):
            cols = st.columns(cols_per_row)
            for c in range(cols_per_row):
                idx = r * cols_per_row + c
                is_matched = st.session_state.mem_matched[idx]
                is_flipped = st.session_state.mem_revealed[idx] or is_matched
                
                label = st.session_state.mem_deck[idx] if is_flipped else "❓"
                disabled = is_matched or (idx in st.session_state.mem_flipped) or len(st.session_state.mem_flipped) >= 2
                
                if cols[c].button(label, key=f"card_{idx}", disabled=disabled, use_container_width=True):
                    st.session_state.mem_revealed[idx] = True
                    st.session_state.mem_flipped.append(idx)
                    
                    if len(st.session_state.mem_flipped) == 2:
                        st.session_state.mem_moves += 1
                        idx1, idx2 = st.session_state.mem_flipped
                        if st.session_state.mem_deck[idx1] == st.session_state.mem_deck[idx2]:
                            st.session_state.mem_matched[idx1] = True
                            st.session_state.mem_matched[idx2] = True
                            st.session_state.mem_flipped = []
                        st.rerun()

        # Check if 2 mismatch cards are open
        if len(st.session_state.mem_flipped) == 2:
            idx1, idx2 = st.session_state.mem_flipped
            if st.session_state.mem_deck[idx1] != st.session_state.mem_deck[idx2]:
                st.warning("Not a match! Click anywhere or press Next to flip back.")
                if st.button("Flip Back Cards ↩️", key="btn_flip_back", type="primary"):
                    st.session_state.mem_revealed[idx1] = False
                    st.session_state.mem_revealed[idx2] = False
                    st.session_state.mem_flipped = []
                    st.rerun()

        # Win condition
        if all(st.session_state.mem_matched):
            st.balloons()
            st.success(f"🎉 Fantastic memory! You matched all pairs in {st.session_state.mem_moves} moves!")

    # -------------------------------------------------------------
    # GAME 2: Focus Breathing Sanctuary
    # -------------------------------------------------------------
    with game_tab2:
        st.markdown("### 🫁 4-7-8 Focus Breathing Sanctuary")
        st.write("The 4-7-8 breathing technique activates your parasympathetic nervous system, instantly lowering heart rate and soothing tension.")
        
        b_col1, b_col2 = st.columns([2, 1])
        with b_col1:
            st.markdown("""
                1. **Inhale quietly through nose:** 4 seconds
                2. **Hold your breath gently:** 7 seconds
                3. **Exhale completely through mouth:** 8 seconds
            """)
            
            if "breath_stage" not in st.session_state:
                st.session_state.breath_stage = 0
                st.session_state.breath_cycle = 0

            stage_names = [
                ("Ready to Begin", "Click the button below to start your calming cycle.", "#64748b"),
                ("Inhale... (4s)", "Breathe in deeply and quietly through your nose. Fill your lungs.", "#0284c7"),
                ("Hold... (7s)", "Hold your breath gently. Relax your shoulders and jaw.", "#7c3aed"),
                ("Exhale... (8s)", "Release all air through your mouth with a soft whoosh sound.", "#059669")
            ]
            
            name, desc, color = stage_names[st.session_state.breath_stage]
            
            st.markdown(f"""
                <div style="background: {color}15; border: 2px solid {color}; border-radius: 12px; padding: 2rem; text-align: center; margin: 1rem 0;">
                    <h2 style="color: {color}; margin: 0;">{name}</h2>
                    <p style="color: #334155; font-size: 1.1rem; margin-top: 0.5rem;">{desc}</p>
                    <p style="font-size: 0.9rem; color: #64748b;">Completed Cycles: <b>{st.session_state.breath_cycle}</b></p>
                </div>
            """, unsafe_allow_html=True)
            
            btn_label = "Start Inhale (4s)" if st.session_state.breath_stage == 0 else "Next Breath Phase →"
            if st.button(btn_label, key="btn_next_breath", type="primary", use_container_width=True):
                if st.session_state.breath_stage == 0:
                    st.session_state.breath_stage = 1
                elif st.session_state.breath_stage == 1:
                    st.session_state.breath_stage = 2
                elif st.session_state.breath_stage == 2:
                    st.session_state.breath_stage = 3
                else:
                    st.session_state.breath_stage = 1
                    st.session_state.breath_cycle += 1
                st.rerun()

        with b_col2:
            st.markdown("#### 💡 Quick Wellness Tips")
            st.markdown("""
                - Drink a warm glass of water 💧
                - Roll your shoulders backward 3 times 🙆
                - Look away from the monitor at a distant object for 20 seconds 👀
                - Stand up and stretch your arms overhead ✨
            """)

    # -------------------------------------------------------------
    # GAME 3: Workplace Word Scramble
    # -------------------------------------------------------------
    with game_tab3:
        st.markdown("### 🔤 Workplace Word Scramble")
        st.write("Unscramble the letters to reveal inspiring workplace wellness and teamwork words.")
        
        WORDS = [
            {"word": "BALANCE", "hint": "Equilibrium between your work tasks and personal life"},
            {"word": "WELLNESS", "hint": "The state of being in good physical and mental health"},
            {"word": "CREATIVITY", "hint": "The use of imagination to create new ideas"},
            {"word": "RESILIENCE", "hint": "The capacity to recover quickly from workplace challenges"},
            {"word": "TEAMWORK", "hint": "Collaborative effort of a group to achieve a common goal"},
            {"word": "HARMONY", "hint": "Peaceful and cooperative atmosphere among peers"},
            {"word": "MINDSET", "hint": "An established set of attitudes held by someone"}
        ]
        
        if "scramble_idx" not in st.session_state:
            st.session_state.scramble_idx = random.randint(0, len(WORDS) - 1)
            st.session_state.scramble_score = 0
            st.session_state.scramble_show_hint = False

        cur_item = WORDS[st.session_state.scramble_idx]
        cur_word = cur_item["word"]
        
        # Scramble word letters deterministically for current word
        scrambled_letters = list(cur_word)
        random.seed(cur_word)
        random.shuffle(scrambled_letters)
        scrambled = "  ".join(scrambled_letters)
        random.seed() # reset seed
        
        st.markdown(f"""
            <div style="background: #f8fafc; border: 1px solid #cbd5e1; border-radius: 10px; padding: 1.5rem; text-align: center; margin-bottom: 1rem;">
                <p style="color: #64748b; margin: 0; font-size: 0.9rem;">Unscramble the letters:</p>
                <h1 style="color: #1e3a8a; letter-spacing: 0.3rem; margin: 0.5rem 0;">{scrambled}</h1>
            </div>
        """, unsafe_allow_html=True)
        
        guess = st.text_input("Your Answer:", key=f"guess_input_{st.session_state.scramble_idx}", placeholder="Type word here...").strip().upper()
        
        col_g1, col_g2, col_g3 = st.columns(3)
        with col_g1:
            if st.button("Check Word ✨", key="btn_check_scramble", type="primary", use_container_width=True):
                if guess == cur_word:
                    st.success(f"🎉 Correct! The word is **{cur_word}**!")
                    st.session_state.scramble_score += 1
                    st.session_state.scramble_show_hint = False
                    st.session_state.scramble_idx = (st.session_state.scramble_idx + 1) % len(WORDS)
                    st.rerun()
                else:
                    st.error("Not quite! Try again or check the hint below.")
                    
        with col_g2:
            if st.button("Need a Hint? 💡", key="btn_hint", use_container_width=True):
                st.session_state.scramble_show_hint = True
                
        with col_g3:
            if st.button("Next Word ⏭️", key="btn_skip_word", use_container_width=True):
                st.session_state.scramble_idx = (st.session_state.scramble_idx + 1) % len(WORDS)
                st.session_state.scramble_show_hint = False
                st.rerun()

        if st.session_state.scramble_show_hint:
            st.info(f"💡 **Hint:** {cur_item['hint']}")
            
        st.write(f"**Words Solved this Session:** {st.session_state.scramble_score}")
