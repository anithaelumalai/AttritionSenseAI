import os
import sys
import json
import sqlite3
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from utils.database import get_connection

# ==============================================================================
# STRUCTURED WEEKLY QUIZ QUESTION BANK (10 MCQs PER WEEK)
# Scenario-based, practical, non-trivial, with thoughtful non-spoiler clues
# ==============================================================================

WEEKLY_QUIZ_BANK: Dict[int, Dict[str, Any]] = {
    1: {
        "title": "Week 1: High-Impact Communication, Feedback & Alignment",
        "description": "Master proactive clarity, constructive feedback delivery, psychological safety, and asynchronous team collaboration.",
        "questions": [
            {
                "id": 1,
                "question": "A product manager shares a feature brief with ambiguous acceptance criteria, and your sprint starts tomorrow. What is the most constructive first step?",
                "options": [
                    "Begin coding the parts that seem obvious and ask questions only when you get stuck",
                    "Send a concise bulleted summary of your interpretation with 2-3 specific clarification questions and request a 10-minute alignment sync",
                    "Wait until the sprint retrospective to document that the product requirements were incomplete",
                    "Ask an adjacent teammate to make the scoping decisions on behalf of the product manager"
                ],
                "answer_index": 1,
                "clue": "Think about securing rapid, documented alignment before sinking development hours, without stalling team momentum.",
                "explanation": "Documenting your interpretation alongside specific targeted questions minimizes back-and-forth friction and establishes shared expectations before sprint work begins."
            },
            {
                "id": 2,
                "question": "During a technical design review, a colleague strongly advocates for an architecture that you anticipate will hit severe scaling bottlenecks under load. How should you raise your concern?",
                "options": [
                    "Acknowledge the architectural benefits they highlighted, then present concrete traffic benchmarks outlining the specific bottleneck scenario and invite collaborative stress-testing",
                    "Privately direct-message the engineering lead during the call asking them to overrule the proposal",
                    "Concede in the meeting to avoid friction, then build an alternative proof-of-concept in private",
                    "State that previous industry leaders avoided this pattern and label the proposal fundamentally flawed"
                ],
                "answer_index": 0,
                "clue": "Anchor technical pushback on verifiable empirical metrics and mutual problem-solving rather than subjective debate.",
                "explanation": "Validating the positive aspects of a peer's proposal before presenting objective benchmark scenarios preserves psychological safety while guiding the team toward resilient engineering."
            },
            {
                "id": 3,
                "question": "You are conducting a peer code review and notice repeated omission of unit tests that violates your team's documented engineering guidelines. What is the most effective comment?",
                "options": [
                    "'Why are there no tests again? Please read the team documentation before opening PRs.'",
                    "'Looks good overall, but hopefully someone can add test coverage in a follow-up ticket before production.'",
                    "'Clean implementation of the core domain logic! Let's add test coverage for boundary cases X and Y to uphold our team regression safety standard.'",
                    "Approve the pull request as is and quickly write the missing tests yourself to prevent sprint delays"
                ],
                "answer_index": 2,
                "clue": "Pair genuine acknowledgement of quality work with clear, standards-based expectations for thoroughness.",
                "explanation": "Framing feedback around team standards and specific edge cases depersonalizes the critique and reinforces high craft standards constructively."
            },
            {
                "id": 4,
                "question": "You are engaged in deep troubleshooting on a critical customer issue when a cross-functional peer sends a chat message with a 'quick non-urgent request'. What is the best communication practice?",
                "options": [
                    "Immediately switch tasks and answer their questions so they aren't blocked waiting",
                    "Ignore the notification completely until the end of your shift without acknowledging receipt",
                    "Send a brief polite reply: 'Deep in an urgent production fix right now. I have dedicated open hours at 3:30 PM and will review this with full focus then!'",
                    "Reply with an unaccompanied link to a 40-page wiki documentation page"
                ],
                "answer_index": 2,
                "clue": "Protect your focus state while giving the stakeholder predictable visibility on when to expect your support.",
                "explanation": "Setting a clear, timely boundary confirms that their inquiry is noted while safeguarding uninterrupted focus for high-stakes problem resolution."
            },
            {
                "id": 5,
                "question": "In a 1-on-1, your manager observes that your status updates during daily standups have been too detailed and are extending meeting duration. What is the most professional response?",
                "options": [
                    "Defend your approach by explaining that total technical transparency is essential for engineering rigor",
                    "Thank them for the observation, ask for an example of ideal standup brevity, and propose adopting a 3-bullet headline format",
                    "Cease speaking in standups entirely and only post written messages in the team chat channel",
                    "Express distress and ask whether this will negatively affect your upcoming annual compensation review"
                ],
                "answer_index": 1,
                "clue": "Treat feedback as coaching input: clarify the expected baseline and propose a concrete mechanism to adapt.",
                "explanation": "Seeking clarity on the desired standard and proposing a structured adjustment shows emotional maturity, adaptability, and respect for team time."
            },
            {
                "id": 6,
                "question": "You are preparing to take a week of scheduled annual leave. How should you structure your transition to guarantee zero team disruption?",
                "options": [
                    "Keep your laptop on hand and promise to check and respond to Slack messages every evening",
                    "Publish a concise handoff document covering in-flight initiatives, designated coverage owners, key decision links, and explicit emergency escalation thresholds",
                    "Set your Slack status to 'Away' five minutes before leaving without assigning coverage for active tickets",
                    "Reassign all your open Jira issues to your closest peer right before signing off"
                ],
                "answer_index": 1,
                "clue": "A seamless handoff provides proactive visibility, named owners, and a precise threshold for what constitutes a genuine emergency.",
                "explanation": "A structured handover empowers colleagues to make informed decisions in your absence and allows you to disconnect authentically without guilt."
            },
            {
                "id": 7,
                "question": "A stakeholder expects a new dashboard to launch this Friday, but your team's refined technical estimate indicates two additional weeks are needed. How do you handle this gap?",
                "options": [
                    "Pull consecutive late nights to ship an unverified version to meet the Friday date at all costs",
                    "Schedule an alignment sync today to transparently explain the technical dependencies and propose an MVP phased release plan",
                    "Send an email on Friday morning informing them that the deadline cannot be met",
                    "Ask your team lead to deliver the bad news while you remain focused on coding"
                ],
                "answer_index": 1,
                "clue": "Address timeline mismatches as early as possible with transparent trade-offs and pragmatic phased alternatives.",
                "explanation": "Early transparent communication builds stakeholder trust, and proposing a phased MVP preserves quality while delivering incremental value."
            },
            {
                "id": 8,
                "question": "Your engineering team collaborates across three distinct global time zones. What is a core practice of world-class asynchronous teamwork?",
                "options": [
                    "Requiring teammates in distant time zones to attend midnight status meetings to maintain live sync",
                    "Writing self-contained proposals with full background context, alternatives evaluated, and explicit decision deadlines so peers can review and unblock themselves",
                    "Relying solely on informal direct messages and avoiding centralized team documentation",
                    "Tagging '@everyone' repeatedly to prompt immediate replies regardless of local working hours"
                ],
                "answer_index": 1,
                "clue": "Asynchronous efficiency relies on comprehensive upfront context that eliminates unnecessary back-and-forth round trips.",
                "explanation": "Self-contained asynchronous artifacts allow global team members to digest context and make sound technical decisions during their natural peak focus hours."
            },
            {
                "id": 9,
                "question": "During a postmortem for a major customer-facing outage, the discussion begins turning toward blaming a junior engineer who pushed the failing commit. How should a senior colleague redirect the meeting?",
                "options": [
                    "Concur that the junior engineer should be stripped of deployment permissions until further notice",
                    "Intervene calmly: 'Let's focus on our system safeguards. If a single commit can bypass testing and cause an outage, our automated safety nets failed, not an individual.'",
                    "Remain quiet to allow the meeting organizer to handle the interpersonal dynamic",
                    "Suggest ending the retrospective immediately to avoid awkwardness among team members"
                ],
                "answer_index": 1,
                "clue": "Blameless retrospectives analyze systemic, tooling, and pipeline vulnerabilities rather than personal fault.",
                "explanation": "Psychological safety thrives when organizations treat incidents as opportunities to harden automation and guardrails rather than hunting for scapegoats."
            },
            {
                "id": 10,
                "question": "A teammate approaches you visibly frustrated about an unexpected blocker caused by another department. What is the most effective initial response?",
                "options": [
                    "Immediately prescribe the exact tactical steps you took when faced with a similar issue last quarter",
                    "Listen actively to validate the situation, then ask: 'Would you like to brainstorm practical solutions together, or do you just need to vent through it first?'",
                    "Dismiss their frustration by saying that organizational friction is standard at every tech firm",
                    "Encourage them to escalate the matter directly to executive leadership immediately"
                ],
                "answer_index": 1,
                "clue": "Establish whether the colleague needs emotional decompression or collaborative problem-solving before jumping to advice.",
                "explanation": "Asking whether someone needs a sounding board or active brainstorming demonstrates empathy and prevents premature, unhelpful advice."
            }
        ]
    },
    2: {
        "title": "Week 2: Prioritization, Problem Solving & Growth Mindset",
        "description": "Develop frameworks for navigating ambiguity, managing technical debt, root-cause troubleshooting, and continuous learning.",
        "questions": [
            {
                "id": 1,
                "question": "You arrive on Monday morning with 6 competing tasks marked 'Urgent' by different stakeholders. How do you prioritize objectively?",
                "options": [
                    "Complete the quickest tasks first to clear your backlog, regardless of business impact",
                    "Apply an impact-versus-effort matrix, identify dependencies on the critical path, and communicate realistic sequencing to stakeholders",
                    "Work simultaneously on all 6 tasks in 15-minute increments throughout the day",
                    "Focus only on requests from the most senior stakeholder and ignore the rest"
                ],
                "answer_index": 1,
                "clue": "Evaluate initiatives through systemic business impact and workflow dependencies rather than urgency volume.",
                "explanation": "Systematic prioritization based on impact and critical-path dependencies ensures high-leverage execution and manages stakeholder expectations."
            },
            {
                "id": 2,
                "question": "A recurring database connection timeout is disrupting services intermittently. A quick service reboot clears it for 48 hours. What is the soundest engineering approach?",
                "options": [
                    "Schedule an automated cron job to reboot the service every midnight and consider the issue resolved",
                    "Conduct a 5-Whys root cause analysis, inspect connection pool leak traces, and implement connection lifecycle hygiene",
                    "Increase server RAM and CPU specifications without investigating application query behavior",
                    "Disable health checks so alerting systems stop notifying on-call engineers"
                ],
                "answer_index": 1,
                "clue": "Address underlying systemic defects rather than repeatedly treating visible surface symptoms.",
                "explanation": "Restarting masking leaks incurs growing technical debt; diagnosing connection pool leak lifecycles ensures long-term operational resilience."
            },
            {
                "id": 3,
                "question": "You are assigned to architect a new microservice using an unfamiliar distributed streaming technology. You feel a surge of imposter syndrome. How do you proceed?",
                "options": [
                    "Decline the project immediately to avoid exposing gaps in your technical background",
                    "Acknowledge the learning curve, build a time-boxed prototype to validate key unknowns, and seek architecture feedback from a domain specialist",
                    "Pretend complete mastery in team meetings and hope you can figure out distributed nuances along the way",
                    "Copy an existing codebase verbatim without understanding its message-ordering trade-offs"
                ],
                "answer_index": 1,
                "clue": "Treat unfamiliar technologies with a growth mindset: time-boxed experimentation de-risks architectural uncertainty.",
                "explanation": "Spike prototypes and transparent consultation with domain peers accelerate mastery and lead to robust architectural decisions."
            },
            {
                "id": 4,
                "question": "Midway through a two-week sprint, a product owner requests adding a 'small additional filter' to an in-flight search feature. What is the best agile response?",
                "options": [
                    "Accept the request immediately without adjusting estimates to delight the product owner",
                    "Reject the request rudely and criticize the product owner for poor initial planning",
                    "Evaluate the architectural impact with the team; if it threatens sprint commitments, capture it as the top backlog candidate for the next sprint or swap out an equal-effort task",
                    "Quietly cut unit testing time to accommodate the new filter without telling anyone"
                ],
                "answer_index": 2,
                "clue": "Protect delivery commitments through transparent trade-off discussions rather than absorbing hidden scope creep.",
                "explanation": "Agile teams welcome evolving requirements by making the trade-off visible—either through sprint scope swaps or backlog prioritization."
            },
            {
                "id": 5,
                "question": "Your codebase has accumulated substantial technical debt that slows feature velocity, but product management wants only customer-facing features this quarter. How do you advocate for refactoring?",
                "options": [
                    "Refuse to work on any new features until management permits a full 3-month total rewrite",
                    "Translate technical debt into business metrics: demonstrate how legacy modules increase defect rates and lengthen time-to-market, and propose allocating 20% of each sprint to incremental debt reduction",
                    "Surreptitiously refactor core modules during feature work without mentioning it in standups",
                    "Resign yourself to the debt and accept that software quality inevitably degrades"
                ],
                "answer_index": 1,
                "clue": "Connect engineering health directly to business outcomes like release velocity, defect rates, and customer reliability.",
                "explanation": "Framing refactoring in terms of business velocity and proposing a steady 20% capacity investment aligns technical hygiene with product velocity."
            },
            {
                "id": 6,
                "question": "You are delegating an integration module to a junior engineer. How do you balance guidance with autonomy?",
                "options": [
                    "Dictate every variable name, method structure, and commit message on an hourly basis",
                    "Clearly define the desired end outcome, architectural boundaries, and test criteria, schedule regular check-ins, and let them own the implementation path",
                    "Hand them the title of the ticket and offer zero guidance so they can 'figure it out the hard way'",
                    "Take the task back the moment they run into their first compiler or syntax error"
                ],
                "answer_index": 1,
                "clue": "Effective delegation provides clear outcome parameters and guardrails while leaving tactical execution ownership to the engineer.",
                "explanation": "Defining clear goals and milestones while granting implementation autonomy accelerates growth and builds genuine engineering ownership."
            },
            {
                "id": 7,
                "question": "You must choose an external vendor API for a core workflow. You have about 70% of the complete data you'd ideally want, and gathering more will take 3 weeks. How should you approach the decision?",
                "options": [
                    "Paralyze the initiative for 3 weeks until you have 100% certainty",
                    "Evaluate whether this decision is reversible (a two-way door) or irreversible; if reversible, synthesize the 70% data with a fallback contingency and move forward",
                    "Flip a coin to make the decision instantly without documenting trade-offs",
                    "Delegate the final sign-off to a junior teammate to avoid personal accountability"
                ],
                "answer_index": 1,
                "clue": "Distinguish between reversible and irreversible decisions; waiting for complete certainty often incurs unacceptable delay costs.",
                "explanation": "High-velocity organizations use the 70% information rule for two-way door decisions, moving decisively while implementing mitigations."
            },
            {
                "id": 8,
                "question": "A junior developer asks you for help with a bug that has blocked them for 2 hours. What is the best coaching approach?",
                "options": [
                    "Take their keyboard, fix the bug in 30 seconds, and tell them to watch what you did",
                    "Ask guiding questions: 'What was your mental model of what should happen? Where did the actual execution diverge, and what does the log trace indicate?'",
                    "Tell them they should spend at least 4 more hours trying to solve it alone before asking for help",
                    "Send them a link to a generic tutorial site without reviewing their code"
                ],
                "answer_index": 1,
                "clue": "Teach debugging methodology and mental models rather than simply providing the final fix.",
                "explanation": "Guided inquiry helps engineers develop diagnostic intuition, self-sufficiency, and analytical problem-solving skills."
            },
            {
                "id": 9,
                "question": "A major third-party cloud API outage disrupts your continuous deployment pipeline during a critical launch window. What is the most effective response?",
                "options": [
                    "Post frantic messages in company-wide channels assigning blame to the cloud provider",
                    "Activate your team's documented disaster recovery / fallback protocol, communicate status proactively on the incident channel, and adjust deployment timelines calmly",
                    "Try hacking around the provider's security controls to force a manual deployment",
                    "Abandon all communication and sign off until the cloud vendor's status dashboard turns green"
                ],
                "answer_index": 1,
                "clue": "Operational maturity shows through calm protocol activation, transparent status dissemination, and orderly contingency management.",
                "explanation": "Maintaining composure, following established incident protocols, and communicating clearly preserves team trust during external service disruptions."
            },
            {
                "id": 10,
                "question": "During a demanding quarter with aggressive deliverables, how can an engineer maintain continuous learning and technical sharpness?",
                "options": [
                    "Sacrifice sleep to complete 4-hour technical courses late every night",
                    "Integrate micro-learning: dedicate 20-30 minutes during weekly focus blocks to study technical architecture RFCs, postmortems, or new language patterns relevant to current projects",
                    "Assume that professional learning can only happen when the company sponsors an external conference",
                    "Stop learning entirely until workloads decrease to zero"
                ],
                "answer_index": 1,
                "clue": "Small, consistent micro-learning habits tied directly to your day-to-day domain outlast sporadic binge studying.",
                "explanation": "Consistent micro-learning integrated into weekly routines compounds into significant expertise without creating schedule exhaustion."
            }
        ]
    },
    3: {
        "title": "Week 3: Work-Life Harmony, Energy Management & Sustainable Pace",
        "description": "Cultivate resilient work boundaries, combat cognitive exhaustion, practice effective recovery, and sustain long-term career stamina.",
        "questions": [
            {
                "id": 1,
                "question": "You find yourself checking work email and messaging channels repeatedly late on Sunday evening, creating preemptive Monday anxiety. What is the most effective habit shift?",
                "options": [
                    "Start completing Monday's workload on Sunday night so Monday morning feels less stressful",
                    "Establish a digital sunset ritual: schedule an asynchronous status review on Friday afternoon, turn off weekend notifications, and reserve Sunday evening for genuine cognitive recharge",
                    "Leave notifications on but resolve not to reply unless a message has exclamation marks",
                    "Delete all work apps from your mobile device permanently and never communicate asynchronously"
                ],
                "answer_index": 1,
                "clue": "Preemptive anxiety diminishes when you close open cognitive loops on Friday afternoon before your weekend starts.",
                "explanation": "A deliberate Friday shutdown routine closes open loops, giving your subconscious permission to detach and rest throughout the weekend."
            },
            {
                "id": 2,
                "question": "What is the primary cognitive difference between taking a 10-minute walk outside and spending a 10-minute break scrolling social media?",
                "options": [
                    "Social media scrolling is more restful because it requires zero physical movement",
                    "Natural environments and walking activate involuntary attention (soft fascination), restoring executive function, whereas social feeds sustain high cognitive stimulation and dopamine spikes",
                    "There is no difference; both are considered equivalent rest activities",
                    "Walking depletes energy reserves needed for programming tasks"
                ],
                "answer_index": 1,
                "clue": "True cognitive restoration requires disengaging the prefrontal cortex rather than bombarding it with new digital stimuli.",
                "explanation": "Attention Restoration Theory proves that non-screen nature breaks allow prefrontal attentional mechanisms to recover, whereas social media perpetuates mental fatigue."
            },
            {
                "id": 3,
                "question": "You are juggling tasks across 4 different projects, constantly interrupted by pings, and by 3:00 PM you feel exhausted despite having written very little code. What is causing this?",
                "options": [
                    "Lack of intrinsic technical passion for the projects",
                    "Attentional residue and context-switching overhead: shifting attention leaves cognitive baggage on previous tasks, multiplying mental exhaustion",
                    "Insufficient daily caffeine consumption",
                    "Working on too many modern software tools"
                ],
                "answer_index": 1,
                "clue": "Every rapid context switch incurs a measurable cognitive penalty that drains mental stamina without producing real output.",
                "explanation": "Research by Dr. Gloria Mark shows that switching tasks every few minutes incurs massive attention residue, fragmenting focus and inducing severe cognitive fatigue."
            },
            {
                "id": 4,
                "question": "A colleague routinely works late into the evening and begins sending non-urgent messages at 11:00 PM expecting immediate replies. How do you handle this professionally?",
                "options": [
                    "Wake up and reply immediately to maintain a reputation as an ultra-responsive team player",
                    "Set your notification schedules to Do Not Disturb outside working hours, and reply during normal business hours the next morning calmly without apology",
                    "Send an angry late-night message rebuking them for messaging outside office hours",
                    "Complain directly to human resources without speaking with your colleague first"
                ],
                "answer_index": 1,
                "clue": "Model healthy personal boundaries through calm, predictable asynchronous behavior during business hours.",
                "explanation": "You teach peers how to treat your time by your response patterns; answering during normal business hours sets a healthy standard without escalating tension."
            },
            {
                "id": 5,
                "question": "Perfectionism is causing you to spend 8 extra hours endlessly refactoring internal code that is already tested, functional, and meeting all acceptance criteria. What principle helps overcome this?",
                "options": [
                    "Software should always be pursued to theoretical perfection regardless of delivery schedules",
                    "The law of diminishing returns: recognize that shipping high-quality, maintainable code on time is superior to endlessly chasing elusive perfection",
                    "Never refactor any code under any circumstances",
                    "Only submit code if you are 100% confident it will never need to be modified in the next 10 years"
                ],
                "answer_index": 1,
                "clue": "Strive for excellent craftsmanship while recognizing where incremental polish ceases to provide meaningful user value.",
                "explanation": "Mature engineering balances high technical quality with pragmatic delivery, recognizing that software is an evolving artifact, not a permanent monument."
            },
            {
                "id": 6,
                "question": "You have accumulated 15 days of earned paid time off (PTO) but feel guilty taking a week off because your team has a busy quarterly roadmap. What is the most constructive perspective?",
                "options": [
                    "Forfeit your vacation time to demonstrate total dedication to the team",
                    "Recognize that planned rest sustains long-term creativity and performance; coordinate coverage in advance and take your earned leave with clear handoffs",
                    "Take the time off but secretly work 4 hours every morning from your hotel room",
                    "Wait until you experience complete burnout before taking emergency leave"
                ],
                "answer_index": 1,
                "clue": "Preventative recovery is far more effective for team velocity than emergency recovery from severe burnout.",
                "explanation": "Taking earned leave prevents deep exhaustion, restores creative problem-solving, and models healthy, sustainable behaviors for your peers."
            },
            {
                "id": 7,
                "question": "Which workplace ergonomic setup has the strongest documented impact on reducing musculoskeletal strain during long desk shifts?",
                "options": [
                    "Slouching deep into a couch with a laptop balanced on your knees",
                    "Positioning the top third of your monitor at eye level, elbows at 90 degrees, feet flat on the floor or footrest, with frequent standing/micro-movement pauses",
                    "Sitting completely motionless in an expensive gaming chair for 8 hours without standing",
                    "Working with the screen tilted at a 45-degree angle in a dim room"
                ],
                "answer_index": 1,
                "clue": "Align eye level with the upper screen area and maintain neutral joint angles to avoid cervical spine fatigue.",
                "explanation": "Aligning your monitor with eye level and keeping joints at neutral 90-degree angles minimizes neck, shoulder, and lumbar strain."
            },
            {
                "id": 8,
                "question": "You realize your workload has expanded to the point where meeting quality standards requires working 60 hours a week continuously. How should you address this with your manager?",
                "options": [
                    "Keep working 60 hours quietly until you collapse from exhaustion",
                    "Schedule a sync with your manager, present a categorized inventory of your active commitments with time allocations, and ask for guidance on prioritizing and delegating the lower-impact items",
                    "Silently drop several commitments without informing anyone and hope no one notices",
                    "Send an ultimatum threatening to resign unless half your tasks are removed by tomorrow"
                ],
                "answer_index": 1,
                "clue": "Present your manager with clear visibility into your current commitments and engage them collaboratively in prioritization.",
                "explanation": "Good managers appreciate structured capacity visibility; presenting objective data enables constructive workload rebalancing."
            },
            {
                "id": 9,
                "question": "Following a tense, adversarial meeting with an external stakeholder, your heart is racing and your adrenaline is high. What physiological tool most quickly down-regulates autonomic stress?",
                "options": [
                    "Immediately drafting a fiery rebuttal email to express your frustration",
                    "The physiological sigh: two rapid nasal inhales followed by one prolonged, slow mouth exhale, repeated 3 to 4 times",
                    "Drinking two shots of espresso to power through the emotion",
                    "Denying that you feel any stress and jumping immediately into complex code"
                ],
                "answer_index": 1,
                "clue": "A double inhale followed by a prolonged exhale activates the parasympathetic vagus nerve response within 30 seconds.",
                "explanation": "Neurobiology research by Dr. Andrew Huberman confirms that physiological sighs rapidly rebalance carbon dioxide and stimulate the vagus nerve to slow heart rate."
            },
            {
                "id": 10,
                "question": "What is the hallmark of an effective daily shutdown routine at the end of the working day?",
                "options": [
                    "Leaving 40 browser tabs open, closing your laptop abruptly in mid-sentence, and wondering what you forgot all evening",
                    "Reviewing completed items, logging top 3 priority intentions for tomorrow, closing work tabs, and verbally or mentally declaring the workday concluded",
                    "Keeping Slack open on your phone so you never have to officially sign off",
                    "Writing a 10-page retrospective every single evening"
                ],
                "answer_index": 1,
                "clue": "A shutdown ritual creates a psychological boundary that signals to your brain that professional duties are safely parked until tomorrow.",
                "explanation": "A deliberate daily shutdown ritual documents open loops and cues the brain that it is safe to transition into personal and family recovery time."
            }
        ]
    },
    4: {
        "title": "Week 4: Team Leadership, Culture & Psychological Safety",
        "description": "Foster inclusive collaboration, lead through influence, build team resilience, and elevate team performance without authority.",
        "questions": [
            {
                "id": 1,
                "question": "A team project encounters an unforeseen regulatory roadblock that delays delivery by a month. Morale dips significantly. As an informal leader, how can you best support the team?",
                "options": [
                    "Point out that regulatory bodies are incompetent and commiserate in cynical complaints",
                    "Acknowledge the disappointment candidly, celebrate the resilient work done so far, and facilitate a focused session to break the new regulatory path into achievable weekly milestones",
                    "Pretend that the delay is wonderful news and tell everyone to be happy",
                    "Disengage from the project and focus exclusively on independent tasks"
                ],
                "answer_index": 1,
                "clue": "Acknowledge reality honestly while helping the team regain agency and momentum through clear, manageable next steps.",
                "explanation": "Authentic leadership balances empathy for disappointment with pragmatic reframing that restores agency and forward momentum."
            },
            {
                "id": 2,
                "question": "In a team meeting, a quieter team member tries to speak up with a technical suggestion but is repeatedly talked over by more vocal colleagues. How do you intervene?",
                "options": [
                    "Interrupt the meeting by shouting at the vocal colleagues to be quiet",
                    "Step in smoothly: 'Hold on a moment, I'd really like to hear what [Colleague] was beginning to share about that approach. [Colleague], what were your thoughts?'",
                    "Wait until after the meeting and tell the quieter colleague they need to be more assertive",
                    "Ignore it because the loudest ideas are usually the best ones anyway"
                ],
                "answer_index": 1,
                "clue": "Use conversational amplification to create space for peers without unnecessarily escalating meeting friction.",
                "explanation": "Amplifying quieter voices creates an inclusive culture where diverse perspectives can surface to improve technical outcomes."
            },
            {
                "id": 3,
                "question": "You notice that two high-performing senior engineers on your squad have developed personal friction over code formatting and architectural styling, slowing team reviews. What is the best path forward?",
                "options": [
                    "Pick a side publicly in standup to settle the debate once and for all",
                    "Encourage the squad to adopt automated linter and formatter rules in CI, removing subjective personal preferences from human reviews entirely",
                    "Reassign one of the engineers to a different department to eliminate contact",
                    "Ignore the tension and hope they work it out between themselves eventually"
                ],
                "answer_index": 1,
                "clue": "Replace subjective personal arguments with automated, team-agreed tooling standards in the CI pipeline.",
                "explanation": "Codifying conventions into automated linters eliminates bike-shedding and depersonalizes code review debates."
            },
            {
                "id": 4,
                "question": "Your engineering squad recently delivered a high-visibility feature ahead of schedule that received praise from executive leadership. How should credit be shared?",
                "options": [
                    "Take primary personal credit since you wrote the most complex technical module",
                    "Generously highlight the specific contributions of all team members, including testing, QA, documentation, design, and operations, in public channels",
                    "Downplay the achievement and say it was nothing special",
                    "Credit only the engineering manager who approved the sprint plan"
                ],
                "answer_index": 1,
                "clue": "Great teammates shine light on the whole collective effort and specific contributions of cross-functional partners.",
                "explanation": "Generous public recognition reinforces team cohesion, builds goodwill across disciplines, and creates a supportive cultural flywheel."
            },
            {
                "id": 5,
                "question": "A newly hired engineer makes a significant mistake in their second week, inadvertently dropping a development staging database. How should you respond?",
                "options": [
                    "Share a meme making fun of their mistake in the general company Slack channel",
                    "Reassure them: 'Welcome to the club—every senior engineer here has dropped a database before. Let's restore from our backup together and add a safety check so it's impossible to do accidentally again.'",
                    "Report their error to their manager and suggest probation review",
                    "Privately warn them that another mistake will likely lead to termination"
                ],
                "answer_index": 1,
                "clue": "Turn early mistakes into bonding and learning milestones by normalizing errors and hardening developer guardrails.",
                "explanation": "Normalizing recovery from mistakes transforms an anxiety-inducing moment into lasting psychological safety and technical resilience."
            },
            {
                "id": 6,
                "question": "Your team is deciding between two cloud vendors. One engineer presents a passionate, well-researched case for Vendor A, while another presents an equally compelling case for Vendor B. How do you lead toward resolution?",
                "options": [
                    "Vote based on who has spent more years at the company",
                    "Formulate a weighted decision matrix with clear criteria (cost, latency, compliance, maintainability) and test both options against the criteria objectively",
                    "Continue debating in meetings indefinitely until one person gives up out of exhaustion",
                    "Avoid using cloud services entirely to maintain neutrality"
                ],
                "answer_index": 1,
                "clue": "Decouple technical evaluations from egos by establishing clear, weighted decision criteria ahead of time.",
                "explanation": "Weighted decision matrices depersonalize decisions and provide transparent rationale that everyone can align behind."
            },
            {
                "id": 7,
                "question": "What is the primary characteristic of an organization with high psychological safety, according to Harvard research by Dr. Amy Edmondson?",
                "options": [
                    "A culture where conflict never occurs and everyone always agrees with leadership",
                    "A culture where team members feel safe to take interpersonal risks, ask questions, admit mistakes, and propose wild ideas without fear of humiliation",
                    "A culture where performance standards are lowered so no one feels stressed",
                    "A culture where all employee metrics are made completely public on leaderboards"
                ],
                "answer_index": 1,
                "clue": "Psychological safety does not mean low standards; it means the freedom to be candid, vulnerable, and innovative without social penalty.",
                "explanation": "Dr. Edmondson's research shows that psychological safety pairs high accountability with freedom from interpersonal fear, unlocking elite performance."
            },
            {
                "id": 8,
                "question": "You notice that a teammate who is usually communicative and energetic has become quiet, withdrawn, and is missing deadlines over the past two weeks. What is the most empathetic step?",
                "options": [
                    "Call them out publicly in standup to hold them accountable to the team",
                    "Reach out for a casual, supportive 1-on-1: 'Hey, I've noticed things seem heavier than usual lately and wanted to check in. No work pressure, just here if you need a listening ear or want to offload a ticket.'",
                    "Assume they are slacking off and ignore it until management steps in",
                    "Send an anonymous complaint to their manager"
                ],
                "answer_index": 1,
                "clue": "Approach behavioral shifts with genuine personal curiosity and compassion rather than immediate punitive judgment.",
                "explanation": "Checking in with warmth and low pressure creates a safe space for colleagues going through personal or professional challenges."
            },
            {
                "id": 9,
                "question": "Your squad is embarking on an experimental new architecture that has a real chance of failing. How should the team frame the initiative?",
                "options": [
                    "Promise executive leadership guaranteed perfection and hide any preliminary failures",
                    "Frame it as an empirical experiment: define explicit success/failure criteria, time-box the exploration, and celebrate lessons learned regardless of the outcome",
                    "Abandon the experiment because safe, legacy approaches never risk failure",
                    "Place all risk on a contractor so internal employees avoid accountability"
                ],
                "answer_index": 1,
                "clue": "Innovation requires framing uncertainty as hypotheses to test rather than win/lose gambles.",
                "explanation": "Treating innovation as time-boxed scientific experimentation allows teams to push technical boundaries while bounding blast radius."
            },
            {
                "id": 10,
                "question": "What distinguishes genuine mentorship from simply supervising someone's day-to-day tickets?",
                "options": [
                    "Mentorship focuses only on policing deadlines and micromanaging pull requests",
                    "Mentorship invests in the mentee's long-term career trajectory, building their strategic problem-solving instincts, expanding their network, and advocating for their growth",
                    "Mentorship means doing the mentee's work for them whenever they feel tired",
                    "Mentorship is an informal social chat with zero technical substance"
                ],
                "answer_index": 1,
                "clue": "Mentorship looks beyond immediate sprint deliverables to nurture the engineer's enduring capabilities and career horizon.",
                "explanation": "True mentors invest in their peers' broader career development, strategic thinking, and confidence, creating lasting organizational value."
            }
        ]
    }
}

# ==============================================================================
# QUIZ DATA ACCESS & SUBMISSION METHODS
# ==============================================================================

def get_available_weeks() -> List[int]:
    """Returns the list of available weekly quiz numbers."""
    return sorted(list(WEEKLY_QUIZ_BANK.keys()))

def get_quiz_for_week(week_num: int) -> Dict[str, Any]:
    """Retrieves the complete quiz structure for a given week."""
    if week_num not in WEEKLY_QUIZ_BANK:
        week_num = 1
    return WEEKLY_QUIZ_BANK[week_num]

def get_current_week_number() -> int:
    """
    Returns an appropriate week number (1-4) based on the current calendar week.
    Cycle across the 4 curated weeks.
    """
    cal_week = datetime.now().isocalendar()[1]
    week_idx = ((cal_week - 1) % len(WEEKLY_QUIZ_BANK)) + 1
    return week_idx

def get_weekend_quiz_questions(week_num: Optional[int] = None) -> List[Dict[str, Any]]:
    """
    Returns the 10 questions for the selected (or current) week.
    Maintained for backwards compatibility.
    """
    if week_num is None:
        week_num = get_current_week_number()
    return get_quiz_for_week(week_num)["questions"]

def save_weekly_quiz_submission(
    employee_id: str,
    week: int,
    score: int,
    total_questions: int,
    answers: Dict[int, str],
    correct_answers: Dict[int, str],
    category: str = "Mindfulness & Workplace"
) -> bool:
    """
    Saves structured weekly quiz completion.
    
    PRIVACY GUARANTEE:
    This score is strictly personal and private to the employee.
    It is NEVER shared with HR and NEVER influences AI attrition risk,
    growth status, or retention recommendations.
    """
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO quiz_scores (
            employee_id, score, total_questions, category, week,
            answers_json, correct_answers_json, quiz_date
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        str(employee_id),
        int(score),
        int(total_questions),
        category,
        int(week),
        json.dumps(answers),
        json.dumps(correct_answers),
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ))
    conn.commit()
    conn.close()
    return True

def save_quiz_score(
    employee_id: str,
    score: int,
    total_questions: int,
    category: str = "Mindfulness & Workplace",
    week: int = 1
) -> bool:
    """
    Saves quiz score (backwards compatibility method).
    """
    return save_weekly_quiz_submission(
        employee_id=employee_id,
        week=week,
        score=score,
        total_questions=total_questions,
        answers={},
        correct_answers={},
        category=category
    )

def get_employee_quiz_scores(employee_id: str) -> List[Dict[str, Any]]:
    """Returns all quiz completion history for the authenticated employee only."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT * FROM quiz_scores 
        WHERE employee_id = ? 
        ORDER BY quiz_date DESC
    """, (str(employee_id),))
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows

def get_employee_completed_weeks(employee_id: str) -> Dict[int, Dict[str, Any]]:
    """Returns a map of week -> latest completion for the employee."""
    all_scores = get_employee_quiz_scores(employee_id)
    completed = {}
    for entry in all_scores:
        wk = entry.get("week") or 1
        if wk not in completed:
            completed[wk] = entry
    return completed
