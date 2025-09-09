import requests
from datetime import datetime
from fastapi import HTTPException, Request
from typing import Dict, List, Any

from config import FACEBOOK_GRAPH_URL
from models import get_page_token, page_exists, Conversation, Message

async def get_conversations(page_id: str) -> Dict[str, Any]:
    """Get conversations for a page"""
    if not page_exists(page_id):
        raise HTTPException(status_code=404, detail="Page not found or not authorized")
    
    page_token = get_page_token(page_id)
    page_access_token = page_token["access_token"]
    
    conversations_response = requests.get(
        f"{FACEBOOK_GRAPH_URL}/{page_id}/conversations?"
        f"fields=participants,updated_time,message_count,unread_count&"
        f"access_token={page_access_token}"
    )
    
    if conversations_response.status_code != 200:
        return {"error": "Failed to fetch conversations", "details": conversations_response.text}
    
    conversations = []
    for conversation in conversations_response.json().get("data", []):
        participants = conversation.get("participants", {}).get("data", [])
        for participant in participants:
            if participant.get("id") != page_id:  # Exclude the page itself
                conversations.append({
                    "conversation_id": conversation["id"],
                    "participant_psid": participant.get("id"),
                    "participant_name": participant.get("name", "Unknown"),
                    "updated_time": conversation.get("updated_time"),
                    "message_count": conversation.get("message_count", 0),
                    "unread_count": conversation.get("unread_count", 0)
                })
    
    print(f"📝 Found {len(conversations)} conversations for page {page_token['name']}")
    
    return {
        "page_id": page_id,
        "page_name": page_token["name"],
        "total_conversations": len(conversations),
        "conversations": conversations
    }

async def get_messages(page_id: str, limit: int = 25) -> Dict[str, Any]:
    """Get messages for a page"""
    if not page_exists(page_id):
        raise HTTPException(status_code=404, detail="Page not found or not authorized")
    
    page_token = get_page_token(page_id)
    page_access_token = page_token["access_token"]
    
    # Get conversations
    conversations_response = requests.get(
        f"{FACEBOOK_GRAPH_URL}/{page_id}/conversations?"
        f"fields=participants,updated_time,message_count,unread_count&"
        f"limit={limit}&"
        f"access_token={page_access_token}"
    )
    
    if conversations_response.status_code != 200:
        return {"error": "Failed to fetch conversations", "details": conversations_response.text}
    
    conversations_data = conversations_response.json()
    messages_data = []
    
    # Get messages for each conversation
    for conversation in conversations_data.get("data", []):
        conversation_id = conversation["id"]
        messages_response = requests.get(
            f"{FACEBOOK_GRAPH_URL}/{conversation_id}/messages?"
            f"fields=id,created_time,from,to,message&"
            f"limit=50&"
            f"access_token={page_access_token}"
        )
        
        if messages_response.status_code == 200:
            messages = messages_response.json().get("data", [])
            for msg in messages:
                messages_data.append({
                    "conversation_id": conversation_id,
                    "message_id": msg.get("id"),
                    "created_time": msg.get("created_time"),
                    "from": msg.get("from"),
                    "to": msg.get("to"),
                    "message": msg.get("message"),
                    "participants": conversation.get("participants", {}).get("data", [])
                })
    
    # Sort messages chronologically
    messages_data_sorted = sorted(messages_data, key=lambda x: x["created_time"] if x["created_time"] else "")
    
    return {
        "page_id": page_id,
        "page_name": page_token["name"],
        "total_conversations": len(conversations_data.get("data", [])),
        "total_messages": len(messages_data_sorted),
        "messages": messages_data_sorted,
        "retrieved_at": datetime.now().isoformat()
    }

async def send_message(page_id: str, request: Request) -> Dict[str, Any]:
    """Send message from Facebook page"""
    if not page_exists(page_id):
        raise HTTPException(status_code=404, detail="Page not found or not authorized")
    
    data = await request.json()
    recipient_psid = data.get("recipient_id")
    message_text = data.get("message")
    
    if not recipient_psid or not message_text:
        raise HTTPException(status_code=400, detail="recipient_id (PSID) and message are required")
    
    page_token = get_page_token(page_id)
    page_access_token = page_token["access_token"]
    
    # Prepare message payload
    message_payload = {
        "recipient": {"id": recipient_psid},
        "message": {"text": message_text},
        "messaging_type": "RESPONSE"
    }
    
    print(f"\n📤 Attempting to send message:")
    print(f" Page: {page_token['name']} ({page_id})")
    print(f" To PSID: {recipient_psid}")
    print(f" Message: {message_text}")
    
    # Send message
    send_response = requests.post(
        f"{FACEBOOK_GRAPH_URL}/me/messages",
        json=message_payload,
        params={"access_token": page_access_token}
    )
    
    print(f"📊 Response Status: {send_response.status_code}")
    print(f"📋 Response Body: {send_response.text}")
    
    if send_response.status_code != 200:
        error_details = send_response.json() if send_response.text else "No error details"
        print(f"❌ Send failed: {error_details}")
        return {
            "error": "Failed to send message",
            "status_code": send_response.status_code,
            "details": error_details,
            "page_id": page_id,
            "recipient_psid": recipient_psid
        }
    
    response_data = send_response.json()
    message_id = response_data.get("message_id")
    print(f"✅ Message sent successfully! Message ID: {message_id}")
    
    return {
        "success": True,
        "message_sent": message_text,
        "recipient_psid": recipient_psid,
        "page_id": page_id,
        "page_name": page_token["name"],
        "message_id": message_id,
        "sent_at": datetime.now().isoformat()
    }
