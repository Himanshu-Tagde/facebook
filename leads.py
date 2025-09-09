import requests
from datetime import datetime
from typing import Dict, List, Any

from config import FACEBOOK_GRAPH_URL
from models import get_client_token, client_exists

async def get_facebook_leads(client_id: str, limit: int = 25) -> Dict[str, Any]:
    """Retrieve Facebook leads for a client"""
    if not client_exists(client_id):
        return {"error": "Client not connected"}
    
    client_token = get_client_token(client_id)
    access_token = client_token["access_token"]
    
    # Get ad accounts
    accounts_response = requests.get(
        f"{FACEBOOK_GRAPH_URL}/me/adaccounts?access_token={access_token}"
    )
    
    if accounts_response.status_code != 200:
        return {"error": "Failed to fetch ad accounts", "details": accounts_response.text}
    
    accounts_data = accounts_response.json()
    leads_data = []
    
    # Loop through accounts → forms → leads
    for account in accounts_data.get("data", []):
        account_id = account["id"]
        forms_response = requests.get(
            f"{FACEBOOK_GRAPH_URL}/{account_id}/leadgen_forms?access_token={access_token}"
        )
        
        if forms_response.status_code != 200:
            continue
        
        for form in forms_response.json().get("data", []):
            form_id = form["id"]
            form_name = form.get("name", "Unnamed Form")
            
            leads_response = requests.get(
                f"{FACEBOOK_GRAPH_URL}/{form_id}/leads?access_token={access_token}&limit={limit}"
            )
            
            if leads_response.status_code == 200:
                for lead in leads_response.json().get("data", []):
                    leads_data.append({
                        "lead_id": lead.get("id"),
                        "form_id": form_id,
                        "form_name": form_name,
                        "created_time": lead.get("created_time"),
                        "field_data": lead.get("field_data", [])
                    })
    
    return {
        "client_id": client_id,
        "total_leads": len(leads_data),
        "leads": leads_data,
        "retrieved_at": datetime.now().isoformat()
    }
