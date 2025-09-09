import requests
from typing import Dict, Any

def terminal_interface():
    """Interactive terminal interface for sending messages"""
    print("\n" + "="*60)
    print("🔥 FACEBOOK MESSENGER TERMINAL INTERFACE")
    print("="*60)
    
    while True:
        try:
            print("\n📋 Available Commands:")
            print("1. List Pages")
            print("2. List Conversations")
            print("3. Send Message")
            print("4. Exit")
            
            choice = input("\n👉 Enter your choice (1-4): ").strip()
            
            if choice == "1":
                list_pages()
            elif choice == "2":
                list_conversations()
            elif choice == "3":
                send_message_terminal()
            elif choice == "4":
                print("👋 Goodbye!")
                break
            else:
                print("❌ Invalid choice. Please enter 1-4.")
                
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {str(e)}")

def list_pages():
    """List available pages"""
    response = requests.get("http://localhost:8000/terminal/pages")
    if response.status_code == 200:
        data = response.json()
        if "pages" in data:
            print("\n📄 Available Pages:")
            for i, page in enumerate(data["pages"], 1):
                print(f"{i}. {page['page_name']} (ID: {page['page_id']})")
        else:
            print(f"❌ {data.get('error', 'No pages found')}")
    else:
        print("❌ Failed to fetch pages")

def list_conversations():
    """List conversations for a page"""
    page_id = input("📄 Enter Page ID: ").strip()
    if page_id:
        response = requests.get(f"http://localhost:8000/terminal/conversations/{page_id}")
        if response.status_code == 200:
            data = response.json()
            if "conversations" in data:
                print(f"\n💬 Conversations for {data['page_name']}:")
                for conv in data["conversations"]:
                    print(f"{conv['index']}. {conv['name']} (PSID: {conv['psid']}) - {conv['message_count']} messages")
            else:
                print(f"❌ {data.get('error', 'No conversations found')}")
        else:
            print("❌ Failed to fetch conversations")

def send_message_terminal():
    """Send message through terminal"""
    page_id = input("📄 Enter Page ID: ").strip()
    recipient_psid = input("👤 Enter Recipient PSID: ").strip()
    message = input("💬 Enter Message: ").strip()
    
    if page_id and recipient_psid and message:
        payload = {
            "recipient_id": recipient_psid,
            "message": message
        }
        
        response = requests.post(
            f"http://localhost:8000/messages/{page_id}/send",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                print(f"✅ Message sent successfully!")
                print(f"📤 Message: {result['message_sent']}")
                print(f"🆔 Message ID: {result['message_id']}")
            else:
                print(f"❌ Failed to send: {result}")
        else:
            print(f"❌ HTTP Error {response.status_code}: {response.text}")
    else:
        print("❌ All fields are required!")
