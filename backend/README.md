# E-KYC Check - Backend API

Compliance-as-a-Service platform for Nigerian financial institutions. White-labeled KYC verification API that proxies to VerifyMe.ng with added intelligence (BVN/NIN cross-validation, CAC/UBO analysis, FATF/CBN risk scoring).

## Features

- **BVN/NIN Verification**: Cross-validates individual identity data
- **CAC Corporate Lookup**: Identifies Ultimate Beneficial Owners (≥25%)
- **FATF/CBN Compliance**: Transparent risk scoring engine
- **Print-Ready Reports**: Branded HTML/PDF verification reports
- **Multi-Tenant**: Row-Level Security for branch/zone isolation
- **Audit Trail**: Immutable WORM logs for 5-year compliance
- **Mock Provider**: Test without external API calls

## Tech Stack

- **Framework**: FastAPI (Python 3.12)
- **Database**: PostgreSQL 16 with SQLAlchemy 2.0
- **Cache**: Redis 7
- **Authentication**: API Keys (SHA-256) + JWT for internal dashboard
- **External API**: VerifyMe.ng (configurable provider)

## Quick Start

### Prerequisites

- Python 3.12+
- PostgreSQL 16+
- Redis 7+
- OR Docker + Docker Compose

### Option 1: Docker (Recommended)

```powershell
# Start all services
docker-compose up -d

# Run migrations
docker-compose exec api alembic upgrade head

# Check health
curl http://localhost:8000/health

# View logs
docker-compose logs -f api
```

### Option 2: Local Development

1. **Install Dependencies**

```powershell
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

2. **Setup Database**

```powershell
# Create PostgreSQL database
psql -U postgres
CREATE DATABASE ekyc_db;
CREATE USER ekyc WITH PASSWORD 'ekyc_password';
GRANT ALL PRIVILEGES ON DATABASE ekyc_db TO ekyc;
\q

# Run migrations
alembic upgrade head
```

3. **Configure Environment**

```powershell
# Copy example environment
copy .env.example .env

# Edit .env with your settings
notepad .env
```

4. **Start Server**

```powershell
uvicorn app.main:app --reload
```

## Configuration

Key environment variables (see `.env.example` for full list):

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | - |
| `REDIS_URL` | Redis connection string | - |
| `VERIFICATION_PROVIDER` | Provider (`mock` or `verifyme`) | `mock` |
| `VERIFYME_SECRET_KEY` | VerifyMe.ng API key | - |
| `JWT_SECRET` | Secret for JWT signing | - |
| `ENVIRONMENT` | `development`, `staging`, or `production` | `development` |

## API Documentation

Once running, visit:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Authentication

External API uses Bearer token authentication:

```http
Authorization: Bearer <your-api-key>
```

### Example Requests

**Individual Verification**

```bash
curl -X POST http://localhost:8000/api/v1/verify/individual \
  -H "Authorization: Bearer <your-api-key>" \
  -H "Content-Type: application/json" \
  -d '{
    "bvn": "22123456789",
    "nin": "12345678901",
    "first_name": "John",
    "last_name": "Obi"
  }'
```

**Corporate Verification**

```bash
curl -X POST http://localhost:8000/api/v1/verify/corporate \
  -H "Authorization: Bearer <your-api-key>" \
  -H "Content-Type: application/json" \
  -d '{
    "rc_number": "RC123456",
    "business_name": "Alpha Trading Limited"
  }'
```

**Get Report**

```bash
curl http://localhost:8000/api/v1/reports/{verification_id} \
  -H "Authorization: Bearer <your-api-key>"
```

## Mock Provider Test Data

When `VERIFICATION_PROVIDER=mock`:

| Type | Valid Input | Returns |
|------|-------------|---------|
| BVN | `22123456789` | Verified with name "OBI, JOHN PAUL" |
| NIN | `12345678901` | Verified with name "JOHN PAUL OBI" |
| CAC | `RC123456` | Verified with 2 UBOs (60%, 40%) |

Use these values to test cross-validation and risk scoring without external API calls.

## Database Migrations

```powershell
# Create new migration
alembic revision --autogenerate -m "Add new table"

# Apply migrations
alembic upgrade head

# Rollback one version
alembic downgrade -1

# View migration history
alembic history
```

## Project Structure

```
backend/
├── alembic/              # Database migrations
│   └── versions/         # Migration scripts
├── app/
│   ├── api/              # API endpoints
│   │   ├── external/     # Client-facing API
│   │   │   └── v1/       # Version 1
│   │   └── internal/     # Internal dashboard (TODO)
│   ├── core/             # Core infrastructure
│   │   ├── config.py     # Settings management
│   │   ├── database.py   # SQLAlchemy setup
│   │   ├── logging.py    # Structured logging
│   │   ├── security.py   # Authentication
│   │   └── exceptions.py # Custom exceptions
│   ├── models/           # SQLAlchemy models
│   │   ├── api_client.py
│   │   ├── customer.py
│   │   ├── verification_result.py
│   │   └── ...
│   ├── services/         # Business logic
│   │   ├── providers/    # Verification providers
│   │   │   ├── base.py   # Interface
│   │   │   ├── mock.py   # Mock provider
│   │   │   └── verifyme.py # VerifyMe.ng client
│   │   ├── cross_validator.py
│   │   ├── ubo_analyzer.py
│   │   ├── risk_engine.py
│   │   ├── verification_orchestrator.py
│   │   └── report_generator.py
│   └── main.py           # FastAPI application
├── tests/                # Test suite (TODO)
├── .env.example          # Environment template
├── requirements.txt      # Python dependencies
├── alembic.ini           # Alembic config
├── Dockerfile            # Container build
└── docker-compose.yml    # Local stack
```

## Risk Scoring

The system implements FATF-compliant risk scoring with transparent breakdown:

- **Customer Risk** (35%): Type, PEP status, occupation
- **Geographic Risk** (25%): Nationality, FATF lists
- **Product Risk** (20%): Transaction types, amounts
- **Channel Risk** (20%): Delivery method, remote vs face-to-face

Risk Categories:
- **LOW**: Score < 30 (Simplified Due Diligence)
- **MEDIUM**: Score 30-60 (Standard Due Diligence)
- **HIGH**: Score 60-90 (Enhanced Due Diligence)
- **PROHIBITED**: Score ≥ 90 (Reject transaction)

## Compliance Features

- **FATF Recommendation 10-12**: KYC/CDD implementation
- **FATF Recommendation 24**: UBO identification (≥25% threshold)
- **CBN AML/CFT Regulations 2022**: Risk-based approach
- **5-Year Retention**: WORM audit logs
- **Row-Level Security**: Multi-tenant data isolation

## Development

### Code Style

- Follow PEP 8 guidelines
- Use type hints
- Keep functions focused and readable
- Document with docstrings
- Avoid over-engineering

### Running Tests

```powershell
# Run all tests
pytest

# Run with coverage
pytest --cov=app tests/

# Run specific test file
pytest tests/test_risk_engine.py
```

## Deployment

### Production Checklist

- [ ] Set `ENVIRONMENT=production`
- [ ] Generate strong `JWT_SECRET`
- [ ] Configure `VERIFYME_SECRET_KEY`
- [ ] Set `ALLOWED_ORIGINS` to frontend domain
- [ ] Enable PostgreSQL SSL
- [ ] Configure Redis AUTH
- [ ] Set up database backups
- [ ] Configure logging aggregation
- [ ] Enable HTTPS
- [ ] Set up monitoring/alerting

### Environment Variables for Production

```env
ENVIRONMENT=production
DATABASE_URL=postgresql://user:pass@prod-db:5432/ekyc_db?sslmode=require
REDIS_URL=redis://:password@prod-redis:6379/0
VERIFICATION_PROVIDER=verifyme
VERIFYME_SECRET_KEY=<actual-secret>
JWT_SECRET=<generate-with-secrets.token-urlsafe-32>
ALLOWED_ORIGINS=https://app.yourdomain.com
LOG_LEVEL=INFO
```

## Pricing

All verifications are billable at ₦1000 per request, regardless of success/failure.

## Support

For issues or questions:
- Check API documentation at `/docs`
- Review logs with `docker-compose logs api`
- Verify environment configuration in `.env`

## License

Proprietary - All rights reserved
