import os
from typing import Dict, Any

# Facebook OAuth configuration
FACEBOOK_APP_ID = ""
FACEBOOK_APP_SECRET = ""
REDIRECT_URI = "http://localhost:8000/auth/facebook/callback"
WEBHOOK_VERIFY_TOKEN = "crmsecret123"

# Server configuration
HOST = "127.0.0.1"
PORT = 8000

# Facebook API configuration
FACEBOOK_API_VERSION = "v18.0"
FACEBOOK_GRAPH_URL = f"https://graph.facebook.com/{FACEBOOK_API_VERSION}"
FACEBOOK_OAUTH_URL = f"https://www.facebook.com/{FACEBOOK_API_VERSION}/dialog/oauth"

# OAuth scopes
FACEBOOK_SCOPES = [
    "pages_messaging",
    "pages_show_list", 
    "pages_manage_metadata",
    "pages_read_engagement",
    "pages_read_user_content",
    "email",
    "public_profile",
    "ads_management",
    "ads_read",
    "leads_retrieval"
]

def get_oauth_url(client_id: str, state: str) -> str:
    """Generate Facebook OAuth URL"""
    scope_string = ",".join(FACEBOOK_SCOPES)
    return (
        f"{FACEBOOK_OAUTH_URL}?"
        f"client_id={FACEBOOK_APP_ID}&"
        f"redirect_uri={REDIRECT_URI}&"
        f"state={state}&"
        f"scope={scope_string}&"
        f"response_type=code"
    )

