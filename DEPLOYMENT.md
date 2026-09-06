# AttritionSense AI — Production Deployment Guide

This guide outlines how to deploy the **AttritionSense AI** application to various production environments, configure secrets securely, and ensure full desktop & mobile responsiveness.

---

## 1. Quick Local Execution

To run the application locally:

```bash
cd AttritionSenseAI_Automatic
streamlit run app.py
```

- **Local URL:** `http://localhost:8501`
- **Network URL:** `http://<your-local-ip>:8501` (accessible from mobile phones on the same Wi-Fi network)

### Pre-configured Accounts
- **HR & Leadership:** `admin` / `admin123` (or `hr_manager` / `hr123`)
- **Employee Portal:** Any Employee ID from `1` to `2068` (e.g., `1`, `68`, `4`, `10`) with password `emp123`.

---

## 2. Option A: Streamlit Community Cloud (Recommended & Free)

Streamlit Community Cloud provides 1-click deployment with built-in HTTPS and automatic GitHub sync.

### Steps:
1. Push this project repository to **GitHub** (ensure `.streamlit/secrets.toml` is in `.gitignore`).
2. Log in to [share.streamlit.io](https://share.streamlit.io).
3. Click **"New app"**.
4. Select your GitHub repository, branch (`main`), and set the main file path to:
   ```
   AttritionSenseAI_Automatic/app.py
   ```
   *(or `app.py` if the repository root is the project folder)*.
5. In **Advanced Settings → Secrets**, paste your secrets:
   ```toml
   SMTP_EMAIL = "your_email@gmail.com"
   SMTP_APP_PASSWORD = "your_16_digit_app_password"
   HR_EMAIL = "hr_director@example.com"
   # Optional: for cloud generative AI BuddyBot
   GEMINI_API_KEY = "your_gemini_api_key"
   ```
6. Click **Deploy!**

---

## 3. Option B: Docker Container Deployment

The application includes a production-ready `Dockerfile` and `.dockerignore`.

### Build & Run Locally with Docker:
```bash
cd AttritionSenseAI_Automatic

# Build image
docker build -t attritionsense-ai .

# Run container
docker run -d -p 8501:8501 \
  -e SMTP_EMAIL="your_email@gmail.com" \
  -e SMTP_APP_PASSWORD="your_app_password" \
  -e HR_EMAIL="hr@example.com" \
  --name attritionsense attritionsense-ai
```

Access the app at `http://localhost:8501`.

---

## 4. Option C: Render / Railway / Hugging Face Spaces

### Render (Web Service)
1. Create a new **Web Service** pointing to your repository.
2. Select **Docker** environment (or Python 3.12).
3. Build Command (if Python): `pip install -r requirements.txt`
4. Start Command: `streamlit run app.py --server.port=$PORT --server.address=0.0.0.0`
5. Under **Environment Variables**, add:
   - `SMTP_EMAIL`
   - `SMTP_APP_PASSWORD`
   - `HR_EMAIL`
   - `GEMINI_API_KEY` (optional)

---

## 5. Environment Variables & Secrets Reference

| Variable | Required | Description | Example |
|---|:---:|---|---|
| `SMTP_EMAIL` | Recommended | Sender Gmail address for HR feedback notifications | `notifications@gmail.com` |
| `SMTP_APP_PASSWORD` | Recommended | 16-character Google App Password (with or without spaces) | `xxxx yyyy zzzz wwww` |
| `HR_EMAIL` | Recommended | HR recipient email address for feedback alerts | `hr_director@company.com` |
| `GEMINI_API_KEY` | Optional | Google Gemini API key for cloud LLM BuddyBot | `AIzaSy...` |
| `PORT` | Auto | Web server binding port | `8501` |

> [!IMPORTANT]
> Never commit `.streamlit/secrets.toml` or `.env` files to git. Use environment variables or cloud provider secrets managers in production.

---

## 6. Architecture & Data Persistence in Cloud

1. **Automated Database Seeding**:
   When the app starts up, `startup_system()` automatically initializes the SQLite tables and seeds the 1,470 verified employee accounts and default HR accounts if the database does not exist. No manual database setup is required.

2. **Persistent Storage**:
   In ephemeral cloud containers (e.g. basic Render or Heroku dynos), container restarts reset local SQLite files. If persistent feedback history across container redeploys is required in production, attach a persistent volume (e.g. Render Persistent Disk or Docker Volume mounted at `/app/database` and `/app/data`).

---

## 7. Cross-Device Compatibility

The application is engineered and tested for:
- **Desktop / Laptop browsers**: Chrome, Edge, Safari, Firefox.
- **Android mobile browsers**: Chrome for Android, Samsung Internet.
- **iPhone / iOS browsers**: Safari for iOS, Chrome for iOS.
- **Key mobile adaptations**:
  - Touch target heights (`>= 46px`)
  - No horizontal scrolling on small screens (`360px - 430px`)
  - Sliders sized for fingers without clipping
  - Responsive flexbox banners and stacking columns
  - Safe 16px input font sizing preventing iOS Safari auto-zoom
