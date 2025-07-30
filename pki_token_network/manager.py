#!/usr/bin/env python3

import os
import sys
import json
from typing import Dict, List, Optional
from .core import PKITokenNetwork
from .packager import create_secure_token_package

class PKIWizard:
    def __init__(self):
        self.network = None
        self.storage_dir = "token_storage"
        self.clear_screen()
        
    def clear_screen(self):
        """Clear terminal screen"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def print_header(self):
        """Print wizard header"""
        print("=" * 80)
        print("🔐 PKI TOKEN NETWORK WIZARD")
        print("=" * 80)
        print("Interactive wizard for PKI token operations")
        print()
    
    def print_menu(self, title: str, options: List[str]) -> int:
        """Print menu and get user selection"""
        print(f"\n📋 {title}")
        print("-" * 50)
        
        for i, option in enumerate(options, 1):
            print(f"  {i}. {option}")
        
        print(f"  0. Back/Exit")
        print()
        
        while True:
            try:
                choice = input("👉 Select option (0-{}): ".format(len(options)))
                choice_int = int(choice)
                if 0 <= choice_int <= len(options):
                    return choice_int
                else:
                    print(f"❌ Please enter a number between 0 and {len(options)}")
            except ValueError:
                print("❌ Please enter a valid number")
    
    def get_input(self, prompt: str, required: bool = True, default: str = None) -> str:
        """Get user input with validation"""
        while True:
            if default:
                user_input = input(f"👉 {prompt} [{default}]: ").strip()
                if not user_input:
                    return default
            else:
                user_input = input(f"👉 {prompt}: ").strip()
            
            if user_input or not required:
                return user_input
            print("❌ This field is required")
    
    def confirm_action(self, message: str) -> bool:
        """Get confirmation from user"""
        while True:
            response = input(f"❓ {message} (y/n): ").strip().lower()
            if response in ['y', 'yes']:
                return True
            elif response in ['n', 'no']:
                return False
            print("❌ Please enter 'y' or 'n'")
    
    def setup_network(self):
        """Setup or load PKI network"""
        print("\n🔧 PKI Network Setup")
        print("-" * 30)
        
        # Check if network exists
        if os.path.exists(self.storage_dir):
            print(f"📁 Found existing network in: {self.storage_dir}")
            use_existing = self.confirm_action("Use existing network?")
            if not use_existing:
                custom_dir = self.get_input("Enter custom storage directory", required=False)
                if custom_dir:
                    self.storage_dir = custom_dir
        
        try:
            self.network = PKITokenNetwork(self.storage_dir)
            print(f"✅ Network loaded successfully")
            
            if self.network.master_token:
                print(f"🏛️  Master token: {self.network.master_token.node_id}")
                print(f"📊 Total tokens: {len(self.network.tokens)}")
            else:
                print("⚠️  No master token found - you'll need to create one")
            
            input("\n📱 Press Enter to continue...")
            
        except Exception as e:
            print(f"❌ Error loading network: {e}")
            input("📱 Press Enter to continue...")
            return False
        
        return True
    
    def create_master_wizard(self):
        """Wizard for creating master token"""
        self.clear_screen()
        self.print_header()
        
        print("🏛️  CREATE MASTER TOKEN")
        print("-" * 30)
        
        if self.network.master_token:
            print(f"⚠️  Master token already exists: {self.network.master_token.node_id}")
            input("📱 Press Enter to continue...")
            return
        
        print("The master token serves as the root certificate authority.")
        print("Choose a descriptive name for your organization's root authority.")
        print()
        
        # Get master node ID
        master_id = self.get_input("Master node ID (e.g., 'corporate-root', 'pki-authority')")
        
        # Validate node ID
        if not master_id.replace('-', '').replace('_', '').replace('.', '').isalnum():
            print("❌ Node ID can only contain letters, numbers, hyphens, underscores, and dots")
            input("📱 Press Enter to continue...")
            return
        
        print(f"\n📋 Creating master token:")
        print(f"   Node ID: {master_id}")
        print(f"   Storage: {self.storage_dir}")
        
        if not self.confirm_action("Create master token?"):
            return
        
        try:
            master_token = self.network.create_master_token(master_id)
            print(f"\n✅ Master token created successfully!")
            print(f"   Node ID: {master_token.node_id}")
            print(f"   Token Hash: {master_token.token_hash[:32]}...")
            print(f"   Hierarchy Level: {master_token.hierarchy_level}")
            print(f"   Verification Paths: {list(master_token.verification_paths)}")
            
        except Exception as e:
            print(f"❌ Error creating master token: {e}")
        
        input("\n📱 Press Enter to continue...")
    
    def issue_token_wizard(self):
        """Wizard for issuing tokens"""
        self.clear_screen()
        self.print_header()
        
        print("📄 ISSUE NEW TOKEN")
        print("-" * 30)
        
        if not self.network.master_token:
            print("❌ No master token exists. Create a master token first.")
            input("📱 Press Enter to continue...")
            return
        
        # Show available issuers
        print("Available token issuers:")
        issuers = list(self.network.tokens.keys())
        for i, issuer in enumerate(issuers, 1):
            token = self.network.tokens[issuer]
            print(f"  {i}. {issuer} (Level {token.hierarchy_level})")
        
        print()
        
        # Get issuer
        issuer_choice = self.get_input("Select issuer by number or enter node ID")
        
        try:
            issuer_num = int(issuer_choice)
            if 1 <= issuer_num <= len(issuers):
                issuer_id = issuers[issuer_num - 1]
            else:
                print("❌ Invalid issuer number")
                input("📱 Press Enter to continue...")
                return
        except ValueError:
            issuer_id = issuer_choice
            if issuer_id not in self.network.tokens:
                print(f"❌ Issuer '{issuer_id}' not found")
                input("📱 Press Enter to continue...")
                return
        
        # Get new node details
        new_node_id = self.get_input("New node ID")
        
        # Validate node ID
        if not new_node_id.replace('-', '').replace('_', '').replace('.', '').isalnum():
            print("❌ Node ID can only contain letters, numbers, hyphens, underscores, and dots")
            input("📱 Press Enter to continue...")
            return
        
        if new_node_id in self.network.tokens:
            print(f"❌ Node '{new_node_id}' already exists")
            input("📱 Press Enter to continue...")
            return
        
        token_data = self.get_input("Token description/data", required=False, 
                                   default=f"Token for {new_node_id}")
        
        # Summary
        issuer_token = self.network.tokens[issuer_id]
        print(f"\n📋 Token issuance summary:")
        print(f"   Issuer: {issuer_id} (Level {issuer_token.hierarchy_level})")
        print(f"   New Node: {new_node_id}")
        print(f"   New Level: {issuer_token.hierarchy_level + 1}")
        print(f"   Data: {token_data}")
        
        if not self.confirm_action("Issue token?"):
            return
        
        try:
            new_token = self.network.issue_token(issuer_id, new_node_id, token_data)
            print(f"\n✅ Token issued successfully!")
            print(f"   Node ID: {new_token.node_id}")
            print(f"   Issued by: {new_token.issuer_id}")
            print(f"   Token Hash: {new_token.token_hash[:32]}...")
            print(f"   Hierarchy Level: {new_token.hierarchy_level}")
            print(f"   Master ID: {new_token.master_id}")
            print(f"   Verification Paths: {list(new_token.verification_paths)}")
            
        except Exception as e:
            print(f"❌ Error issuing token: {e}")
        
        input("\n📱 Press Enter to continue...")
    
    def verify_token_wizard(self):
        """Wizard for token verification"""
        self.clear_screen()
        self.print_header()
        
        print("🔍 VERIFY TOKEN")
        print("-" * 30)
        
        if not self.network.tokens:
            print("❌ No tokens found in network")
            input("📱 Press Enter to continue...")
            return
        
        # Show available tokens
        print("Available tokens:")
        tokens = list(self.network.tokens.keys())
        for i, token_id in enumerate(tokens, 1):
            token = self.network.tokens[token_id]
            token_type = "MASTER" if token.hierarchy_level == 0 else f"Level {token.hierarchy_level}"
            print(f"  {i}. {token_id} ({token_type})")
        
        print()
        
        # Get token to verify
        token_choice = self.get_input("Select token by number or enter node ID")
        
        try:
            token_num = int(token_choice)
            if 1 <= token_num <= len(tokens):
                token_id = tokens[token_num - 1]
            else:
                print("❌ Invalid token number")
                input("📱 Press Enter to continue...")
                return
        except ValueError:
            token_id = token_choice
            if token_id not in self.network.tokens:
                print(f"❌ Token '{token_id}' not found")
                input("📱 Press Enter to continue...")
                return
        
        # Verification mode selection
        verification_modes = [
            "Chain Verification (Traditional)",
            "Master Direct Verification", 
            "Hybrid Verification (All Methods)"
        ]
        
        if self.network.tokens[token_id].issuer_id:
            verification_modes.append("Issuer Verification")
        
        mode_choice = self.print_menu("Select Verification Method", verification_modes)
        
        if mode_choice == 0:
            return
        
        print(f"\n🔍 Verifying token: {token_id}")
        print("-" * 40)
        
        try:
            if mode_choice == 1:  # Chain verification
                is_valid, chain = self.network.verify_token(token_id)
                print(f"Status: {'✅ VALID' if is_valid else '❌ INVALID'}")
                print("\nVerification chain:")
                for i, step in enumerate(chain, 1):
                    print(f"  {i}. {step}")
            
            elif mode_choice == 2:  # Master direct
                is_valid, result = self.network.verify_token_direct_master(token_id)
                print(f"Status: {'✅ VALID' if is_valid else '❌ INVALID'}")
                print("\nMaster direct verification:")
                for step in result:
                    print(f"  - {step}")
            
            elif mode_choice == 3:  # Hybrid
                is_valid, results = self.network.verify_token_hybrid(token_id)
                print(f"Overall Status: {'✅ VALID' if is_valid else '❌ INVALID'}")
                print("\nVerification Results by Method:")
                for method, (valid, details) in results.items():
                    status = '✅ VALID' if valid else '❌ INVALID'
                    print(f"  {method}: {status}")
                    for detail in details[:2]:  # Limit output
                        print(f"    - {detail}")
            
            elif mode_choice == 4:  # Issuer verification
                token = self.network.tokens[token_id]
                if token.issuer_id:
                    is_valid, result = self.network.verify_token_as_issuer(token.issuer_id, token_id)
                    print(f"Status: {'✅ VALID' if is_valid else '❌ INVALID'}")
                    print(f"\nIssuer verification: {token.issuer_id} → {token_id}")
                    for step in result:
                        print(f"  - {step}")
                
        except Exception as e:
            print(f"❌ Verification error: {e}")
        
        input("\n📱 Press Enter to continue...")
    
    def create_secure_package_wizard(self):
        """Wizard for creating secure distribution packages"""
        self.clear_screen()
        self.print_header()
        
        print("📦 CREATE SECURE DISTRIBUTION PACKAGE")
        print("-" * 45)
        
        if not self.network.tokens:
            print("❌ No tokens found in network")
            input("📱 Press Enter to continue...")
            return
        
        # Show available tokens
        print("Available tokens for packaging:")
        tokens = list(self.network.tokens.keys())
        for i, token_id in enumerate(tokens, 1):
            token = self.network.tokens[token_id]
            token_type = "MASTER" if token.hierarchy_level == 0 else f"Level {token.hierarchy_level}"
            print(f"  {i}. {token_id} ({token_type})")
        
        print()
        
        # Get token to package
        token_choice = self.get_input("Select token by number or enter node ID")
        
        try:
            token_num = int(token_choice)
            if 1 <= token_num <= len(tokens):
                token_id = tokens[token_num - 1]
            else:
                print("❌ Invalid token number")
                input("📱 Press Enter to continue...")
                return
        except ValueError:
            token_id = token_choice
            if token_id not in self.network.tokens:
                print(f"❌ Token '{token_id}' not found")
                input("📱 Press Enter to continue...")
                return
        
        # Get output directory
        default_dir = f"{token_id}_secure_package"
        output_dir = self.get_input("Output directory", required=False, default=default_dir)
        
        print(f"\n📋 Package creation summary:")
        print(f"   Token: {token_id}")
        print(f"   Output Directory: {output_dir}")
        print(f"   Contents: Certificate + Public Keys + Instructions")
        print(f"   🔒 Security: Private keys are NOT included")
        
        if not self.confirm_action("Create secure package?"):
            return
        
        try:
            create_secure_token_package(self.network, token_id, output_dir)
            
            print(f"\n✅ Secure package created successfully!")
            print(f"   Location: {output_dir}/")
            print(f"   Contents:")
            
            for file in os.listdir(output_dir):
                print(f"     📄 {file}")
            
            print(f"\n🔒 Security Notes:")
            print(f"   ✅ Certificate contains all verification data")
            print(f"   ✅ Public keys included for signature verification")
            print(f"   ✅ Instructions provided for recipient")
            print(f"   ❌ Private keys are NOT included (security best practice)")
            
            # Archive option
            if self.confirm_action("Create compressed archive for distribution?"):
                import tarfile
                archive_name = f"{output_dir}.tar.gz"
                with tarfile.open(archive_name, "w:gz") as tar:
                    tar.add(output_dir, arcname=os.path.basename(output_dir))
                print(f"   📦 Archive created: {archive_name}")
            
        except Exception as e:
            print(f"❌ Error creating package: {e}")
        
        input("\n📱 Press Enter to continue...")
    
    def view_network_wizard(self):
        """Wizard for viewing network information"""
        self.clear_screen()
        self.print_header()
        
        print("📊 NETWORK OVERVIEW")
        print("-" * 30)
        
        if not self.network.tokens:
            print("❌ No tokens found in network")
            input("📱 Press Enter to continue...")
            return
        
        # Network statistics
        total_tokens = len(self.network.tokens)
        max_level = max(token.hierarchy_level for token in self.network.tokens.values())
        master_token = self.network.master_token
        
        print(f"🏛️  Master Token: {master_token.node_id if master_token else 'None'}")
        print(f"📊 Total Tokens: {total_tokens}")
        print(f"📈 Maximum Hierarchy Level: {max_level}")
        print(f"🗂️  Storage Directory: {self.storage_dir}")
        
        # Group tokens by level
        tokens_by_level = {}
        for token in self.network.tokens.values():
            level = token.hierarchy_level
            if level not in tokens_by_level:
                tokens_by_level[level] = []
            tokens_by_level[level].append(token)
        
        print(f"\n🌳 Hierarchy Structure:")
        for level in sorted(tokens_by_level.keys()):
            level_name = "Master" if level == 0 else f"Level {level}"
            tokens = tokens_by_level[level]
            print(f"   {level_name}: {len(tokens)} token(s)")
            for token in tokens:
                issuer_info = f" (issued by {token.issuer_id})" if token.issuer_id else ""
                print(f"     • {token.node_id}{issuer_info}")
        
        print(f"\n🔑 Cryptographic Keys:")
        print(f"   Master Keys: {'✅ Present' if self.network.master_private_key else '❌ Missing'}")
        print(f"   Node Keys: {len(self.network.node_keys)} key pair(s)")
        
        # Verification capabilities
        print(f"\n🔍 Verification Capabilities:")
        for token_id, token in self.network.tokens.items():
            paths = list(token.verification_paths)
            print(f"   {token_id}: {', '.join(paths)}")
        
        input("\n📱 Press Enter to continue...")
    
    def token_details_wizard(self):
        """Wizard for viewing detailed token information"""
        self.clear_screen()
        self.print_header()
        
        print("🔍 TOKEN DETAILS")
        print("-" * 30)
        
        if not self.network.tokens:
            print("❌ No tokens found in network")
            input("📱 Press Enter to continue...")
            return
        
        # Show available tokens
        print("Available tokens:")
        tokens = list(self.network.tokens.keys())
        for i, token_id in enumerate(tokens, 1):
            token = self.network.tokens[token_id]
            token_type = "MASTER" if token.hierarchy_level == 0 else f"Level {token.hierarchy_level}"
            print(f"  {i}. {token_id} ({token_type})")
        
        print()
        
        # Get token to view
        token_choice = self.get_input("Select token by number or enter node ID")
        
        try:
            token_num = int(token_choice)
            if 1 <= token_num <= len(tokens):
                token_id = tokens[token_num - 1]
            else:
                print("❌ Invalid token number")
                input("📱 Press Enter to continue...")
                return
        except ValueError:
            token_id = token_choice
            if token_id not in self.network.tokens:
                print(f"❌ Token '{token_id}' not found")
                input("📱 Press Enter to continue...")
                return
        
        # Display token details
        token = self.network.tokens[token_id]
        
        print(f"\n📄 Token Details: {token_id}")
        print("-" * 50)
        print(f"Node ID: {token.node_id}")
        print(f"Token Hash: {token.token_hash}")
        print(f"Master ID: {token.master_id}")
        print(f"Issuer ID: {token.issuer_id or 'None (Master)'}")
        print(f"Hierarchy Level: {token.hierarchy_level}")
        print(f"Token Data: {token.token_data}")
        print(f"Timestamp: {token.timestamp}")
        print(f"Token ID: {token.token_id}")
        
        print(f"\n🔍 Verification Information:")
        print(f"Available Methods: {', '.join(token.verification_paths)}")
        print(f"Has Master Signature: {'✅ Yes' if token.master_signature else '❌ No'}")
        print(f"Has Issuer Signature: {'✅ Yes' if token.issuer_signature else '❌ No'}")
        
        if token.issuer_token_hash:
            print(f"Issuer Token Hash: {token.issuer_token_hash}")
        
        # Test verification
        print(f"\n🧪 Quick Verification Test:")
        try:
            is_valid, _ = self.network.verify_token_hybrid(token_id)
            print(f"Verification Status: {'✅ VALID' if is_valid else '❌ INVALID'}")
        except Exception as e:
            print(f"Verification Error: {e}")
        
        input("\n📱 Press Enter to continue...")
    
    def main_menu(self):
        """Main wizard menu"""
        while True:
            self.clear_screen()
            self.print_header()
            
            # Network status
            if self.network:
                master_info = f"Master: {self.network.master_token.node_id}" if self.network.master_token else "No Master"
                token_count = len(self.network.tokens)
                print(f"📊 Network Status: {master_info} | Tokens: {token_count} | Storage: {self.storage_dir}")
                print()
            
            main_options = [
                "🏛️  Create Master Token",
                "📄 Issue New Token", 
                "🔍 Verify Token",
                "📦 Create Secure Distribution Package",
                "📊 View Network Overview",
                "🔍 View Token Details",
                "🔧 Change Storage Directory"
            ]
            
            choice = self.print_menu("PKI Token Network Operations", main_options)
            
            if choice == 0:
                print("\n👋 Goodbye!")
                sys.exit(0)
            elif choice == 1:
                self.create_master_wizard()
            elif choice == 2:
                self.issue_token_wizard()
            elif choice == 3:
                self.verify_token_wizard()
            elif choice == 4:
                self.create_secure_package_wizard()
            elif choice == 5:
                self.view_network_wizard()
            elif choice == 6:
                self.token_details_wizard()
            elif choice == 7:
                new_dir = self.get_input("Enter new storage directory", required=False, 
                                        default=self.storage_dir)
                if new_dir != self.storage_dir:
                    self.storage_dir = new_dir
                    if self.setup_network():
                        print("✅ Storage directory changed successfully")
                    else:
                        print("❌ Failed to load network from new directory")
                    input("📱 Press Enter to continue...")
    
    def run(self):
        """Run the wizard"""
        self.clear_screen()
        self.print_header()
        
        print("Welcome to the PKI Token Network Wizard!")
        print("This interactive tool will guide you through PKI operations.")
        print()
        
        if not self.setup_network():
            print("❌ Failed to setup network. Exiting.")
            sys.exit(1)
        
        self.main_menu()

def main():
    """Main entry point"""
    try:
        wizard = PKIWizard()
        wizard.run()
    except KeyboardInterrupt:
        print("\n\n👋 Wizard interrupted. Goodbye!")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        print("Please check your system and try again.")
        sys.exit(1)

if __name__ == "__main__":
    main()