import streamlit as st
import random

def render_games_view():
    st.markdown("""
        <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 1.5rem; flex-wrap: wrap; gap: 0.5rem;">
            <div>
                <h2 style="color: #1e3a8a; margin: 0;">🎮 Mind-Free Games — Mental Relaxation Lounge</h2>
                <p style="color: #64748b; margin: 0.2rem 0 0 0;">Gentle cognitive breaks designed to refresh focus, calm anxiety, and decompress</p>
            </div>
            <div style="background: #f0fdf4; color: #15803d; padding: 0.4rem 0.8rem; border-radius: 20px; font-size: 0.85rem; font-weight: bold;">
                ☕ Personal Wellness Lounge
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
        <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-left: 4px solid #10b981; padding: 0.9rem; border-radius: 8px; margin-bottom: 1.5rem;">
            <p style="margin: 0; color: #475569; font-size: 0.95rem;">
                🌿 <strong>100% Private Wellness Activity:</strong>
                Mind-Free games are purely for your personal enjoyment and cognitive relaxation. 
                Your game interactions and results are strictly private, <strong>never shared with HR</strong>, and <strong>never used in any AI model predictions or evaluations</strong>.
            </p>
        </div>
    """, unsafe_allow_html=True)

    game_tab1, game_tab2, game_tab3 = st.tabs([
        "🧩 ZenCode: Coding Puzzle",
        "🪨 Digital Zen Garden",
        "🌈 ColorFlow: Harmony Puzzle"
    ])

    # =========================================================================
    # GAME 1: ZenCode — Coding Relaxation Puzzle
    # =========================================================================
    with game_tab1:
        st.markdown("### 🧩 ZenCode — Coding Relaxation Puzzle")
        st.write(
            "Solve beginner-friendly, mindful code completion puzzles. "
            "Select the most peaceful and collaborative code snippet to complete the routine."
        )

        ZEN_LEVELS = [
            {
                "level": 1,
                "title": "Finding Balance",
                "code_before": "def find_inner_balance(daily_work):\n    if daily_work.completed:\n        return ",
                "code_after": "\n    else:\n        return take_deep_breath()",
                "options": ["rest_and_recharge()", "panic_and_overtime()", "infinite_worry_loop()", "ignore_sleep()"],
                "correct_idx": 0,
                "zen_message": "✨ Excellent! Rest is the true foundation of sustainable excellence."
            },
            {
                "level": 2,
                "title": "Handling Cognitive Clutter",
                "code_before": "while mind.is_overwhelmed():\n    mind.",
                "code_after": "\n    mind.focus_on_one_step_at_a_time()",
                "options": ["pause_and_breathe()", "run_faster_until_crash()", "bottle_up_stress()", "skip_lunch()"],
                "correct_idx": 0,
                "zen_message": "🌸 Beautiful! A brief intentional pause resets cognitive clarity."
            },
            {
                "level": 3,
                "title": "Collaborative Synergy",
                "code_before": "if unexpected_blocker_occurs:\n    team.",
                "code_after": "\n    team.resolve_with_empathy()",
                "options": ["solve_and_support_together()", "blame_individual_contributor()", "hide_the_defect()", "escalate_in_anger()"],
                "correct_idx": 0,
                "zen_message": "🤝 Wonderful! Psychological safety builds unbeatable teams."
            },
            {
                "level": 4,
                "title": "Daily Milestone Reflection",
                "code_before": "for completed_task in today.efforts:\n    ",
                "code_after": "\n    self_esteem += 1",
                "options": ["celebrate_small_wins(completed_task)", "demand_immediate_perfection()", "downplay_achievements()", "erase_from_memory()"],
                "correct_idx": 0,
                "zen_message": "🌱 Outstanding! Acknowledging small wins fuels lasting intrinsic motivation."
            },
            {
                "level": 5,
                "title": "The Master Programmer Mindset",
                "code_before": "def sustainable_career():\n    skills = continuous_curiosity()\n    wellbeing = ",
                "code_after": "\n    return skills + wellbeing",
                "options": ["unconditional_self_compassion()", "grinding_without_boundaries()", "comparison_with_others()", "imposter_syndrome()"],
                "correct_idx": 0,
                "zen_message": "🧘 Master Level Reached! Self-compassion is the ultimate key to resilience."
            }
        ]

        if "zencode_level" not in st.session_state:
            st.session_state.zencode_level = 0
            st.session_state.zencode_completed = False

        cur_lvl = min(st.session_state.zencode_level, len(ZEN_LEVELS) - 1)
        puzzle = ZEN_LEVELS[cur_lvl]

        col_z_top1, col_z_top2 = st.columns([3, 1])
        with col_z_top1:
            st.markdown(f"**Level {puzzle['level']} / {len(ZEN_LEVELS)}:** *{puzzle['title']}*")
        with col_z_top2:
            if st.button("🔄 Restart Puzzles", key="btn_restart_zencode"):
                st.session_state.zencode_level = 0
                st.session_state.zencode_completed = False
                st.rerun()

        # Display code snippet
        code_placeholder = f"{puzzle['code_before']} [ ? SELECT CHOICE BELOW ? ] {puzzle['code_after']}"
        st.code(code_placeholder, language="python")

        choice = st.radio(
            "Choose the mindful code completion:",
            options=puzzle["options"],
            key=f"zen_radio_{cur_lvl}"
        )

        b_check, b_next = st.columns(2)
        with b_check:
            if st.button("✨ Run Mindful Code", key=f"btn_run_zen_{cur_lvl}", type="primary", use_container_width=True):
                if choice == puzzle["options"][puzzle["correct_idx"]]:
                    st.success(puzzle["zen_message"])
                    completed_code = f"{puzzle['code_before']}{choice}{puzzle['code_after']}"
                    st.code(completed_code, language="python")
                    
                    if cur_lvl + 1 < len(ZEN_LEVELS):
                        st.session_state.zencode_level += 1
                        st.info("Level complete! Click Next Level below or choose next puzzle.")
                    else:
                        st.session_state.zencode_completed = True
                        st.balloons()
                        st.success("🎉 You have mastered all 5 ZenCode levels! Your mind is harmonious and focused.")
                else:
                    st.warning("That approach sounds tense! Consider the more mindful, compassionate option.")

        with b_next:
            if cur_lvl + 1 < len(ZEN_LEVELS):
                if st.button("Next Level ⏭️", key=f"btn_next_zen_{cur_lvl}", use_container_width=True):
                    st.session_state.zencode_level = min(st.session_state.zencode_level + 1, len(ZEN_LEVELS) - 1)
                    st.rerun()

    # =========================================================================
    # GAME 2: Digital Zen Garden
    # =========================================================================
    with game_tab2:
        st.markdown("### 🪨 Digital Zen Garden")
        st.write("Craft your peaceful Japanese dry landscape garden (*karesansui*). Arrange river stones, bamboo, and blossoms on raked sand.")

        if "zen_garden_grid" not in st.session_state:
            # 4x4 serene sand garden initialized with ripples
            st.session_state.zen_garden_grid = [
                ["≋", "≋", "≋", "≋"],
                ["≋", "🌸", "≋", "≋"],
                ["≋", "≋", "🪨", "≋"],
                ["≋", "≋", "≋", "🎋"]
            ]
            st.session_state.zen_sand_pattern = "≋"

        ELEMENT_MAP = {
            "🌸 Cherry Blossom": "🌸",
            "🪨 River Stone": "🪨",
            "🎋 Bamboo Stalk": "🎋",
            "🏮 Stone Lantern": "🏮",
            "🐟 Koi Pond": "🐟",
            "🪴 Bonsai Pine": "🪴",
            "〰️ Raked Sand (Waves)": "〰️",
            "≋ Raked Sand (Ripples)": "≋",
            "⚪ Smooth Sand": "⚪"
        }

        col_elem, col_act = st.columns([2, 1])
        with col_elem:
            selected_item = st.selectbox(
                "Select item or sand pattern to place:",
                options=list(ELEMENT_MAP.keys()),
                index=0
            )
        with col_act:
            if st.button("🧹 Rake Clean Canvas", key="btn_rake_clean", use_container_width=True):
                st.session_state.zen_garden_grid = [["≋"] * 4 for _ in range(4)]
                st.rerun()

        st.caption("Click any garden square to place your chosen element:")
        symbol_to_place = ELEMENT_MAP[selected_item]

        # Render interactive 4x4 garden grid
        for row_i in range(4):
            cols = st.columns(4)
            for col_i in range(4):
                cur_symbol = st.session_state.zen_garden_grid[row_i][col_i]
                if cols[col_i].button(
                    cur_symbol,
                    key=f"garden_{row_i}_{col_i}",
                    use_container_width=True
                ):
                    st.session_state.zen_garden_grid[row_i][col_i] = symbol_to_place
                    st.rerun()

        st.markdown("""
            <div style="background: #fdfbf7; border: 1px solid #e7e5e4; border-radius: 10px; padding: 1rem; margin-top: 1.5rem; text-align: center;">
                <p style="color: #78716c; font-style: italic; margin: 0; font-size: 0.95rem;">
                    "Quiet the mind, and the soul will speak." — Traditional Zen Proverb
                </p>
            </div>
        """, unsafe_allow_html=True)

    # =========================================================================
    # GAME 3: ColorFlow — Harmony Relaxation Puzzle
    # =========================================================================
    with game_tab3:
        st.markdown("### 🌈 ColorFlow — Harmony Relaxation Puzzle")
        st.write("Reorder soothing color swatches to create seamless gradient transitions. Pure visual harmony to ease eye fatigue.")

        COLOR_THEMES = [
            {
                "name": "Sunset Serenity",
                "palette": ["#FF7E5F", "#FEB47B", "#FFECCC", "#A8E6CF"],
                "labels": ["Deep Coral", "Warm Peach", "Sunlit Amber", "Sage Mint"]
            },
            {
                "name": "Ocean Deep Sanctuary",
                "palette": ["#0F172A", "#0369A1", "#38BDF8", "#E0F2FE"],
                "labels": ["Midnight Abyss", "Deep Cobalt", "Azure Wave", "Sea Foam"]
            },
            {
                "name": "Lavender Twilight",
                "palette": ["#3B0764", "#7C3AED", "#C084FC", "#F3E8FF"],
                "labels": ["Royal Violet", "Amethyst Glow", "Soft Lilac", "Evening Mist"]
            },
            {
                "name": "Forest Canopy",
                "palette": ["#064E3B", "#059669", "#34D399", "#ECFDF5"],
                "labels": ["Deep Pine", "Emerald Moss", "Spring Fern", "Morning Dew"]
            }
        ]

        if "colorflow_theme_idx" not in st.session_state:
            st.session_state.colorflow_theme_idx = 0
            st.session_state.colorflow_order = [2, 0, 3, 1]  # Shuffled initial order

        cur_theme = COLOR_THEMES[st.session_state.colorflow_theme_idx]
        correct_order = [0, 1, 2, 3]

        col_t1, col_t2 = st.columns([3, 1])
        with col_t1:
            st.markdown(f"**Palette:** *{cur_theme['name']}*")
        with col_t2:
            if st.button("Next Palette 🎨", key="btn_next_palette"):
                st.session_state.colorflow_theme_idx = (st.session_state.colorflow_theme_idx + 1) % len(COLOR_THEMES)
                st.session_state.colorflow_order = [3, 1, 0, 2]
                st.rerun()

        st.caption("Click 'Shift Right ➡️' on any swatch to swap its position until the colors blend in smooth gradient order:")

        # Render current arrangement
        cols_cf = st.columns(4)
        for slot_idx, color_pos in enumerate(st.session_state.colorflow_order):
            hex_code = cur_theme["palette"][color_pos]
            lbl = cur_theme["labels"][color_pos]
            
            with cols_cf[slot_idx]:
                st.markdown(f"""
                    <div style="background-color: {hex_code}; height: 80px; border-radius: 8px; border: 2px solid white; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); margin-bottom: 0.5rem;"></div>
                    <div style="text-align: center; font-size: 0.8rem; font-weight: 600; color: #334155; margin-bottom: 0.5rem;">{lbl}</div>
                """, unsafe_allow_html=True)
                
                if st.button("Shift ➡️", key=f"btn_swap_{slot_idx}", use_container_width=True):
                    # Swap with neighbor to the right (wrap around)
                    next_slot = (slot_idx + 1) % 4
                    arr = st.session_state.colorflow_order.copy()
                    arr[slot_idx], arr[next_slot] = arr[next_slot], arr[slot_idx]
                    st.session_state.colorflow_order = arr
                    st.rerun()

        # Check for harmony
        if st.session_state.colorflow_order == correct_order or st.session_state.colorflow_order == correct_order[::-1]:
            st.success("✨ Harmonious Flow Achieved! The colors are in perfect soothing gradient equilibrium.")
        else:
            st.info("Arrange from deepest shade to lightest tint (or vice-versa) to complete the flow.")
