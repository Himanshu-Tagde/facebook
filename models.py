from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict

# In-memory storage (replace with database in production)
client_tokens: Dict[str, Any] = {}
page_tokens: Dict[str, Any] = {}

@dataclass
class FacebookProfile:
    id: str
    name: str
    email: Optional[str] = None

@dataclass
class FacebookPage:
    id: str
    name: str
    access_token: str

@dataclass
class ClientToken:
    access_token: str
    profile: FacebookProfile
    pages: List[FacebookPage]
    connected_at: str

@dataclass 
class PageToken:
    access_token: str
    name: str
    client_id: str

@dataclass
class Conversation:
    conversation_id: str
    participant_psid: str
    participant_name: str
    updated_time: str
    message_count: int
    unread_count: int

@dataclass
class Message:
    conversation_id: str
    message_id: str
    created_time: str
    from_data: Dict[str, Any]
    to_data: Dict[str, Any]
    message: str
    participants: List[Dict[str, Any]]

def store_client_token(client_id: str, token_data: ClientToken):
    """Store client token data"""
    client_tokens[client_id] = asdict(token_data)

def store_page_token(page_id: str, token_data: PageToken):
    """Store page token data"""
    page_tokens[page_id] = asdict(token_data)

def get_client_token(client_id: str) -> Optional[Dict[str, Any]]:
    """Get client token data"""
    return client_tokens.get(client_id)

def get_page_token(page_id: str) -> Optional[Dict[str, Any]]:
    """Get page token data"""
    return page_tokens.get(page_id)

def client_exists(client_id: str) -> bool:
    """Check if client exists"""
    return client_id in client_tokens

def page_exists(page_id: str) -> bool:
    """Check if page exists"""
    return page_id in page_tokens
