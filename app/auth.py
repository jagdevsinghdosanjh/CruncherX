import streamlit as st
import firebase_admin
from firebase_admin import credentials, auth
import json

@st.cache_resource
def init_firebase():
    if not firebase_admin._apps:
        firebase_config = st.secrets["FIREBASE"]
        cred = credentials.Certificate({
            "type": "service_account",
            "project_id": firebase_config["projectId"],
            "private_key_id": firebase_config.get("private_key_id", ""),
            "private_key": firebase_config.get("private_key", "").replace("\\n", "\n"),
            "client_email": firebase_config.get("client_email", ""),
            "client_id": firebase_config.get("client_id", ""),
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "client_x509_cert_url": firebase_config.get("client_x509_cert_url", "")
        })
        firebase_admin.initialize_app(cred)
    return firebase_admin.get_app()

def get_current_user():
    user_json = st.session_state.get("user")
    if not user_json:
        return None
    return json.loads(user_json)

def set_current_user(user_info: dict):
    st.session_state["user"] = json.dumps(user_info)

def logout():
    if "user" in st.session_state:
        del st.session_state["user"]
