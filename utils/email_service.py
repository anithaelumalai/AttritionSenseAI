import os
import sys
import socket
import smtplib
import tomllib
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, Any, Tuple, Optional
import streamlit as st

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def get_smtp_config() -> Dict[str, Any]:
    """
    Retrieves SMTP configuration securely from Streamlit secrets,
    local .streamlit/secrets.toml, or environment variables.
    Never exposes passwords.
    """
    config = {
        "host": "smtp.gmail.com",
        "port": 587,
        "user": "",
        "password": "",
        "hr_email": "anithaelumalai00987@gmail.com"
    }

    # 1. Check Streamlit secrets if running inside Streamlit
    try:
        if hasattr(st, "secrets"):
            # Flat top-level keys
            if "SMTP_EMAIL" in st.secrets:
                config["user"] = str(st.secrets["SMTP_EMAIL"]).strip()
            if "SMTP_APP_PASSWORD" in st.secrets:
                config["password"] = str(st.secrets["SMTP_APP_PASSWORD"]).strip()
            if "HR_EMAIL" in st.secrets:
                config["hr_email"] = str(st.secrets["HR_EMAIL"]).strip()
            if "SMTP_HOST" in st.secrets:
                config["host"] = str(st.secrets["SMTP_HOST"]).strip()
            if "SMTP_PORT" in st.secrets:
                config["port"] = int(st.secrets["SMTP_PORT"])

            # Nested [smtp] table fallback
            if "smtp" in st.secrets:
                s_dict = st.secrets["smtp"]
                config["user"] = str(s_dict.get("user", s_dict.get("email", config["user"]))).strip()
                config["password"] = str(s_dict.get("password", config["password"])).strip()
                config["hr_email"] = str(s_dict.get("hr_email", config["hr_email"])).strip()
                config["host"] = str(s_dict.get("host", config["host"])).strip()
                config["port"] = int(s_dict.get("port", config["port"]))
    except Exception:
        pass

    # 2. If user or password not found from st.secrets, read .streamlit/secrets.toml directly
    if not config["user"] or not config["password"]:
        toml_paths = [
            os.path.join(PROJECT_ROOT, ".streamlit", "secrets.toml"),
            os.path.join(os.path.dirname(PROJECT_ROOT), ".streamlit", "secrets.toml")
        ]
        for p in toml_paths:
            if os.path.exists(p):
                try:
                    with open(p, "rb") as f:
                        data = tomllib.load(f)
                        if "SMTP_EMAIL" in data:
                            config["user"] = str(data["SMTP_EMAIL"]).strip()
                        if "SMTP_APP_PASSWORD" in data:
                            config["password"] = str(data["SMTP_APP_PASSWORD"]).strip()
                        if "HR_EMAIL" in data:
                            config["hr_email"] = str(data["HR_EMAIL"]).strip()
                        if "SMTP_HOST" in data:
                            config["host"] = str(data["SMTP_HOST"]).strip()
                        if "SMTP_PORT" in data:
                            config["port"] = int(data["SMTP_PORT"])
                        if "smtp" in data and isinstance(data["smtp"], dict):
                            s_dict = data["smtp"]
                            config["user"] = str(s_dict.get("user", s_dict.get("email", config["user"]))).strip()
                            config["password"] = str(s_dict.get("password", config["password"])).strip()
                            config["hr_email"] = str(s_dict.get("hr_email", config["hr_email"])).strip()
                    if config["user"] and config["password"]:
                        break
                except Exception:
                    pass

    # 3. Environment variables (allow explicit overrides/mocking)
    if "SMTP_HOST" in os.environ:
        config["host"] = os.environ["SMTP_HOST"]
    if "SMTP_PORT" in os.environ:
        try:
            config["port"] = int(os.environ["SMTP_PORT"])
        except ValueError:
            pass
    if "SMTP_EMAIL" in os.environ:
        config["user"] = os.environ["SMTP_EMAIL"]
    if "SMTP_USER" in os.environ:
        config["user"] = os.environ["SMTP_USER"]
    if "SMTP_APP_PASSWORD" in os.environ:
        config["password"] = os.environ["SMTP_APP_PASSWORD"]
    if "SMTP_PASSWORD" in os.environ:
        config["password"] = os.environ["SMTP_PASSWORD"]
    if "HR_EMAIL" in os.environ:
        config["hr_email"] = os.environ["HR_EMAIL"]

    return config

def send_feedback_notification_email(feedback_data: Dict[str, Any]) -> Tuple[bool, str]:
    """
    Sends an HR notification email containing feedback summary.
    Triggered ONLY upon Employee Feedback submission.
    Gracefully handles unconfigured SMTP without false positive reports.
    """
    cfg = get_smtp_config()
    
    # If SMTP is not configured, do NOT falsely say 'Email sent'
    if not cfg.get("host") or not cfg.get("user") or not cfg.get("password"):
        return False, "Feedback saved successfully, but HR email notification is not configured."

    # Format email body
    is_anon = feedback_data.get("is_anonymous", False)
    submitter = "Anonymous Employee (Identity Confidential)" if is_anon else f"Employee ID #{feedback_data.get('employee_id', 'N/A')}"
    comments = feedback_data.get("comments", "").strip() or "None provided."
    timestamp = feedback_data.get("created_at") or datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    body = f"""Hello HR Team,

A new employee feedback response has been submitted on AttritionSense AI.

Submission Details:
- Date & Time: {timestamp}
- Submitter: {submitter}
- Privacy Status: {"Confidential / Anonymous" if is_anon else "Identified"}

Feedback Summary (1-5 Rating Scale):
- Job Satisfaction: {feedback_data.get('job_satisfaction', 'N/A')}/5
- Work-Life Balance: {feedback_data.get('work_life_balance', 'N/A')}/5
- Manager Support: {feedback_data.get('manager_support', 'N/A')}/5
- Workload Manageability: {feedback_data.get('workload', 'N/A')}/5
- Career Growth Opportunities: {feedback_data.get('career_growth', 'N/A')}/5
- Recognition & Appreciation: {feedback_data.get('recognition', 'N/A')}/5
- Compensation & Benefits Satisfaction: {feedback_data.get('compensation_satisfaction', 'N/A')}/5
- Intention to Stay: {feedback_data.get('intention_to_stay', 'N/A')}/5

Employee Comments:
"{comments}"

---
This automated notification was generated by AttritionSense AI Feedback Management.
Please log in to the HR Portal to view aggregated workplace sentiment analytics.
"""

    try:
        msg = MIMEMultipart()
        msg["From"] = cfg["user"]
        msg["To"] = cfg["hr_email"]
        msg["Subject"] = "New Employee Feedback Received"
        msg.attach(MIMEText(body, "plain"))
        
        with smtplib.SMTP(cfg["host"], cfg["port"], timeout=10) as server:
            server.starttls()
            server.login(cfg["user"], cfg["password"])
            server.send_message(msg)
            
        return True, f"Notification email sent to HR ({cfg['hr_email']})."
    except smtplib.SMTPAuthenticationError:
        return False, "Feedback saved, but HR email notification failed: Gmail authentication error. Please verify your App Password."
    except (smtplib.SMTPConnectError, socket.error, OSError) as e:
        return False, f"Feedback saved, but HR email notification failed: Unable to connect to SMTP server ({type(e).__name__})."
    except Exception as e:
        # Never leak passwords or sensitive tokens
        err_msg = str(e).replace(cfg.get("password", "********"), "********")
        return False, f"Feedback saved, but HR email notification could not be dispatched: {err_msg[:120]}"

def send_test_email(recipient_override: Optional[str] = None) -> Tuple[bool, str]:
    """
    Safe test-email utility for development and verification.
    Never exposes passwords or sensitive tokens.
    """
    cfg = get_smtp_config()
    target_email = recipient_override or cfg["hr_email"]
    
    if not cfg.get("user") or not cfg.get("password"):
        return False, "SMTP is not configured in .streamlit/secrets.toml."
        
    body = f"""Hello,

This is a test notification from AttritionSense AI.

- SMTP Server: {cfg['host']}:{cfg['port']}
- Sender: {cfg['user']}
- Intended HR Recipient: {target_email}
- Status: Connection & STARTTLS authentication successful.

---
AttritionSense AI System Diagnostic
"""
    try:
        msg = MIMEMultipart()
        msg["From"] = cfg["user"]
        msg["To"] = target_email
        msg["Subject"] = "AttritionSense AI - Test Email Notification"
        msg.attach(MIMEText(body, "plain"))
        
        with smtplib.SMTP(cfg["host"], cfg["port"], timeout=15) as server:
            server.starttls()
            server.login(cfg["user"], cfg["password"])
            server.send_message(msg)
            
        return True, f"Test email dispatched successfully to {target_email}."
    except smtplib.SMTPAuthenticationError:
        return False, "Test email failed: Gmail authentication error. Please verify your App Password."
    except Exception as e:
        err_msg = str(e).replace(cfg.get("password", "********"), "********")
        return False, f"Test email failed: {err_msg[:120]}"
