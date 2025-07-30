#!/usr/bin/env python3

import os
import shutil
from pki_token import PKITokenNetwork

def demo_hierarchical_verification():
    """Demonstrate hierarchical verification capabilities"""
    
    print("=" * 80)
    print("PKI HIERARCHICAL VERIFICATION DEMONSTRATION")
    print("=" * 80)
    
    # Clean setup
    demo_dir = "demo_hierarchical"
    if os.path.exists(demo_dir):
        shutil.rmtree(demo_dir)
    
    # Create network
    network = PKITokenNetwork(demo_dir)
    
    print("\n1. CREATING HIERARCHICAL TOKEN STRUCTURE")
    print("-" * 50)
    
    # Create master
    master = network.create_master_token("corporate-root")
    print(f"✓ Created master token: {master.node_id}")
    
    # Level 1: Regional offices
    us_office = network.issue_token("corporate-root", "us-office", "US Regional Office")
    eu_office = network.issue_token("corporate-root", "eu-office", "EU Regional Office")
    print(f"✓ Created regional offices: {us_office.node_id}, {eu_office.node_id}")
    
    # Level 2: Department heads
    us_eng = network.issue_token("us-office", "us-engineering", "US Engineering Dept")
    us_sales = network.issue_token("us-office", "us-sales", "US Sales Dept")
    eu_eng = network.issue_token("eu-office", "eu-engineering", "EU Engineering Dept")
    print(f"✓ Created department heads: us-engineering, us-sales, eu-engineering")
    
    # Level 3: Team leads
    us_backend = network.issue_token("us-engineering", "us-backend-team", "US Backend Team")
    us_frontend = network.issue_token("us-engineering", "us-frontend-team", "US Frontend Team")
    print(f"✓ Created team leads: us-backend-team, us-frontend-team")
    
    # Level 4: Individual employees
    developer1 = network.issue_token("us-backend-team", "john-doe", "Senior Developer")
    developer2 = network.issue_token("us-frontend-team", "jane-smith", "Lead Frontend Dev")
    print(f"✓ Created employees: john-doe, jane-smith")
    
    print(f"\nHierarchy created with {len(network.tokens)} tokens across 5 levels")
    
    print("\n2. TRADITIONAL CHAIN VERIFICATION")
    print("-" * 50)
    
    # Traditional verification
    is_valid, chain = network.verify_token("john-doe")
    print(f"Verifying john-doe (Level 4 employee)")
    print(f"Status: {'VALID' if is_valid else 'INVALID'}")
    print("Chain traversal:")
    for i, step in enumerate(chain):
        print(f"  {i+1}. {step}")
    
    print("\n3. MASTER DIRECT VERIFICATION (Key Innovation)")
    print("-" * 50)
    
    # Master direct verification
    is_valid, result = network.verify_token_direct_master("john-doe")
    print(f"Master verifying john-doe directly (no intermediates needed)")
    print(f"Status: {'VALID' if is_valid else 'INVALID'}")
    print("Verification method:")
    for step in result:
        print(f"  - {step}")
    
    print("\n4. INTERMEDIATE ISSUER VERIFICATION")
    print("-" * 50)
    
    # Issuer verification
    is_valid, result = network.verify_token_as_issuer("us-office", "john-doe")
    print(f"US Office verifying john-doe (indirect descendant)")
    print(f"Status: {'VALID' if is_valid else 'INVALID'}")
    print("Verification path:")
    for step in result:
        print(f"  - {step}")
    
    # Direct issuer verification
    is_valid, result = network.verify_token_as_issuer("us-backend-team", "john-doe")
    print(f"\nDirect issuer (us-backend-team) verifying john-doe")
    print(f"Status: {'VALID' if is_valid else 'INVALID'}")
    print("Verification method:")
    for step in result:
        print(f"  - {step}")
    
    print("\n5. HYBRID VERIFICATION (All Methods)")
    print("-" * 50)
    
    # Hybrid verification
    is_valid, results = network.verify_token_hybrid("jane-smith")
    print(f"Hybrid verification for jane-smith")
    print(f"Overall Status: {'VALID' if is_valid else 'INVALID'}")
    print("Results by verification method:")
    for method, (valid, details) in results.items():
        status = 'VALID' if valid else 'INVALID'
        print(f"  {method}: {status}")
        for detail in details[:2]:  # Limit output
            print(f"    - {detail}")
    
    print("\n6. DISTRIBUTED VERIFICATION SIMULATION")
    print("-" * 50)
    
    # Simulate master node without intermediate access
    master_only_dir = "demo_master_only"
    if os.path.exists(master_only_dir):
        shutil.rmtree(master_only_dir)
    
    os.makedirs(master_only_dir)
    os.makedirs(os.path.join(master_only_dir, "keys"))
    
    # Copy only master keys and end employee token
    import subprocess
    subprocess.run(["cp", "-r", f"{demo_dir}/keys/", master_only_dir], check=True)
    subprocess.run(["cp", f"{demo_dir}/corporate-root_token.json", master_only_dir], check=True)
    subprocess.run(["cp", f"{demo_dir}/john-doe_token.json", master_only_dir], check=True)
    
    # Create isolated master environment
    master_network = PKITokenNetwork(master_only_dir)
    
    print("Master node in isolated environment (no intermediate tokens)")
    print("Available tokens:", list(master_network.tokens.keys()))
    
    # Master direct verification should work
    is_valid, result = master_network.verify_token_direct_master("john-doe")
    print(f"Master direct verification: {'VALID' if is_valid else 'INVALID'}")
    
    # Chain verification should fail
    is_valid, result = master_network.verify_token("john-doe")
    print(f"Chain verification: {'INVALID (Expected)' if not is_valid else 'UNEXPECTED VALID'}")
    print(f"Failure reason: {result[-1] if result else 'Unknown'}")
    
    print("\n7. TOKEN CAPABILITIES SUMMARY")
    print("-" * 50)
    
    # Show token capabilities
    sample_token = network.tokens["john-doe"]
    print(f"Token: {sample_token.node_id}")
    print(f"Hierarchy Level: {sample_token.hierarchy_level}")
    print(f"Master ID: {sample_token.master_id}")
    print(f"Available Verification Methods: {list(sample_token.verification_paths)}")
    print(f"Has Master Signature: {'Yes' if sample_token.master_signature else 'No'}")
    print(f"Has Issuer Signature: {'Yes' if sample_token.issuer_signature else 'No'}")
    
    print("\n8. PERFORMANCE COMPARISON")
    print("-" * 50)
    
    import time
    
    # Time chain verification
    start = time.time()
    for _ in range(100):
        network.verify_token("john-doe")
    chain_time = time.time() - start
    
    # Time master direct verification
    start = time.time()
    for _ in range(100):
        network.verify_token_direct_master("john-doe")
    master_time = time.time() - start
    
    print(f"Chain verification (100 runs): {chain_time:.4f}s")
    print(f"Master direct (100 runs): {master_time:.4f}s")
    print(f"Master direct is {chain_time/master_time:.1f}x faster")
    
    print("\n" + "=" * 80)
    print("DEMONSTRATION COMPLETE")
    print("=" * 80)
    print("\nKey Achievements:")
    print("✅ Master can verify any token without intermediate access")
    print("✅ Intermediate issuers can verify their subtree tokens")
    print("✅ Multiple verification methods provide redundancy")
    print("✅ Backward compatibility with existing chain verification")
    print("✅ Cryptographic signatures ensure authenticity")
    print("✅ Hierarchical structure scales to deep token chains")
    
    # Cleanup
    shutil.rmtree(demo_dir)
    shutil.rmtree(master_only_dir)

if __name__ == "__main__":
    demo_hierarchical_verification()