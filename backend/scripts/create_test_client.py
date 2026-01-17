"""
Create a test API client for local development.
Run this script to generate an API key for testing.
"""

import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.database import SessionLocal, engine, Base
from app.models.api_client import ApiClient
from app.models.verification_log import VerificationLog  # Import to register relationship
from app.core.security import generate_api_key
from uuid import uuid4
from datetime import datetime

# Create tables if they don't exist
Base.metadata.create_all(bind=engine)

def create_test_client():
    """Create a test API client with generated API key."""
    db = SessionLocal()
    
    try:
        # Check if test client already exists
        existing = db.query(ApiClient).filter(ApiClient.name == "Test Client").first()
        
        if existing:
            print("❌ Test client already exists!")
            print(f"Client ID: {existing.id}")
            print(f"Name: {existing.name}")
            print("\nTo regenerate, delete the existing client first.")
            return
        
        # Generate API key
        raw_key, hashed_key = generate_api_key()
        
        # Create client
        client = ApiClient(
            id=uuid4(),
            name="Test Client",
            api_key_hash=hashed_key,
            is_active=True,
            rate_limit_per_minute=1000,  # 1000 requests per minute
            billing_tier="premium",
            contact_email="test@example.com"
        )
        
        db.add(client)
        db.commit()
        db.refresh(client)
        
        print("✅ Test API client created successfully!")
        print("")
        print("=" * 60)
        print("API CLIENT DETAILS")
        print("=" * 60)
        print(f"Client ID:    {client.id}")
        print(f"Name:         {client.name}")
        print(f"Tier:         {client.billing_tier}")
        print(f"Rate Limit:   {client.rate_limit_per_minute}/min")
        print("")
        print("🔑 API KEY (save this - it won't be shown again):")
        print(f"   {raw_key}")
        print("")
        print("=" * 60)
        print("")
        print("Use this API key in the Authorization header:")
        print(f'  Authorization: Bearer {raw_key}')
        print("")
        print("Test the API:")
        print(f'  curl http://localhost:8000/api/v1/verify/individual \\')
        print(f'    -H "Authorization: Bearer {raw_key}" \\')
        print(f'    -H "Content-Type: application/json" \\')
        print(f'    -d \'{{"bvn":"22123456789","nin":"12345678901"}}\'')
        print("")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error creating client: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    create_test_client()
