#!/usr/bin/env python3

import hashlib
import json
import uuid
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple
import os

class SecureToken:
    def __init__(self, node_id: str, issuer_token_hash: Optional[str] = None, 
                 issuer_id: Optional[str] = None, token_data: Optional[str] = None):
        if not node_id or not isinstance(node_id, str):
            raise ValueError("Node ID must be a non-empty string")
        if len(node_id) > 64:
            raise ValueError("Node ID must be 64 characters or less")
        if not node_id.replace('_', '').replace('-', '').replace('.', '').isalnum():
            raise ValueError("Node ID must contain only alphanumeric characters, hyphens, underscores, and dots")
        
        self.node_id = node_id
        self.issuer_token_hash = issuer_token_hash
        self.issuer_id = issuer_id
        self.timestamp = datetime.now(timezone.utc).isoformat()
        self.token_id = str(uuid.uuid4())
        self.token_data = token_data or f"token_for_{node_id}"
        self.token_hash = self._generate_token_hash()
    
    def _generate_token_hash(self) -> str:
        token_content = f"{self.node_id}:{self.issuer_token_hash}:{self.issuer_id}:{self.timestamp}:{self.token_id}:{self.token_data}"
        return hashlib.sha256(token_content.encode()).hexdigest()
    
    def to_dict(self) -> Dict:
        return {
            'node_id': self.node_id,
            'issuer_token_hash': self.issuer_token_hash,
            'issuer_id': self.issuer_id,
            'timestamp': self.timestamp,
            'token_id': self.token_id,
            'token_data': self.token_data,
            'token_hash': self.token_hash
        }
    
    @classmethod
    def from_dict(cls, data: Dict):
        token = cls.__new__(cls)
        token.node_id = data['node_id']
        token.issuer_token_hash = data['issuer_token_hash']
        token.issuer_id = data['issuer_id']
        token.timestamp = data['timestamp']
        token.token_id = data['token_id']
        token.token_data = data['token_data']
        token.token_hash = data['token_hash']
        return token

class PKITokenNetwork:
    def __init__(self, storage_dir: str = "token_storage"):
        self.storage_dir = storage_dir
        self.tokens: Dict[str, SecureToken] = {}
        self.master_token: Optional[SecureToken] = None
        self._ensure_storage_dir()
        self._load_tokens()
    
    def _ensure_storage_dir(self):
        os.makedirs(self.storage_dir, exist_ok=True)
    
    def _save_token(self, token: SecureToken):
        filename = f"{self.storage_dir}/{token.node_id}_token.json"
        with open(filename, 'w') as f:
            json.dump(token.to_dict(), f, indent=2)
    
    def _load_tokens(self):
        if not os.path.exists(self.storage_dir):
            return
        
        for filename in os.listdir(self.storage_dir):
            if filename.endswith('_token.json'):
                filepath = os.path.join(self.storage_dir, filename)
                try:
                    with open(filepath, 'r') as f:
                        data = json.load(f)
                        token = SecureToken.from_dict(data)
                        self.tokens[token.node_id] = token
                        if token.issuer_token_hash is None:
                            self.master_token = token
                except Exception as e:
                    print(f"Error loading token from {filename}: {e}")
    
    def create_master_token(self, master_node_id: str) -> SecureToken:
        if self.master_token:
            raise ValueError(f"Master token already exists for node: {self.master_token.node_id}")
        
        if master_node_id in self.tokens:
            raise ValueError(f"Node {master_node_id} already has a token")
        
        try:
            master_token = SecureToken(master_node_id)
            self.master_token = master_token
            self.tokens[master_node_id] = master_token
            self._save_token(master_token)
            return master_token
        except Exception as e:
            raise ValueError(f"Failed to create master token: {str(e)}")
    
    def issue_token(self, issuer_node_id: str, new_node_id: str, token_data: Optional[str] = None) -> SecureToken:
        if not self.master_token:
            raise ValueError("No master token exists. Create a master token first.")
        
        if issuer_node_id not in self.tokens:
            raise ValueError(f"Issuer node {issuer_node_id} not found")
        
        if issuer_node_id == new_node_id:
            raise ValueError("Issuer and new node cannot be the same")
        
        if new_node_id in self.tokens:
            raise ValueError(f"Node {new_node_id} already has a token")
        
        try:
            issuer_token = self.tokens[issuer_node_id]
            new_token = SecureToken(
                node_id=new_node_id,
                issuer_token_hash=issuer_token.token_hash,
                issuer_id=issuer_node_id,
                token_data=token_data
            )
            
            self.tokens[new_node_id] = new_token
            self._save_token(new_token)
            return new_token
        except Exception as e:
            raise ValueError(f"Failed to issue token: {str(e)}")
    
    def verify_token(self, node_id: str) -> Tuple[bool, List[str]]:
        if node_id not in self.tokens:
            return False, [f"Token for node {node_id} not found"]
        
        chain = []
        current_token = self.tokens[node_id]
        
        while current_token:
            chain.append(f"{current_token.node_id} -> {current_token.token_hash[:16]}...")
            
            if current_token.issuer_token_hash is None:
                if current_token == self.master_token:
                    return True, chain
                else:
                    return False, chain + ["Invalid master token"]
            
            if current_token.issuer_id not in self.tokens:
                return False, chain + [f"Issuer {current_token.issuer_id} not found"]
            
            issuer_token = self.tokens[current_token.issuer_id]
            if issuer_token.token_hash != current_token.issuer_token_hash:
                return False, chain + ["Hash chain broken - issuer token hash mismatch"]
            
            current_token = issuer_token
        
        return False, chain + ["Unexpected end of chain"]
    
    def get_token_info(self, node_id: str) -> Optional[Dict]:
        if node_id in self.tokens:
            return self.tokens[node_id].to_dict()
        return None
    
    def list_all_tokens(self) -> List[Dict]:
        return [token.to_dict() for token in self.tokens.values()]