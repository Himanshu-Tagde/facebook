from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import RedirectResponse

from auth import generate_oauth_url, handle_oauth_callback
from messaging import get_conversations, get_messages, send_message
from leads import get_facebook_leads
from webhook import verify_webhook, handle_webhook
from debug import debug_page_setup
from models import get_client_token, client_exists, page_tokens

def setup_routes(app: FastAPI):
    """Set up all API routes"""
    
    @app.get("/")
    async def root():
        return {"message": "Facebook CRM Integration Server with Terminal Messaging - Running!"}
    
    @app.get("/login/{client_id}")
    async def facebook_login_direct(client_id: str):
        """Redirect client to Facebook OAuth"""
        oauth_url = generate_oauth_url(client_id)
        return RedirectResponse(url=oauth_url, status_code=307)
    
    @app.get("/auth/facebook/callback")
    async def facebook_callback(request: Request):
        """Handle Facebook OAuth callback"""
        return await handle_oauth_callback(request)
    
    @app.get("/pages/{client_id}")
    async def get_client_pages(client_id: str):
        """Get all pages for a client"""
        if not client_exists(client_id):
            return {"error": "Client not connected"}
        
        client_token = get_client_token(client_id)
        return {
            "client_id": client_id,
            "pages": client_token.get("pages", [])
        }
    
    @app.get("/conversations/{page_id}")
    async def get_page_conversations_with_psids(page_id: str):
        """Get conversations with PSIDs"""
        return await get_conversations(page_id)
    
    @app.get("/messages/{page_id}")
    async def get_page_messages(page_id: str, limit: int = 25):
        """Get messages for a page"""
        return await get_messages(page_id, limit)
    
    @app.post("/messages/{page_id}/send")
    async def send_page_message(page_id: str, request: Request):
        """Send message from Facebook page"""
        return await send_message(page_id, request)
    
    @app.get("/terminal/pages")
    async def list_pages_for_terminal():
        """List pages for terminal interface"""
        if not page_tokens:
            return {"error": "No pages connected. Please complete OAuth first."}
        
        pages_list = []
        for page_id, page_data in page_tokens.items():
            pages_list.append({
                "page_id": page_id,
                "page_name": page_data["name"],
                "client_id": page_data["client_id"]
            })
        
        return {"pages": pages_list}
    
    @app.get("/terminal/conversations/{page_id}")
    async def list_conversations_for_terminal(page_id: str):
        """List conversations for terminal"""
        if page_id not in page_tokens:
            return {"error": "Page not found"}
        
        conversations_data = await get_conversations(page_id)
        if "error" in conversations_data:
            return conversations_data
        
        terminal_conversations = []
        for i, conv in enumerate(conversations_data["conversations"], 1):
            terminal_conversations.append({
                "index": i,
                "name": conv["participant_name"],
                "psid": conv["participant_psid"],
                "last_updated": conv["updated_time"],
                "message_count": conv["message_count"]
            })
        
        return {
            "page_name": conversations_data["page_name"],
            "conversations": terminal_conversations
        }
    
    @app.get("/leads/{client_id}")
    async def get_leads(client_id: str, limit: int = 25):
        """Get Facebook leads"""
        return await get_facebook_leads(client_id, limit)
    
    @app.get("/debug/{page_id}")
    async def debug_page(page_id: str):
        """Debug page setup"""
        return await debug_page_setup(page_id)
    
    @app.get("/webhook")
    async def webhook_verify(request: Request):
        """Verify webhook"""
        return await verify_webhook(request)
    
    @app.post("/webhook")
    async def webhook_receive(request: Request):
        """Handle webhook"""
        return await handle_webhook(request)
