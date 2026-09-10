import streamlit as st
import streamlit.components.v1 as components

def render_games_view():
    st.markdown("""
        <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 1.5rem; flex-wrap: wrap; gap: 0.5rem;">
            <div>
                <h2 style="color: #1e3a8a; margin: 0; font-size: 1.7rem;">🎮 Mind-Free Games — Mental Relaxation Lounge</h2>
                <p style="color: #64748b; margin: 0.2rem 0 0 0; font-size: 0.95rem;">Gentle cognitive breaks designed to refresh focus, calm anxiety, and decompress</p>
            </div>
            <div style="background: #f0fdf4; color: #15803d; padding: 0.4rem 0.9rem; border-radius: 20px; font-size: 0.85rem; font-weight: bold;">
                ☕ Personal Wellness Lounge
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
        <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-left: 4px solid #10b981; padding: 0.9rem 1.1rem; border-radius: 8px; margin-bottom: 1.5rem;">
            <p style="margin: 0; color: #475569; font-size: 0.92rem; line-height: 1.4;">
                🌿 <strong>100% Private Wellness Activity:</strong>
                Mind-Free games are provided strictly for your personal relaxation.
                Your game interactions, time spent, and results are <strong>never shared with HR</strong>, <strong>never stored in performance records</strong>, and <strong>never affect AI attrition risk or growth status evaluations</strong>.
            </p>
        </div>
    """, unsafe_allow_html=True)

    game_tab1, game_tab2, game_tab3 = st.tabs([
        "🧩 ZenCode: Coding Puzzle",
        "🌊 Focus Flow",
        "🔮 Calm Puzzle Room"
    ])

    # =========================================================================
    # GAME 1: ZenCode — Coding Relaxation Puzzle (Preserved as requested)
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
    # GAME 2: Focus Flow (Brand-New Interactive Relaxation Canvas)
    # =========================================================================
    with game_tab2:
        st.markdown("### 🌊 Focus Flow — Ambient Calming Canvas")
        st.write(
            "Gently tap or click the floating luminous energy orbs to release soothing ripples and peaceful affirmations. "
            "No scores, no timer, no competition — simply pause and reset your mental rhythm."
        )

        # Embedded Large Interactive HTML5 / Canvas Engine
        focus_flow_html = """
        <!DOCTYPE html>
        <html>
        <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            * { box-sizing: border-box; margin: 0; padding: 0; user-select: none; }
            body {
                background: transparent;
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
                overflow: hidden;
            }
            .canvas-container {
                position: relative;
                width: 100%;
                height: 480px;
                border-radius: 16px;
                background: radial-gradient(circle at 50% 50%, #0f172a 0%, #020617 100%);
                box-shadow: 0 10px 25px -5px rgba(0,0,0,0.3), inset 0 0 20px rgba(56, 189, 248, 0.1);
                border: 1px solid rgba(56, 189, 248, 0.25);
                overflow: hidden;
                cursor: pointer;
            }
            canvas {
                display: block;
                width: 100%;
                height: 100%;
            }
            .ui-overlay {
                position: absolute;
                top: 14px;
                left: 18px;
                right: 18px;
                display: flex;
                justify-content: space-between;
                align-items: center;
                pointer-events: none;
            }
            .counter-badge {
                background: rgba(15, 23, 42, 0.75);
                backdrop-filter: blur(8px);
                border: 1px solid rgba(56, 189, 248, 0.3);
                color: #e0f2fe;
                padding: 6px 14px;
                border-radius: 20px;
                font-size: 0.88rem;
                font-weight: 600;
                display: flex;
                align-items: center;
                gap: 6px;
            }
            .action-btn {
                pointer-events: auto;
                background: rgba(56, 189, 248, 0.15);
                border: 1px solid rgba(56, 189, 248, 0.4);
                color: #7dd3fc;
                padding: 6px 14px;
                border-radius: 20px;
                font-size: 0.85rem;
                font-weight: 600;
                cursor: pointer;
                transition: all 0.2s ease;
            }
            .action-btn:hover {
                background: rgba(56, 189, 248, 0.3);
                color: #ffffff;
            }
            .bottom-hint {
                position: absolute;
                bottom: 12px;
                width: 100%;
                text-align: center;
                color: #64748b;
                font-size: 0.82rem;
                pointer-events: none;
                letter-spacing: 0.02em;
            }
        </style>
        </head>
        <body>
        <div class="canvas-container" id="container">
            <div class="ui-overlay">
                <div class="counter-badge">
                    <span>✨ Mindful Pulses:</span>
                    <span id="pulseCount" style="color: #38bdf8;">0</span>
                </div>
                <button class="action-btn" id="resetBtn">Add More Orbs 💫</button>
            </div>
            <canvas id="flowCanvas"></canvas>
            <div class="bottom-hint">Touch or click anywhere on the canvas to cast harmonic waves</div>
        </div>

        <script>
            const canvas = document.getElementById('flowCanvas');
            const ctx = canvas.getContext('2d');
            const container = document.getElementById('container');
            const counterEl = document.getElementById('pulseCount');
            const resetBtn = document.getElementById('resetBtn');

            let width = canvas.width = container.clientWidth;
            let height = canvas.height = container.clientHeight;

            window.addEventListener('resize', () => {
                width = canvas.width = container.clientWidth;
                height = canvas.height = container.clientHeight;
            });

            let pulses = 0;
            const PALETTES = [
                { base: '#38bdf8', glow: 'rgba(56, 189, 248, 0.45)' },
                { base: '#818cf8', glow: 'rgba(129, 140, 248, 0.45)' },
                { base: '#34d399', glow: 'rgba(52, 211, 153, 0.45)' },
                { base: '#f472b6', glow: 'rgba(244, 114, 182, 0.45)' },
                { base: '#fbbf24', glow: 'rgba(251, 191, 36, 0.45)' },
                { base: '#a78bfa', glow: 'rgba(167, 139, 250, 0.45)' }
            ];

            const WORDS = ["Inner Peace 🌿", "Deep Breath 🫁", "Clarity 💎", "Gratitude ✨", "Focus 🎯", "Harmony 🌸", "Release 🕊️", "Presence 🌊"];

            class Orb {
                constructor(x, y) {
                    this.x = x || Math.random() * (width - 100) + 50;
                    this.y = y || Math.random() * (height - 100) + 50;
                    this.radius = Math.random() * 12 + 20;
                    this.vx = (Math.random() - 0.5) * 1.1;
                    this.vy = (Math.random() - 0.5) * 1.1;
                    this.palette = PALETTES[Math.floor(Math.random() * PALETTES.length)];
                    this.phase = Math.random() * Math.PI * 2;
                }
                update() {
                    this.phase += 0.03;
                    this.x += this.vx;
                    this.y += this.vy;
                    if (this.x < this.radius || this.x > width - this.radius) this.vx *= -1;
                    if (this.y < this.radius || this.y > height - this.radius) this.vy *= -1;
                }
                draw() {
                    const currentRadius = this.radius + Math.sin(this.phase) * 3;
                    ctx.save();
                    ctx.shadowBlur = 24;
                    ctx.shadowColor = this.palette.glow;
                    ctx.beginPath();
                    ctx.arc(this.x, this.y, currentRadius, 0, Math.PI * 2);
                    const grad = ctx.createRadialGradient(this.x, this.y, 2, this.x, this.y, currentRadius);
                    grad.addColorStop(0, '#ffffff');
                    grad.addColorStop(0.4, this.palette.base);
                    grad.addColorStop(1, 'rgba(15, 23, 42, 0.2)');
                    ctx.fillStyle = grad;
                    ctx.fill();
                    ctx.restore();
                }
            }

            class Ripple {
                constructor(x, y, color) {
                    this.x = x;
                    this.y = y;
                    this.radius = 5;
                    this.maxRadius = Math.random() * 40 + 70;
                    this.alpha = 1.0;
                    this.color = color || '#38bdf8';
                }
                update() {
                    this.radius += 2.2;
                    this.alpha -= 0.024;
                }
                draw() {
                    if (this.alpha <= 0) return;
                    ctx.save();
                    ctx.beginPath();
                    ctx.arc(this.x, this.y, this.radius, 0, Math.PI * 2);
                    ctx.strokeStyle = this.color;
                    ctx.globalAlpha = Math.max(0, this.alpha);
                    ctx.lineWidth = 2.5;
                    ctx.stroke();
                    ctx.restore();
                }
            }

            class FloatingText {
                constructor(x, y, text) {
                    this.x = x;
                    this.y = y;
                    this.text = text;
                    this.alpha = 1.0;
                    this.vy = -1.2;
                }
                update() {
                    this.y += this.vy;
                    this.alpha -= 0.016;
                }
                draw() {
                    if (this.alpha <= 0) return;
                    ctx.save();
                    ctx.font = 'bold 14px sans-serif';
                    ctx.fillStyle = '#f8fafc';
                    ctx.globalAlpha = Math.max(0, this.alpha);
                    ctx.shadowColor = 'rgba(56, 189, 248, 0.8)';
                    ctx.shadowBlur = 10;
                    ctx.textAlign = 'center';
                    ctx.fillText(this.text, this.x, this.y);
                    ctx.restore();
                }
            }

            let orbs = [];
            let ripples = [];
            let texts = [];

            for (let i = 0; i < 7; i++) {
                orbs.push(new Orb());
            }

            function handleInteraction(clientX, clientY) {
                const rect = canvas.getBoundingClientRect();
                const x = clientX - rect.left;
                const y = clientY - rect.top;

                let hitOrb = false;
                for (let i = orbs.length - 1; i >= 0; i--) {
                    const o = orbs[i];
                    const dist = Math.hypot(o.x - x, o.y - y);
                    if (dist < o.radius + 15) {
                        hitOrb = true;
                        ripples.push(new Ripple(o.x, o.y, o.palette.base));
                        ripples.push(new Ripple(o.x, o.y, '#ffffff'));
                        const word = WORDS[Math.floor(Math.random() * WORDS.length)];
                        texts.push(new FloatingText(o.x, o.y - 15, word));
                        orbs.splice(i, 1);
                        orbs.push(new Orb());
                        pulses++;
                        counterEl.innerText = pulses;
                        break;
                    }
                }

                if (!hitOrb) {
                    ripples.push(new Ripple(x, y, '#38bdf8'));
                }
            }

            container.addEventListener('pointerdown', (e) => {
                if (e.target === resetBtn) return;
                handleInteraction(e.clientX, e.clientY);
            });

            resetBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                for (let i = 0; i < 3; i++) {
                    orbs.push(new Orb());
                }
            });

            function animate() {
                ctx.clearRect(0, 0, width, height);

                // Draw background ambient connection threads
                ctx.save();
                for (let i = 0; i < orbs.length; i++) {
                    for (let j = i + 1; j < orbs.length; j++) {
                        const dist = Math.hypot(orbs[i].x - orbs[j].x, orbs[i].y - orbs[j].y);
                        if (dist < 130) {
                            ctx.beginPath();
                            ctx.moveTo(orbs[i].x, orbs[i].y);
                            ctx.lineTo(orbs[j].x, orbs[j].y);
                            ctx.strokeStyle = 'rgba(56, 189, 248,' + (1 - dist / 130) * 0.2 + ')';
                            ctx.lineWidth = 1;
                            ctx.stroke();
                        }
                    }
                }
                ctx.restore();

                // Update & draw ripples
                for (let i = ripples.length - 1; i >= 0; i--) {
                    ripples[i].update();
                    ripples[i].draw();
                    if (ripples[i].alpha <= 0) ripples.splice(i, 1);
                }

                // Update & draw orbs
                for (const orb of orbs) {
                    orb.update();
                    orb.draw();
                }

                // Update & draw texts
                for (let i = texts.length - 1; i >= 0; i--) {
                    texts[i].update();
                    texts[i].draw();
                    if (texts[i].alpha <= 0) texts.splice(i, 1);
                }

                requestAnimationFrame(animate);
            }
            animate();
        </script>
        </body>
        </html>
        """
        components.html(focus_flow_html, height=510, scrolling=False)

    # =========================================================================
    # GAME 3: Calm Puzzle Room (Brand-New Visual Alignment Mini-Puzzles)
    # =========================================================================
    with game_tab3:
        st.markdown("### 🔮 Calm Puzzle Room — Sacred Mandala Alignment")
        st.write(
            "Align harmonious elemental tiles into their serene resonant pattern. "
            "Tap any tile to rotate its orientation until all elements achieve equilibrium. Pure visual satisfaction."
        )

        PUZZLE_LEVELS = [
            {
                "level": 1,
                "title": "Level 1: The Celestial Triangle",
                "intro": "Rotate the 3 cosmic stones so their sacred glyphs point toward the central celestial core.",
                "tiles": [
                    {"id": 0, "name": "Sun Stone", "target_rot": 0, "symbol": "☀️"},
                    {"id": 1, "name": "Moon Shard", "target_rot": 0, "symbol": "🌙"},
                    {"id": 2, "name": "Star Core", "target_rot": 0, "symbol": "⭐"}
                ],
                "affirmation": "✨ Balance achieved! Cosmic clarity illuminates your mind."
            },
            {
                "level": 2,
                "title": "Level 2: The Four Elements",
                "intro": "Harmonize the 4 primordial elements (Earth, Water, Air, Fire) into their cardinal axes.",
                "tiles": [
                    {"id": 0, "name": "Earth Grove", "target_rot": 0, "symbol": "🌿"},
                    {"id": 1, "name": "Water Tide", "target_rot": 0, "symbol": "💧"},
                    {"id": 2, "name": "Air Breeze", "target_rot": 0, "symbol": "🌬️"},
                    {"id": 3, "name": "Fire Ember", "target_rot": 0, "symbol": "🔥"}
                ],
                "affirmation": "🌸 The four elements are in serene balance. Your energy is centered."
            },
            {
                "level": 3,
                "title": "Level 3: The Sacred Lotus",
                "intro": "Rotate the 4 lotus blossom petals to open the flower of mindfulness.",
                "tiles": [
                    {"id": 0, "name": "North Petal", "target_rot": 0, "symbol": "🌸"},
                    {"id": 1, "name": "East Petal", "target_rot": 0, "symbol": "🌺"},
                    {"id": 2, "name": "South Petal", "target_rot": 0, "symbol": "🪷"},
                    {"id": 3, "name": "West Petal", "target_rot": 0, "symbol": "🌷"}
                ],
                "affirmation": "🪷 The sacred lotus is in full bloom. You have discovered profound calmness."
            }
        ]

        if "calm_puzzle_lvl" not in st.session_state:
            st.session_state.calm_puzzle_lvl = 0
            # Initialize rotations: random non-zero rotations for current level
            st.session_state.puzzle_rotations = [90, 180, 270, 90]

        cur_p_idx = min(st.session_state.calm_puzzle_lvl, len(PUZZLE_LEVELS) - 1)
        p_data = PUZZLE_LEVELS[cur_p_idx]
        tiles = p_data["tiles"]
        num_tiles = len(tiles)

        # Controls bar
        cp_top1, cp_top2 = st.columns([3, 1])
        with cp_top1:
            st.markdown(f"#### {p_data['title']}")
            st.caption(p_data["intro"])
        with cp_top2:
            if st.button("🔄 Scramble / Reset", key=f"btn_reset_puzzle_{cur_p_idx}", use_container_width=True):
                st.session_state.puzzle_rotations = [(i * 90 + 90) % 360 for i in range(num_tiles)]
                st.rerun()

        # Render puzzle interactive grid
        tile_cols = st.columns(num_tiles)
        all_aligned = True

        for idx, t in enumerate(tiles):
            cur_rot = st.session_state.puzzle_rotations[idx] if idx < len(st.session_state.puzzle_rotations) else 0
            is_target = (cur_rot % 360 == t["target_rot"])
            if not is_target:
                all_aligned = False

            border_color = "#10b981" if is_target else "#cbd5e1"
            bg_color = "#ecfdf5" if is_target else "#ffffff"
            status_tag = "Aligned ✅" if is_target else f"Rotated {cur_rot}°"

            with tile_cols[idx]:
                st.markdown(f"""
                    <div style="background: {bg_color}; border: 2px solid {border_color}; border-radius: 12px; padding: 1.2rem; text-align: center; margin-bottom: 0.5rem; transition: all 0.3s ease; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);">
                        <div style="font-size: 2.8rem; transform: rotate({cur_rot}deg); transition: transform 0.3s cubic-bezier(0.34, 1.56, 0.64, 1); margin-bottom: 0.5rem;">
                            {t['symbol']}
                        </div>
                        <div style="font-weight: 700; color: #1e293b; font-size: 0.95rem;">{t['name']}</div>
                        <div style="font-size: 0.8rem; color: {'#059669' if is_target else '#64748b'}; font-weight: 600; margin-top: 0.2rem;">{status_tag}</div>
                    </div>
                """, unsafe_allow_html=True)

                if st.button(f"Rotate ↻", key=f"btn_rot_{cur_p_idx}_{idx}", use_container_width=True):
                    arr = st.session_state.puzzle_rotations.copy()
                    while len(arr) <= idx:
                        arr.append(0)
                    arr[idx] = (arr[idx] + 90) % 360
                    st.session_state.puzzle_rotations = arr
                    st.rerun()

        # Completion Status
        if all_aligned:
            st.markdown(f"""
                <div style="background: #ecfdf5; border: 2px solid #10b981; border-radius: 12px; padding: 1.2rem; text-align: center; margin: 1.5rem 0;">
                    <h3 style="color: #065f46; margin: 0 0 0.3rem 0;">🎉 Equilibrium Unlocked!</h3>
                    <p style="color: #047857; font-weight: 600; margin: 0;">{p_data['affirmation']}</p>
                </div>
            """, unsafe_allow_html=True)
            
            if cur_p_idx + 1 < len(PUZZLE_LEVELS):
                if st.button("Advance to Next Room ➡️", key=f"btn_next_puzzle_{cur_p_idx}", type="primary", use_container_width=True):
                    st.session_state.calm_puzzle_lvl += 1
                    next_count = len(PUZZLE_LEVELS[cur_p_idx + 1]["tiles"])
                    st.session_state.puzzle_rotations = [(i * 90 + 90) % 360 for i in range(next_count)]
                    st.rerun()
            else:
                st.balloons()
                st.success("🌟 Master of Calm! You have completed all rooms in the Calm Puzzle Sanctuary.")
                if st.button("Revisit Room 1 🌿", key="btn_replay_all_puzzles", use_container_width=True):
                    st.session_state.calm_puzzle_lvl = 0
                    st.session_state.puzzle_rotations = [90, 180, 270, 90]
                    st.rerun()
        else:
            st.caption("💡 Hint: Rotate each tile until it faces upright (0°) and turns green to harmonize the mandala.")
