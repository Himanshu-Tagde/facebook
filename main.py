import uvicorn
import threading
import time
import sys
import uuid
from fastapi import FastAPI

from config import HOST, PORT, get_oauth_url, FACEBOOK_APP_ID
from routes import setup_routes
from terminal import terminal_interface

app = FastAPI()

# Setup all routes
setup_routes(app)

def start_server():
    """Start the FastAPI server"""
    uvicorn.run(app, host=HOST, port=PORT, reload=False)

def print_startup_info():
    """Print startup information"""
    client_id = "test_client"
    oauth_url = get_oauth_url(client_id, f"{client_id}_{uuid.uuid4().hex}")
    
    print("=" * 80)
    print("🚀 Facebook CRM Integration Server with Terminal Messaging")
    print(f"📱 Running at http://{HOST}:{PORT}")
    print(f"🔗 Direct Login URL for '{client_id}':\n{oauth_url}")
    print("\n📋 Available endpoints:")
    print(" • GET /terminal/pages - List pages for terminal")
    print(" • GET /terminal/conversations/{page_id} - List conversations for terminal")
    print(" • POST /messages/{page_id}/send - Send message")
    print(" • All previous endpoints still available")
    print("=" * 80)

if __name__ == "__main__":
    print_startup_info()
    
    # Start server in background thread
    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()
    
    # Wait for server to start
    time.sleep(2)
    
    # Start terminal interface
    try:
        terminal_interface()
    except KeyboardInterrupt:
        print("\n👋 Server shutting down...")
        sys.exit(0)
