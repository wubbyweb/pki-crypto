#!/usr/bin/env python3

import argparse
import sys
import json
from .core import PKITokenNetwork

def create_master(args):
    network = PKITokenNetwork(args.storage_dir)
    try:
        master_token = network.create_master_token(args.node_id)
        print(f"Master token created for node: {args.node_id}")
        print(f"Token hash: {master_token.token_hash}")
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)

def issue_token(args):
    network = PKITokenNetwork(args.storage_dir)
    try:
        new_token = network.issue_token(args.issuer, args.node_id, args.data)
        print(f"Token issued to node: {args.node_id}")
        print(f"Issued by: {args.issuer}")
        print(f"Token hash: {new_token.token_hash}")
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)

def verify_token(args):
    network = PKITokenNetwork(args.storage_dir)
    
    # Determine verification mode
    mode = getattr(args, 'mode', 'chain')
    
    print(f"Token verification for node: {args.node_id}")
    print(f"Verification mode: {mode}")
    
    if mode == 'chain':
        is_valid, chain = network.verify_token(args.node_id)
        print(f"Status: {'VALID' if is_valid else 'INVALID'}")
        print("\nVerification chain:")
        for i, step in enumerate(chain):
            print(f"  {i+1}. {step}")
    
    elif mode == 'master':
        is_valid, result = network.verify_token_direct_master(args.node_id)
        print(f"Status: {'VALID' if is_valid else 'INVALID'}")
        print("\nMaster direct verification:")
        for i, step in enumerate(result):
            print(f"  {i+1}. {step}")
    
    elif mode == 'hybrid':
        is_valid, results = network.verify_token_hybrid(args.node_id)
        print(f"Overall Status: {'VALID' if is_valid else 'INVALID'}")
        print("\nVerification Results by Method:")
        for method, (valid, details) in results.items():
            status = 'VALID' if valid else 'INVALID'
            print(f"  {method}: {status}")
            for detail in details:
                print(f"    - {detail}")
    
    else:
        print(f"Unknown verification mode: {mode}")
        return

def verify_as_issuer(args):
    network = PKITokenNetwork(args.storage_dir)
    is_valid, chain = network.verify_token_as_issuer(args.issuer_id, args.descendant_id)
    
    print(f"Issuer verification: {args.issuer_id} → {args.descendant_id}")
    print(f"Status: {'VALID' if is_valid else 'INVALID'}")
    print("\nVerification path:")
    for i, step in enumerate(chain):
        print(f"  {i+1}. {step}")

def show_token(args):
    network = PKITokenNetwork(args.storage_dir)
    token_info = network.get_token_info(args.node_id)
    
    if token_info:
        print(f"Token information for node: {args.node_id}")
        print(json.dumps(token_info, indent=2))
    else:
        print(f"No token found for node: {args.node_id}")
        sys.exit(1)

def list_tokens(args):
    network = PKITokenNetwork(args.storage_dir)
    tokens = network.list_all_tokens()
    
    if not tokens:
        print("No tokens found in the network")
        return
    
    print(f"Found {len(tokens)} tokens in the network:")
    print("-" * 80)
    
    for token in tokens:
        token_type = "MASTER" if token['issuer_token_hash'] is None else "NODE"
        print(f"Node ID: {token['node_id']}")
        print(f"Type: {token_type}")
        print(f"Token Hash: {token['token_hash']}")
        if token['issuer_id']:
            print(f"Issued by: {token['issuer_id']}")
        print(f"Created: {token['timestamp']}")
        print("-" * 80)

def main():
    parser = argparse.ArgumentParser(description="PKI Token Network CLI")
    parser.add_argument("--storage-dir", default="token_storage", 
                       help="Directory to store token files (default: token_storage)")
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Create master token
    master_parser = subparsers.add_parser('create-master', help='Create a master token')
    master_parser.add_argument('node_id', help='Master node identifier')
    master_parser.set_defaults(func=create_master)
    
    # Issue token
    issue_parser = subparsers.add_parser('issue', help='Issue a new token')
    issue_parser.add_argument('issuer', help='Node ID of the token issuer')
    issue_parser.add_argument('node_id', help='Node ID for the new token')
    issue_parser.add_argument('--data', help='Optional token data')
    issue_parser.set_defaults(func=issue_token)
    
    # Verify token
    verify_parser = subparsers.add_parser('verify', help='Verify a token')
    verify_parser.add_argument('node_id', help='Node ID to verify')
    verify_parser.add_argument('--mode', choices=['chain', 'master', 'hybrid'], 
                              default='chain', help='Verification mode (default: chain)')
    verify_parser.set_defaults(func=verify_token)
    
    # Verify as issuer
    verify_issuer_parser = subparsers.add_parser('verify-as-issuer', 
                                                help='Verify token as issued by specific node')
    verify_issuer_parser.add_argument('issuer_id', help='Issuer node ID')
    verify_issuer_parser.add_argument('descendant_id', help='Descendant node ID to verify')
    verify_issuer_parser.set_defaults(func=verify_as_issuer)
    
    # Show token info
    show_parser = subparsers.add_parser('show', help='Show token information')
    show_parser.add_argument('node_id', help='Node ID to show')
    show_parser.set_defaults(func=show_token)
    
    # List all tokens
    list_parser = subparsers.add_parser('list', help='List all tokens')
    list_parser.set_defaults(func=list_tokens)
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    args.func(args)

if __name__ == "__main__":
    main()