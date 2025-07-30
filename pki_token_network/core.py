#!/usr/bin/env python3

import hashlib
import json
import uuid
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple, Set
import os
import base64
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.serialization import load_pem_private_key, load_pem_public_key

class SecureToken:
    def __init__(self, node_id: str, issuer_token_hash: Optional[str] = None, 
                 issuer_id: Optional[str] = None, token_data: Optional[str] = None,
                 master_id: Optional[str] = None, hierarchy_level: int = 0):
        if not node_id or not isinstance(node_id, str):
            raise ValueError("Node ID must be a non-empty string")
        if len(node_id) > 64:
            raise ValueError("Node ID must be 64 characters or less")
        if not node_id.replace('_', '').replace('-', '').replace('.', '').isalnum():
            raise ValueError("Node ID must contain only alphanumeric characters, hyphens, underscores, and dots")
        
        # Original fields for backward compatibility
        self.node_id = node_id
        self.issuer_token_hash = issuer_token_hash
        self.issuer_id = issuer_id
        self.timestamp = datetime.now(timezone.utc).isoformat()
        self.token_id = str(uuid.uuid4())
        self.token_data = token_data or f"token_for_{node_id}"
        
        # Enhanced hierarchical verification fields
        self.master_id = master_id or (node_id if issuer_token_hash is None else None)
        self.hierarchy_level = hierarchy_level
        self.master_signature: Optional[str] = None
        self.issuer_signature: Optional[str] = None
        self.delegation_proof: Optional[str] = None
        self.merkle_proof: Optional[Dict] = None
        self.verification_paths: Set[str] = {"chain"}  # Available verification methods
        
        # Generate token hash (must be last)
        self.token_hash = self._generate_token_hash()
    
    def _generate_token_hash(self) -> str:
        token_content = f"{self.node_id}:{self.issuer_token_hash}:{self.issuer_id}:{self.timestamp}:{self.token_id}:{self.token_data}"
        return hashlib.sha256(token_content.encode()).hexdigest()
    
    def to_dict(self) -> Dict:
        return {
            # Original fields for backward compatibility
            'node_id': self.node_id,
            'issuer_token_hash': self.issuer_token_hash,
            'issuer_id': self.issuer_id,
            'timestamp': self.timestamp,
            'token_id': self.token_id,
            'token_data': self.token_data,
            'token_hash': self.token_hash,
            
            # Enhanced hierarchical verification fields
            'master_id': self.master_id,
            'hierarchy_level': self.hierarchy_level,
            'master_signature': self.master_signature,
            'issuer_signature': self.issuer_signature,
            'delegation_proof': self.delegation_proof,
            'merkle_proof': self.merkle_proof,
            'verification_paths': list(self.verification_paths)
        }
    
    @classmethod
    def from_dict(cls, data: Dict):
        token = cls.__new__(cls)
        # Original fields
        token.node_id = data['node_id']
        token.issuer_token_hash = data['issuer_token_hash']
        token.issuer_id = data['issuer_id']
        token.timestamp = data['timestamp']
        token.token_id = data['token_id']
        token.token_data = data['token_data']
        token.token_hash = data['token_hash']
        
        # Enhanced fields (with defaults for backward compatibility)
        token.master_id = data.get('master_id', token.node_id if token.issuer_token_hash is None else None)
        token.hierarchy_level = data.get('hierarchy_level', 0)
        token.master_signature = data.get('master_signature')
        token.issuer_signature = data.get('issuer_signature')
        token.delegation_proof = data.get('delegation_proof')
        token.merkle_proof = data.get('merkle_proof')
        token.verification_paths = set(data.get('verification_paths', ['chain']))
        
        return token
    
    def add_master_signature(self, master_private_key, master_id: str):
        """Add master signature to token for direct verification"""
        if not master_private_key:
            return
        
        # Create content to sign (excludes the signature itself)
        sign_content = f"{self.node_id}:{self.token_hash}:{master_id}:{self.timestamp}"
        
        try:
            signature = master_private_key.sign(
                sign_content.encode(),
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            self.master_signature = base64.b64encode(signature).decode('utf-8')
            self.master_id = master_id
            self.verification_paths.add("master-direct")
        except Exception as e:
            # Graceful degradation - token still works with chain verification
            pass
    
    def add_issuer_signature(self, issuer_private_key, issuer_id: str):
        """Add issuer signature to token for intermediate verification"""
        if not issuer_private_key or not issuer_id:
            return
        
        # Create content to sign
        sign_content = f"{self.node_id}:{self.token_hash}:{issuer_id}:{self.timestamp}"
        
        try:
            signature = issuer_private_key.sign(
                sign_content.encode(),
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            self.issuer_signature = base64.b64encode(signature).decode('utf-8')
            self.verification_paths.add("issuer-direct")
        except Exception as e:
            # Graceful degradation
            pass
    
    def verify_master_signature(self, master_public_key) -> bool:
        """Verify master signature for direct validation"""
        if not self.master_signature or not master_public_key or not self.master_id:
            return False
        
        try:
            signature = base64.b64decode(self.master_signature.encode('utf-8'))
            sign_content = f"{self.node_id}:{self.token_hash}:{self.master_id}:{self.timestamp}"
            
            master_public_key.verify(
                signature,
                sign_content.encode(),
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            return True
        except Exception:
            return False
    
    def verify_issuer_signature(self, issuer_public_key, issuer_id: str) -> bool:
        """Verify issuer signature for intermediate validation"""
        if not self.issuer_signature or not issuer_public_key:
            return False
        
        try:
            signature = base64.b64decode(self.issuer_signature.encode('utf-8'))
            sign_content = f"{self.node_id}:{self.token_hash}:{issuer_id}:{self.timestamp}"
            
            issuer_public_key.verify(
                signature,
                sign_content.encode(),
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            return True
        except Exception:
            return False

class PKITokenNetwork:
    def __init__(self, storage_dir: str = "token_storage"):
        self.storage_dir = storage_dir
        self.tokens: Dict[str, SecureToken] = {}
        self.master_token: Optional[SecureToken] = None
        
        # Cryptographic key management
        self.master_private_key = None
        self.master_public_key = None
        self.node_keys: Dict[str, Tuple[object, object]] = {}  # node_id -> (private, public)
        
        self._ensure_storage_dir()
        self._load_keys()
        self._load_tokens()
    
    def _ensure_storage_dir(self):
        os.makedirs(self.storage_dir, exist_ok=True)
        os.makedirs(os.path.join(self.storage_dir, "keys"), exist_ok=True)
    
    def _generate_rsa_key_pair(self):
        """Generate RSA key pair for cryptographic operations"""
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048
        )
        public_key = private_key.public_key()
        return private_key, public_key
    
    def _save_key_pair(self, node_id: str, private_key, public_key):
        """Save RSA key pair to disk"""
        try:
            # Save private key
            private_pem = private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            )
            private_file = os.path.join(self.storage_dir, "keys", f"{node_id}_private.pem")
            with open(private_file, 'wb') as f:
                f.write(private_pem)
            
            # Save public key
            public_pem = public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            )
            public_file = os.path.join(self.storage_dir, "keys", f"{node_id}_public.pem")
            with open(public_file, 'wb') as f:
                f.write(public_pem)
        except Exception as e:
            # Graceful degradation - continue without key persistence
            pass
    
    def _load_key_pair(self, node_id: str):
        """Load RSA key pair from disk"""
        try:
            private_file = os.path.join(self.storage_dir, "keys", f"{node_id}_private.pem")
            public_file = os.path.join(self.storage_dir, "keys", f"{node_id}_public.pem")
            
            if os.path.exists(private_file) and os.path.exists(public_file):
                with open(private_file, 'rb') as f:
                    private_key = load_pem_private_key(f.read(), password=None)
                
                with open(public_file, 'rb') as f:
                    public_key = load_pem_public_key(f.read())
                
                return private_key, public_key
        except Exception:
            pass
        return None, None
    
    def _load_keys(self):
        """Load all keys from storage"""
        keys_dir = os.path.join(self.storage_dir, "keys")
        if not os.path.exists(keys_dir):
            return
        
        # Load master keys
        self.master_private_key, self.master_public_key = self._load_key_pair("master")
        
        # Load node keys
        for filename in os.listdir(keys_dir):
            if filename.endswith("_private.pem"):
                node_id = filename[:-12]  # Remove "_private.pem"
                if node_id != "master":
                    private_key, public_key = self._load_key_pair(node_id)
                    if private_key and public_key:
                        self.node_keys[node_id] = (private_key, public_key)
    
    def _ensure_master_keys(self, master_node_id: str):
        """Ensure master keys exist, generate if necessary"""
        if not self.master_private_key or not self.master_public_key:
            self.master_private_key, self.master_public_key = self._generate_rsa_key_pair()
            self._save_key_pair("master", self.master_private_key, self.master_public_key)
    
    def _ensure_node_keys(self, node_id: str):
        """Ensure node keys exist, generate if necessary"""
        if node_id not in self.node_keys:
            private_key, public_key = self._generate_rsa_key_pair()
            self.node_keys[node_id] = (private_key, public_key)
            self._save_key_pair(node_id, private_key, public_key)
    
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
            # Ensure master keys exist
            self._ensure_master_keys(master_node_id)
            
            # Create master token with enhanced capabilities
            master_token = SecureToken(master_node_id, master_id=master_node_id, hierarchy_level=0)
            
            # Master signs its own token for consistency
            master_token.add_master_signature(self.master_private_key, master_node_id)
            
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
            
            # Calculate hierarchy level
            hierarchy_level = issuer_token.hierarchy_level + 1
            
            # Create enhanced token with hierarchical information
            new_token = SecureToken(
                node_id=new_node_id,
                issuer_token_hash=issuer_token.token_hash,
                issuer_id=issuer_node_id,
                token_data=token_data,
                master_id=self.master_token.node_id,
                hierarchy_level=hierarchy_level
            )
            
            # Add master signature cascade for direct verification
            if self.master_private_key:
                new_token.add_master_signature(self.master_private_key, self.master_token.node_id)
            
            # Add issuer signature for intermediate verification
            self._ensure_node_keys(issuer_node_id)
            if issuer_node_id in self.node_keys:
                issuer_private_key, _ = self.node_keys[issuer_node_id]
                new_token.add_issuer_signature(issuer_private_key, issuer_node_id)
            
            # Ensure keys exist for the new node for future issuance
            self._ensure_node_keys(new_node_id)
            
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
    
    def verify_token_direct_master(self, node_id: str) -> Tuple[bool, List[str]]:
        """Verify token using master signature only (no intermediate tokens needed)"""
        if node_id not in self.tokens:
            return False, [f"Token for node {node_id} not found"]
        
        token = self.tokens[node_id]
        
        # Check if master signature verification is available
        if "master-direct" not in token.verification_paths:
            return False, ["Master signature verification not available for this token"]
        
        if not self.master_public_key:
            return False, ["Master public key not available"]
        
        # Verify master signature
        if token.verify_master_signature(self.master_public_key):
            return True, [f"Master signature verified for {node_id}"]
        else:
            return False, ["Master signature verification failed"]
    
    def verify_token_as_issuer(self, issuer_node_id: str, descendant_node_id: str) -> Tuple[bool, List[str]]:
        """Verify that a token was issued by a specific issuer (direct or indirect)"""
        if descendant_node_id not in self.tokens:
            return False, [f"Token for node {descendant_node_id} not found"]
        
        if issuer_node_id not in self.tokens:
            return False, [f"Issuer node {issuer_node_id} not found"]
        
        descendant_token = self.tokens[descendant_node_id]
        
        # Check direct issuance
        if descendant_token.issuer_id == issuer_node_id:
            # Verify issuer signature if available
            if issuer_node_id in self.node_keys and "issuer-direct" in descendant_token.verification_paths:
                _, issuer_public_key = self.node_keys[issuer_node_id]
                if descendant_token.verify_issuer_signature(issuer_public_key, issuer_node_id):
                    return True, [f"Direct issuer signature verified: {issuer_node_id} → {descendant_node_id}"]
                else:
                    return False, ["Direct issuer signature verification failed"]
            else:
                # Fall back to hash chain verification
                return self._verify_direct_issuance(issuer_node_id, descendant_node_id)
        
        # Check indirect issuance (traverse up the chain)
        return self._verify_indirect_issuance(issuer_node_id, descendant_node_id)
    
    def _verify_direct_issuance(self, issuer_node_id: str, descendant_node_id: str) -> Tuple[bool, List[str]]:
        """Verify direct parent-child relationship"""
        descendant_token = self.tokens[descendant_node_id]
        issuer_token = self.tokens[issuer_node_id]
        
        if descendant_token.issuer_token_hash == issuer_token.token_hash:
            return True, [f"Hash chain verified: {issuer_node_id} → {descendant_node_id}"]
        else:
            return False, ["Hash chain verification failed"]
    
    def _verify_indirect_issuance(self, issuer_node_id: str, descendant_node_id: str) -> Tuple[bool, List[str]]:
        """Verify indirect ancestor-descendant relationship"""
        chain = []
        current_token = self.tokens[descendant_node_id]
        
        while current_token and current_token.issuer_id:
            chain.append(f"{current_token.node_id}")
            
            if current_token.issuer_id == issuer_node_id:
                chain.append(f"{issuer_node_id} (issuer found)")
                return True, chain
            
            if current_token.issuer_id not in self.tokens:
                chain.append(f"Missing issuer: {current_token.issuer_id}")
                return False, chain
            
            current_token = self.tokens[current_token.issuer_id]
        
        return False, chain + [f"Issuer {issuer_node_id} not found in chain"]
    
    def verify_token_hybrid(self, node_id: str) -> Tuple[bool, Dict[str, Tuple[bool, List[str]]]]:
        """Verify token using all available methods for maximum confidence"""
        results = {}
        
        # Try chain verification
        results["chain"] = self.verify_token(node_id)
        
        # Try master direct verification
        if node_id in self.tokens and "master-direct" in self.tokens[node_id].verification_paths:
            results["master-direct"] = self.verify_token_direct_master(node_id)
        
        # Try issuer verification (if not master)
        if node_id in self.tokens:
            token = self.tokens[node_id]
            if token.issuer_id and token.issuer_id in self.tokens:
                results["issuer-direct"] = self.verify_token_as_issuer(token.issuer_id, node_id)
        
        # Determine overall result
        any_valid = any(result[0] for result in results.values())
        
        return any_valid, results
    
    def get_token_info(self, node_id: str) -> Optional[Dict]:
        if node_id in self.tokens:
            return self.tokens[node_id].to_dict()
        return None
    
    def list_all_tokens(self) -> List[Dict]:
        return [token.to_dict() for token in self.tokens.values()]