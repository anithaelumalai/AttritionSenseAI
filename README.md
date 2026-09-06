# AttritionSense AI – Intelligent Employee Attrition Prediction and Retention Recommendation System

**AttritionSense AI** is a production-ready, dual-role AI platform that empowers organizations to understand and proactively mitigate employee turnover while providing team members with a private, supportive workplace companion.

Built strictly from scratch with **Python**, **Streamlit**, **Scikit-learn (Random Forest)**, **SQLite**, **Plotly**, and **ReportLab**.

---

## 🌟 Core Architecture & Two Separate Portals

The application enforces **strict Role-Based Access Control (RBAC)** across two separate interfaces:

### 1. 👤 Employee Portal (Confidential & Supportive)
- **Automatic Profile Loading:** Seamlessly loads the authenticated employee's verified HR attributes (read-only; no manual ML parameter editing).
- **BuddyBot (Conversational AI Companion):** Empathetic, context-aware workplace chatbot designed to listen, discuss burnout, meetings, and career questions. Fully private to the employee; never exposed to HR.
- **Mini Games:** Playable relaxation experiences (Memory Card Match, 4-7-8 Focus Breathing Sanctuary, Workplace Word Scramble) to recharge mental focus. Completely decoupled from attrition risk scoring.
- **Employee Feedback Channel:** Structured 8-dimension rating form with optional comments and confidentiality toggle. Triggers an automated SMTP notification email to HR upon submission.
- **Personal Wellness & Habits:** Self-care reminders and career reflection check-ins.

### 2. 🛡️ HR & Leadership Portal (Analytical & Prescriptive)
- **Executive Radar & Dashboard:** Real-time KPI summary across all 1,470 employees (High / Medium / Low Risk distribution, historical attrition rate, priority intervention queue).
- **Zero Manual ML Feature Entry:** HR searches or selects any verified `EmployeeNumber`. The system automatically loads all organizational attributes directly from the dataset.
- **Random Forest ML Prediction:** Predicts attrition probability, computes calibrated 0–100 Risk Score, and assigns risk level (`LOW RISK`: 0–39, `MEDIUM RISK`: 40–69, `HIGH RISK`: 70–100).
- **Attributed Risk Drivers:** Automatically highlights specific employee risk factors (e.g., frequent overtime, promotion stagnation, long commute, equity misalignment).
- **Prescriptive Retention Action Plan:** Generates tailored, actionable intervention strategies with designated owners and urgency targets.
- **Publication-Ready PDF Reports:** Instant one-click generation of formal executive PDF dossiers via ReportLab with signature blocks for HR case review.
- **Workforce Analytics:** Interactive Plotly charts analyzing attrition by Department, Job Role, Overtime, Satisfaction, Income, and Tenure.
- **Feedback Analytics:** Aggregated 8-dimension sentiment radar charts, stay-intent percentages, and anonymous comment logs.
- **Prediction History:** Full audit log of historical risk assessments with search, filtering, and CSV export.

---

## 🛠️ Technology Stack

- **Frontend & App Framework:** Streamlit
- **Machine Learning:** Scikit-learn (`RandomForestClassifier`), Joblib
- **Data Engineering:** Pandas, NumPy
- **Interactive Visualizations:** Plotly Express & Plotly Graph Objects
- **Document Generation:** ReportLab
- **Database & Storage:** SQLite (`app.db`), CSV (`employees.csv`, `feedback.csv`, `prediction_history.csv`)
- **Security & Hashing:** PBKDF2-HMAC-SHA256 with distinct per-user cryptographic salts
- **Email Dispatch:** Python `smtplib` / `email.mime`
- **Generative AI (Optional):** Google Gemini API (`google-generativeai`) with intelligent offline rule-based dialogue fallback

---

## 📂 Project Structure

```
AttritionSenseAI_Automatic/
│
├── app.py                          # Master Streamlit entrypoint with secure RBAC routing
├── requirements.txt                # Python dependencies
├── README.md                       # Documentation & deployment guide
├── .gitignore                      # Git ignore configuration
├── .env.example                    # Sample environment variables (SMTP, Gemini)
│
├── data/
│   ├── employees.csv               # 1,470-record IBM HR employee dataset
│   ├── feedback.csv                # Synced feedback records
│   └── prediction_history.csv      # Synced prediction audit log
│
├── database/
│   └── app.db                      # SQLite database (users, chats, feedback, history)
│
├── models/
│   ├── attrition_model.pkl         # Trained Random Forest Scikit-learn Pipeline
│   └── model_metadata.json         # Evaluation metrics & top feature importances
│
├── utils/
│   ├── __init__.py
│   ├── data_loader.py              # Dataset loading & employee lookup
│   ├── auth.py                     # PBKDF2 hashing, authentication & session RBAC
│   ├── database.py                 # SQLite initialization & actual EmployeeNumber seeding
│   ├── ml_pipeline.py              # Scikit-learn pipeline & training logic
│   ├── prediction.py               # ML inference & risk factor extraction
│   ├── recommendation.py           # Contextual retention action plan generator
│   ├── analytics.py                # Plotly workforce analytics
│   ├── feedback.py                 # Feedback submission & metrics aggregation
│   ├── history.py                  # Prediction logging & CSV synchronization
│   ├── pdf_report.py               # ReportLab executive PDF dossier generator
│   ├── chatbot.py                  # BuddyBot multi-turn contextual conversational engine
│   └── email_service.py            # SMTP dispatcher for feedback alerts
│
├── views/
│   ├── employee/
│   │   ├── login.py                # Dedicated Employee Login
│   │   ├── dashboard.py            # Employee wellness dashboard
│   │   ├── profile.py              # Read-only personal profile viewer
│   │   ├── buddybot_view.py        # BuddyBot private chat interface
│   │   ├── games_view.py           # Memory Match, Breathing, Word Scramble
│   │   ├── feedback_view.py        # 8-question feedback submission form
│   │   └── personal_info_view.py   # Personal wellness & reflection space
│   └── hr/
│       ├── login.py                # Dedicated HR Login
│       ├── dashboard.py            # Executive KPI radar & priority intervention queue
│       ├── search_prediction.py    # Automatic Employee ID search & ML prediction
│       ├── analytics_view.py       # Deep-dive interactive Plotly charts
│       ├── feedback_analytics.py   # Aggregated 8-dimension sentiment radar
│       ├── history_view.py         # Prediction history table with filters
│       ├── reports_view.py         # Executive PDF report center
│       └── about_view.py           # Architecture & ethical AI guidelines
│
├── scripts/
│   ├── setup_data.py               # Downloads and verifies the 1,470-record dataset
│   └── train_model.py              # Trains and evaluates the Random Forest model
│
├── tests/
│   ├── test_auth.py                # Authentication & RBAC test suite
│   ├── test_pdf_and_prediction.py  # Prediction, recommendation & PDF test suite
│   └── test_chatbot.py             # BuddyBot multi-turn dialogue test suite
│
└── notebooks/
    └── model_training.ipynb        # Jupyter notebook documenting EDA and ML training
```

---

## 🚀 Quickstart Guide

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Verify Dataset & Initialize System
The dataset, database, and machine learning models are pre-configured. To re-run the verification:
```bash
# Verify dataset (1,470 rows, 35 columns, non-sequential EmployeeNumbers)
python scripts/setup_data.py

# Initialize SQLite database and seed actual Employee accounts
python utils/database.py

# Train Random Forest model (Accuracy: ~83.3%, ROC-AUC: ~0.80)
python scripts/train_model.py
```

### 3. Run the Streamlit Application
```bash
streamlit run app.py
```

---

## 🔑 Login Credentials

### HR & Leadership Portal
- **Username:** `admin` | **Password:** `admin123`
- **Username:** `hr_manager` | **Password:** `hr123`

### Employee Portal
- **Employee ID:** `1` (or any valid `EmployeeNumber` such as `2`, `4`, `5`, `7`, `8`, `10`, ... `2068`)
- **Password:** `emp123`

*(Note: Accounts are pre-seeded exclusively for actual `EmployeeNumber`s present in `employees.csv`.)*

---

## 🛡️ Privacy & Ethical Safeguards

1. **Strict Role Separation:** Employees cannot view organizational analytics or other employee records; HR cannot access private BuddyBot conversations.
2. **Voluntary Activities:** Mini-games and BuddyBot chats are purely for employee well-being and are completely decoupled from performance reviews or attrition risk scores.
3. **Objective ML Inputs:** HR cannot alter individual employee attributes to manipulate predictive risk scores.
4. **Confidential Feedback:** Employees can submit feedback anonymously with a single toggle.
