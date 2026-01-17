"""
Pre-deployment validation script.
Tests all imports and database initialization.
"""

import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

print("=" * 70)
print("E-KYC Pre-Deployment Validation")
print("=" * 70)
print()

# Test 1: Import core modules
print("✓ Testing core module imports...")
try:
    from app.core.config import settings, get_settings
    from app.core.database import engine, Base, get_db, SessionLocal
    from app.core.types import UUID, JSONB
    from app.core.security import generate_api_key
    from app.core.logging import setup_logging, get_logger
    from app.core.exceptions import EKYCBaseException, ProviderError
    print("  ✅ Core modules imported successfully")
except Exception as e:
    print(f"  ❌ FAILED: {e}")
    sys.exit(1)

# Test 2: Import all models
print("✓ Testing model imports...")
try:
    from app.models.api_client import ApiClient
    from app.models.customer import Customer
    from app.models.verification_result import VerificationResult
    from app.models.document import Document
    from app.models.beneficial_owner import BeneficialOwner
    from app.models.audit_log import AuditLog
    from app.models.verification_log import VerificationLog
    from app.models.workflow import WorkflowApproval
    print("  ✅ All 8 models imported successfully")
except Exception as e:
    print(f"  ❌ FAILED: {e}")
    sys.exit(1)

# Test 3: Import services
print("✓ Testing service imports...")
try:
    from app.services.providers.factory import get_verification_provider
    from app.services.cross_validator import CrossValidator
    from app.services.ubo_analyzer import UBOAnalyzer
    from app.services.risk_engine import RiskEngine
    from app.services.verification_orchestrator import VerificationOrchestrator
    from app.services.report_generator import ReportGenerator
    print("  ✅ All services imported successfully")
except Exception as e:
    print(f"  ❌ FAILED: {e}")
    sys.exit(1)

# Test 4: Import API endpoints
print("✓ Testing API endpoint imports...")
try:
    from app.api.external.v1 import verification, reports
    from app.api.schemas import (
        IndividualVerificationRequest,
        CorporateVerificationRequest,
        VerificationResponse
    )
    print("  ✅ API endpoints imported successfully")
except Exception as e:
    print(f"  ❌ FAILED: {e}")
    sys.exit(1)

# Test 5: Import main application
print("✓ Testing main application import...")
try:
    from app.main import app
    print("  ✅ FastAPI application imported successfully")
except Exception as e:
    print(f"  ❌ FAILED: {e}")
    sys.exit(1)

# Test 6: Validate settings
print("✓ Testing configuration...")
try:
    s = get_settings()
    assert isinstance(s.allowed_origins, list), "allowed_origins should be a list"
    assert len(s.allowed_origins) > 0, "allowed_origins should not be empty"
    assert s.database_url is not None, "database_url is required"
    print(f"  ✅ Configuration valid")
    print(f"     - Database: {s.database_url}")
    print(f"     - Provider: {s.verification_provider}")
    print(f"     - Environment: {s.environment}")
    print(f"     - CORS Origins: {len(s.allowed_origins)} configured")
except Exception as e:
    print(f"  ❌ FAILED: {e}")
    sys.exit(1)

# Test 7: Test database connection
print("✓ Testing database connection...")
try:
    # Test connection
    with engine.connect() as conn:
        pass
    print("  ✅ Database connection successful")
except Exception as e:
    print(f"  ❌ FAILED: {e}")
    sys.exit(1)

# Test 8: Create database tables
print("✓ Creating database tables...")
try:
    Base.metadata.create_all(bind=engine)
    
    # Verify tables were created
    from sqlalchemy import inspect
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    
    expected_tables = [
        "api_clients",
        "customers",
        "verification_results",
        "documents",
        "beneficial_owners",
        "audit_logs",
        "verification_logs",
        "workflow_approvals"
    ]
    
    missing = []
    for table in expected_tables:
        if table not in tables:
            missing.append(table)
    
    if missing:
        print(f"  ❌ FAILED: Missing tables: {missing}")
        sys.exit(1)
    
    print(f"  ✅ All {len(expected_tables)} tables created successfully")
    for table in expected_tables:
        print(f"     - {table}")
except Exception as e:
    print(f"  ❌ FAILED: {e}")
    sys.exit(1)

# Test 9: Test UUID type
print("✓ Testing UUID type compatibility...")
try:
    from uuid import uuid4
    test_uuid = uuid4()
    
    # Create a test client
    db = SessionLocal()
    try:
        test_client = ApiClient(
            id=test_uuid,
            name="Validation Test Client",
            organization="Test Org",
            api_key_hash="test_hash_for_validation",
            tier="STARTER",
            contact_email="test@test.com"
        )
        db.add(test_client)
        db.commit()
        
        # Query it back
        retrieved = db.query(ApiClient).filter(ApiClient.id == test_uuid).first()
        assert retrieved is not None, "Failed to retrieve test client"
        assert retrieved.id == test_uuid, "UUID mismatch"
        
        # Clean up
        db.delete(retrieved)
        db.commit()
        
        print("  ✅ UUID type working correctly")
    finally:
        db.close()
except Exception as e:
    print(f"  ❌ FAILED: {e}")
    sys.exit(1)

# Test 10: Test JSONB type
print("✓ Testing JSONB/JSON type compatibility...")
try:
    db = SessionLocal()
    try:
        test_customer = Customer(
            id=uuid4(),
            customer_type="INDIVIDUAL",
            first_name="Test",
            last_name="User",
            extra_data={"test_key": "test_value", "nested": {"data": 123}}
        )
        db.add(test_customer)
        db.commit()
        
        # Query it back
        retrieved = db.query(Customer).filter(Customer.id == test_customer.id).first()
        assert retrieved is not None, "Failed to retrieve test customer"
        assert retrieved.extra_data == {"test_key": "test_value", "nested": {"data": 123}}, "JSON data mismatch"
        
        # Clean up
        db.delete(retrieved)
        db.commit()
        
        print("  ✅ JSONB/JSON type working correctly")
    finally:
        db.close()
except Exception as e:
    print(f"  ❌ FAILED: {e}")
    sys.exit(1)

# Summary
print()
print("=" * 70)
print("✅ ALL VALIDATION TESTS PASSED!")
print("=" * 70)
print()
print("The application is ready to run. Start the server with:")
print()
print("  cd backend")
print("  .\\run_backend.ps1")
print()
print("Then create a test API client:")
print()
print("  python scripts\\create_test_client.py")
print()
