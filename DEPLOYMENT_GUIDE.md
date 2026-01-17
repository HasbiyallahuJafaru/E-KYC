# E-KYC Check Platform - Deployment Guide

## Issues Fixed

### Database Compatibility
✅ Created `app/core/types.py` with cross-database TypeDecorator classes
- UUID type: PostgreSQL (native UUID) / SQLite (CHAR(36) with conversion)
- JSONB type: PostgreSQL (native JSONB) / SQLite (JSON)

✅ Updated all 8 database models to use compatible types:
- api_client.py
- customer.py
- verification_result.py
- document.py
- beneficial_owner.py
- audit_log.py
- verification_log.py
- workflow.py

✅ Fixed database engine configuration (`app/core/database.py`):
- Connection pooling: PostgreSQL only
- SQLite connect_args: `{"check_same_thread": False}`
- search_path event listener: Graceful fallback for SQLite

✅ Fixed reserved column name conflicts:
- Renamed `metadata` → `extra_data` in customer.py and audit_log.py

### Configuration Issues
✅ Fixed `app/core/config.py`:
- Changed `database_url` from PostgresDsn to str (accepts SQLite URLs)
- Changed `redis_url` from RedisDsn to str
- Fixed `allowed_origins` type from str to list[str]
- Fixed field validator with mode="before"
- Added `get_settings()` function

### Model Issues
✅ Fixed `app/models/verification_log.py`:
- Added missing `Boolean` import
- Changed `SQLEnum(name="boolean")` → `Boolean` for `success` and `billed` fields

### API Endpoint Issues
✅ Fixed `app/api/external/v1/verification.py`:
- Removed duplicate VerificationResult creation (orchestrator already creates it)
- Fixed orchestrator method signatures: Pass `Customer` object instead of individual parameters
- Fixed result access: Changed from nested dataclass attributes to model fields
  - Example: `result.bvn_data.verified` → `result.bvn_verified`
- Fixed VerificationLog field names:
  - `api_client_id` → `client_id`
  - `verification_type` → `request_type`
  - `status` → `success` (Boolean)
  - `billable` → `billed`
  - `amount_naira` → `cost_ngn`
  - Added required fields: `endpoint`, `request_id`, `status_code`, `billing_month`
- Fixed error handling to work without pre-created verification_id

### Application Initialization
✅ Fixed `app/main.py`:
- Added automatic table creation on startup: `Base.metadata.create_all(bind=engine)`
- Imported all models to register with Base
- Properly imported engine and Base from database module

### Frontend Issues
✅ Fixed `package.json`:
- Added missing dependencies: axios, react-hook-form, zod, @hookform/resolvers, react-router-dom

✅ Fixed `tsconfig.app.json`:
- Added path alias configuration: `@/*` → `./src/*`

✅ Fixed `vite.config.ts`:
- Added path alias resolution for `@` imports

✅ Fixed `src/services/api.ts`:
- Added explicit `any` types for axios interceptor parameters

✅ Fixed `src/components/IndividualVerificationForm.tsx`:
- Changed `err: any` to proper error handling pattern
- Added explicit types for map callback parameters

✅ Fixed `src/components/CorporateVerificationForm.tsx`:
- Changed `err: any` to proper error handling pattern
- Added explicit types for UBO and action map callbacks

✅ Created missing files:
- `frontend/.env` with API configuration
- `frontend/run_frontend.ps1` startup script
- `run_platform.ps1` for launching both servers

## Quick Start (Local Development with SQLite)

### Option 1: Run Everything at Once (Recommended)

```powershell
# From the E-KYC root directory
.\run_platform.ps1
```

This will automatically:
- Start backend on http://localhost:8000
- Start frontend on http://localhost:5173
- Open two PowerShell windows (one for each server)

### Option 2: Manual Step-by-Step

#### 1. Backend Setup

```powershell
# Navigate to backend directory
cd c:\Users\User\Documents\E-KYC\backend

# Start the backend server (virtual env already activated)
.\run_backend.ps1
```

The backend will be available at:
- **API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

#### 2. Frontend Setup

```powershell
# In a new terminal, navigate to frontend
cd c:\Users\User\Documents\E-KYC\frontend

# Install dependencies and start dev server
.\run_frontend.ps1
```

The frontend will be available at: http://localhost:5173

#### 3. Create API Client for Testing

```powershell
# In backend directory
cd c:\Users\User\Documents\E-KYC\backend
python scripts\create_test_client.py
```

This will output an API key. Copy it and update `frontend/.env`:

```dotenv
VITE_API_KEY=<paste-your-api-key-here>
```

Then refresh the frontend page.

## Testing the API

### 1. Health Check
```powershell
curl http://localhost:8000/health
```

### 2. Get API Token

You'll need to create an API client first. For testing with mock provider:

**Mock Test Data:**
- BVN: `22123456789`
- NIN: `12345678901`
- RC Number: `RC123456`

### 3. Test Individual Verification

```powershell
curl -X POST http://localhost:8000/api/v1/verify/individual `
  -H "Content-Type: application/json" `
  -H "Authorization: Bearer YOUR_API_KEY" `
  -d '{
    "bvn": "22123456789",
    "nin": "12345678901",
    "first_name": "Test",
    "last_name": "User"
  }'
```

### 4. Test Corporate Verification

```powershell
curl -X POST http://localhost:8000/api/v1/verify/corporate `
  -H "Content-Type: application/json" `
  -H "Authorization: Bearer YOUR_API_KEY" `
  -d '{
    "rc_number": "RC123456",
    "business_name": "Test Company Ltd"
  }'
```

## Database

The application uses **SQLite** for local development:
- Database file: `backend/ekyc.db`
- Automatically created on first run
- Tables created via SQLAlchemy: `Base.metadata.create_all()`

## Configuration

All configuration in `backend/.env`:

```dotenv
# Database (SQLite for local dev)
DATABASE_URL=sqlite:///./ekyc.db

# Verification Provider
VERIFICATION_PROVIDER=mock  # Use mock for testing

# Security
JWT_SECRET=your-secret-key-min-32-characters-long-change-in-production

# API
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173
```

## Architecture

### Backend Structure
```
backend/
├── app/
│   ├── api/
│   │   └── external/v1/      # Revenue-generating API endpoints
│   ├── core/
│   │   ├── types.py          # Cross-database type compatibility
│   │   ├── config.py         # Pydantic settings
│   │   ├── database.py       # SQLAlchemy setup
│   │   └── security.py       # API key auth
│   ├── models/               # 8 database models
│   ├── services/
│   │   ├── providers/        # Mock + VerifyMe.ng
│   │   ├── cross_validator.py
│   │   ├── ubo_analyzer.py
│   │   ├── risk_engine.py
│   │   └── verification_orchestrator.py
│   └── main.py              # FastAPI application
├── .env                     # Configuration
└── requirements.txt         # Dependencies
```

### Frontend Structure
```
frontend/
├── src/
│   ├── components/          # React components
│   ├── services/
│   │   └── api.ts          # Axios API client
│   ├── types/
│   │   └── api.ts          # TypeScript interfaces
│   └── pages/              # Page components
└── package.json
```

## Production Deployment

For production with PostgreSQL:

1. Update `.env`:
```dotenv
DATABASE_URL=postgresql://user:password@localhost:5432/ekyc_db
VERIFICATION_PROVIDER=verifyme
VERIFYME_LIVE_SECRET=your_live_secret_key
USE_TEST_KEYS=false
ENVIRONMENT=production
```

2. Install PostgreSQL driver:
```powershell
pip install psycopg2-bwith all dependencies installed
3. ✅ Path aliases configured (@/ imports working)
4. ⏳ Create initial API client for testing (run `create_test_client.py`)
5. ⏳ Update frontend/.env with API key
6. ⏳ Test end-to-end verification flow
7. The same code works with PostgreSQL (auto-detects database type)

## Troubleshooting

### Database Issues
- **Error**: "no such table"
  - **Solution**: Delete `ekyc.db` and restart - tables will be recreated

### Import Errors
- **Error**: "cannot import name 'UUID'"
  - **Solution**: Check that `app/core/types.py` exists and is imported correctly

### API Key Issues
- **Error**: "401 Unauthorized"
  - **Solution**: You need to create an API client first (TODO: Add admin endpoint)

### Port Already in Use
- **Error**: "Address already in use"
  - **Solution**: Change port in `run_backend.ps1` (default: 8000)

## Next Steps

1. ✅ Backend running with automatic table creation
2. ✅ Frontend running and connecting to backend
3. ⏳ Create initial API client for testing
4. ⏳ Test end-to-end verification flow
5. ⏳ Set up VerifyMe.ng production credentials

## Support

For issues, check:
1. Backend logs in console
2. Frontend console (F12 in browser)
3. Database file: `backend/ekyc.db`
4. API documentation: http://localhost:8000/docs
