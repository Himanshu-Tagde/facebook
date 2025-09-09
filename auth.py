import requests
import uuid
from datetime import datetime
from fastapi import Request, HTTPException
from fastapi.responses import RedirectResponse
from typing import Dict, Any

from config import *
from models import *

def generate_oauth_url(client_id: str) -> str:
    """Generate Facebook OAuth URL for client"""
    state = f"{client_id}_{uuid.uuid4().hex}"
    oauth_url = get_oauth_url(client_id, state)
    print(f"\n🔗 Direct Facebook OAuth URL for {client_id}: {oauth_url}")
    return oauth_url

async def handle_oauth_callback(request: Request) -> Dict[str, Any]:
    """Handle Facebook OAuth callback"""
    code = request.query_params.get("code")
    state = request.query_params.get("state")
    error = request.query_params.get("error")
    
    print("\n📥 Callback received from Facebook")
    
    if error:
        print(f"❌ Error: {error}")
        return {"error": f"Facebook authorization failed: {error}"}
    
    if not code or not state:
        print("❌ Missing code or state")
        return {"error": "Missing code or state parameter"}
    
    # Extract client_id from state
    client_id = state.split("_")[0]
    print(f"👤 Client ID: {client_id}")
    
    # Exchange code for access token
    access_token = await exchange_code_for_token(code)
    if not access_token:
        return {"error": "Failed to exchange token"}
    
    # Get user profile
    profile = await get_user_profile(access_token)
    
    # Get user's pages
    pages_data = await get_user_pages(access_token, client_id)
    
    # Store tokens
    client_token = ClientToken(
        access_token=access_token,
        profile=profile,
        pages=pages_data,
        connected_at=datetime.now().isoformat()
    )
    store_client_token(client_id, client_token)
    
    print(f"✅ Token stored for client {client_id}")
    print(f"👤 Profile: {profile}")
    print(f"📄 Pages: {len(pages_data)} pages found")
    
    # Print page links
    print_page_links(pages_data)
    
    return {
        "message": "🎉 Facebook connected successfully!",
        "client_id": client_id,
        "profile": profile.__dict__,
        "pages": [page.__dict__ for page in pages_data],
        "token_saved": True,
        "leads_url": f"http://localhost:8000/leads/{client_id}",
        "message_links": [f"http://localhost:8000/messages/{page.id}" for page in pages_data]
    }

async def exchange_code_for_token(code: str) -> Optional[str]:
    """Exchange authorization code for access token"""
    print("🔄 Exchanging code for access token...")
    
    token_response = requests.get(
        f"{FACEBOOK_GRAPH_URL}/oauth/access_token?"
        f"client_id={FACEBOOK_APP_ID}&"
        f"redirect_uri={REDIRECT_URI}&"
        f"client_secret={FACEBOOK_APP_SECRET}&"
        f"code={code}"
    )
    
    if token_response.status_code != 200:
        print(f"❌ Token exchange failed: {token_response.text}")
        return None
    
    token_data = token_response.json()
    return token_data["access_token"]

async def get_user_profile(access_token: str) -> FacebookProfile:
    """Get user profile information"""
    profile_response = requests.get(
        f"{FACEBOOK_GRAPH_URL}/me?fields=id,name,email&access_token={access_token}"
    )
    
    if profile_response.status_code == 200:
        profile_data = profile_response.json()
        return FacebookProfile(
            id=profile_data.get("id"),
            name=profile_data.get("name"),
            email=profile_data.get("email")
        )
    return FacebookProfile(id="", name="Unknown")

async def get_user_pages(access_token: str, client_id: str) -> List[FacebookPage]:
    """Get user's Facebook pages"""
    pages_response = requests.get(
        f"{FACEBOOK_GRAPH_URL}/me/accounts?access_token={access_token}"
    )
    
    pages_data = []
    if pages_response.status_code == 200:
        pages_info = pages_response.json()
        for page in pages_info.get("data", []):
            page_id = page["id"]
            page_access_token = page["access_token"]
            page_name = page.get("name")
            
            # Store page token
            page_token = PageToken(
                access_token=page_access_token,
                name=page_name,
                client_id=client_id
            )
            store_page_token(page_id, page_token)
            
            pages_data.append(FacebookPage(
                id=page_id,
                name=page_name,
                access_token=page_access_token
            ))
    
    return pages_data

def print_page_links(pages_data: List[FacebookPage]):
    """Print direct page message links"""
    print("\n📱 DIRECT PAGE MESSAGE LINKS:")
    print("=" * 80)
    for page in pages_data:
        print(f"📄 Page: {page.name} ({page.id})")
        print(f" 📥 Get Messages: http://localhost:8000/messages/{page.id}")
        print(f" 📝 Get Conversations: http://localhost:8000/conversations/{page.id}")
        print(f" 📤 Send Message: http://localhost:8000/messages/{page.id}/send")
        print(f" 🔍 Debug Page: http://localhost:8000/debug/{page.id}")
        print("-" * 80)
