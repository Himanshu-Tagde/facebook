import json
import requests
from typing import Dict, Any

from config import FACEBOOK_GRAPH_URL
from models import get_page_token, page_exists

async def debug_page_setup(page_id: str) -> Dict[str, Any]:
    """Debug page messaging setup"""
    if not page_exists(page_id):
        return {"error": "Page not found"}
    
    page_token = get_page_token(page_id)
    page_access_token = page_token["access_token"]
    
    # Test page access
    page_info = requests.get(
        f"{FACEBOOK_GRAPH_URL}/{page_id}?fields=name,id&access_token={page_access_token}"
    )
    
    # Test permissions
    permissions = requests.get(
        f"{FACEBOOK_GRAPH_URL}/me/permissions?access_token={page_access_token}"
    )
    
    # Test messaging features
    page_messaging_test = requests.get(
        f"{FACEBOOK_GRAPH_URL}/{page_id}?fields=name,messaging_feature_status&access_token={page_access_token}"
    )
    
    debug_info = {
        "page_id": page_id,
        "page_name": page_token["name"],
        "token_exists": page_access_token is not None,
        "page_info": page_info.json() if page_info.status_code == 200 else {"error": page_info.text},
        "permissions": permissions.json() if permissions.status_code == 200 else {"error": permissions.text},
        "messaging_status": page_messaging_test.json() if page_messaging_test.status_code == 200 else {"error": page_messaging_test.text}
    }
    
    print(f"🔍 Debug info for page {page_id}:")
    print(json.dumps(debug_info, indent=2))
    
    return debug_info
