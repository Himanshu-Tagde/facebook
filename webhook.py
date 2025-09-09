import json
from fastapi import Request, HTTPException
from typing import Dict, Any

from config import WEBHOOK_VERIFY_TOKEN

async def verify_webhook(request: Request) -> int:
    """Verify Facebook webhook"""
    mode = request.query_params.get("hub.mode")
    token = request.query_params.get("hub.verify_token")
    challenge = request.query_params.get("hub.challenge")
    
    print(f"🔍 Webhook verification: mode={mode}, token={token}")
    
    if mode == "subscribe" and token == WEBHOOK_VERIFY_TOKEN:
        print("✅ Webhook verified successfully!")
        return int(challenge)
    else:
        print("❌ Webhook verification failed!")
        raise HTTPException(status_code=403, detail="Forbidden")

async def handle_webhook(request: Request) -> Dict[str, Any]:
    """Handle incoming webhook messages"""
    try:
        body = await request.json()
        print(f"\n📨 Webhook received: {json.dumps(body, indent=2)}")
        
        # Process webhook data
        if body.get("object") == "page":
            for entry in body.get("entry", []):
                page_id = entry.get("id")
                
                # Handle messages
                for messaging in entry.get("messaging", []):
                    sender_id = messaging.get("sender", {}).get("id")
                    message_data = messaging.get("message", {})
                    
                    if message_data:
                        message_text = message_data.get("text", "No text")
                        print(f"💬 New message from {sender_id} to page {page_id}")
                        print(f"Message: {message_text}")
                        print(f"🆔 Sender PSID: {sender_id} (use this for replies)")
        
        return {"status": "EVENT_RECEIVED"}
    
    except Exception as e:
        print(f"❌ Webhook processing error: {str(e)}")
        return {"status": "ERROR", "message": str(e)}
