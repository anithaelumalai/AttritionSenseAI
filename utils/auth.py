import hashlib
import secrets
import hmac
from typing import Tuple, Optional, Dict, Any
import streamlit as st
from utils.database import get_connection

def hash_password(password: str, salt: Optional[str] = None) -> Tuple[str, str]:
    """Generates a secure PBKDF2-HMAC-SHA256 password hash and salt."""
    if salt is None:
        salt = secrets.token_hex(16)
    iterations = 100_000
    key = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt.encode('utf-8'), iterations)
    return key.hex(), salt

def verify_password(password: str, stored_hash: str, salt: str) -> bool:
    """Verifies a plain text password against a stored PBKDF2 hash and salt."""
    computed_hash, _ = hash_password(password, salt)
    return hmac.compare_digest(computed_hash, stored_hash)

def authenticate_user(identifier: str, password: str, expected_role: Optional[str] = None) -> Tuple[bool, Optional[Dict[str, Any]], str]:
    """
    Authenticates a user against the SQLite users table.
    Ensures strict role separation.
    """
    identifier_str = str(identifier).strip()
    if not identifier_str or not password:
        return False, None, "Identifier and password are required."
        
    conn = get_connection()
    cur = conn.cursor()
    
    if expected_role:
        cur.execute("SELECT * FROM users WHERE identifier = ? AND role = ?", (identifier_str, expected_role))
    else:
        cur.execute("SELECT * FROM users WHERE identifier = ?", (identifier_str,))
        
    user = cur.fetchone()
    conn.close()
    
    if not user:
        if expected_role == "employee":
            return False, None, f"Employee ID '{identifier_str}' not found. Please check your Employee ID."
        elif expected_role == "hr":
            return False, None, "Invalid HR credentials."
        return False, None, "User not found."
        
    user_dict = dict(user)
    if verify_password(password, user_dict["password_hash"], user_dict["salt"]):
        # Do not expose password hash outside auth
        user_dict.pop("password_hash", None)
        user_dict.pop("salt", None)
        return True, user_dict, "Authentication successful."
    else:
        return False, None, "Incorrect password. Please try again."

def authenticate_employee(employee_id: str, password: str) -> Tuple[bool, Optional[Dict[str, Any]], str]:
    """Authenticates an Employee using Employee ID and password."""
    return authenticate_user(employee_id, password, expected_role="employee")

def authenticate_hr(username: str, password: str) -> Tuple[bool, Optional[Dict[str, Any]], str]:
    """Authenticates an HR professional using HR Username/ID and password."""
    return authenticate_user(username, password, expected_role="hr")

def update_password(identifier: str, new_password: str) -> bool:
    """Updates password for a given user."""
    if len(new_password) < 4:
        return False
    pwd_hash, salt = hash_password(new_password)
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "UPDATE users SET password_hash = ?, salt = ? WHERE identifier = ?",
        (pwd_hash, salt, str(identifier).strip())
    )
    affected = cur.rowcount
    conn.commit()
    conn.close()
    return affected > 0

# --- Streamlit Session State Management ---

def init_session():
    """Initializes standard session state keys if not already set."""
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    if "user_role" not in st.session_state:
        st.session_state.user_role = None  # 'employee' or 'hr'
    if "user_id" not in st.session_state:
        st.session_state.user_id = None
    if "employee_data" not in st.session_state:
        st.session_state.employee_data = None
    if "active_page" not in st.session_state:
        st.session_state.active_page = "login"

def login_session(user_dict: Dict[str, Any], employee_data: Optional[Dict[str, Any]] = None):
    """Sets session state upon successful authentication."""
    st.session_state.authenticated = True
    st.session_state.user_role = user_dict["role"]
    st.session_state.user_id = user_dict["identifier"]
    st.session_state.employee_data = employee_data
    if user_dict["role"] == "employee":
        st.session_state.active_page = "employee_dashboard"
    else:
        st.session_state.active_page = "hr_dashboard"

def logout_session():
    """Clears authentication session state."""
    st.session_state.authenticated = False
    st.session_state.user_role = None
    st.session_state.user_id = None
    st.session_state.employee_data = None
    st.session_state.active_page = "landing"

def is_authenticated() -> bool:
    return st.session_state.get("authenticated", False)

def get_role() -> Optional[str]:
    return st.session_state.get("user_role")

def get_user_id() -> Optional[str]:
    return st.session_state.get("user_id")

def is_employee() -> bool:
    return is_authenticated() and get_role() == "employee"

def is_hr() -> bool:
    return is_authenticated() and get_role() == "hr"
