# CAC Entity Type Support - Implementation Summary

## Overview

Enhanced the E-KYC platform to properly handle different types of business entities registered with the Corporate Affairs Commission (CAC) in Nigeria. The system now properly differentiates between and stores complete information for:

1. **Limited Companies (Ltd)** - Private limited companies
2. **Public Limited Companies (PLC)** - Publicly traded companies  
3. **Business Names (BN)** - Sole proprietorships and partnerships
4. **NGOs** - Non-governmental organizations
5. **Incorporated Trustees (IT)** - Charitable/religious organizations

## Problem Statement

Previously, the CAC verification response used a generic structure that only supported limited companies with directors and shareholders. This meant:

- Business Names didn't capture proprietor information properly
- NGOs/Incorporated Trustees couldn't store trustee data
- Entity-specific fields (aims/objectives for NGOs, nature of business for BNs) were lost
- The response didn't accurately reflect the actual CAC document structure

## Solution

### 1. Enhanced Data Models

#### Backend Provider Models (`app/services/providers/base.py`)

Added new dataclasses for entity-specific information:

```python
@dataclass
class ProprietorInfo:
    """Business name proprietor/partner information."""
    name: str
    percentage: Optional[float] = None  # For partnerships
    address: Optional[str] = None
    nationality: Optional[str] = None

@dataclass
class TrusteeInfo:
    """NGO/Incorporated Trustee information."""
    name: str
    appointment_date: Optional[str] = None
    address: Optional[str] = None
```

Enhanced `CACResult` to include all entity-specific fields:

```python
@dataclass
class CACResult:
    entity_type: Optional[str]  # LIMITED, PLC, BUSINESS_NAME, NGO, INCORPORATED_TRUSTEES
    
    # Fields for Limited Companies (Ltd/PLC)
    directors: list[DirectorInfo]
    shareholders: list[ShareholderInfo]
    share_capital: Optional[float]
    
    # Fields for Business Names
    proprietors: list[ProprietorInfo]
    business_commencement_date: Optional[str]
    nature_of_business: Optional[str]
    
    # Fields for NGOs/Incorporated Trustees
    trustees: list[TrusteeInfo]
    aims_and_objectives: Optional[str]
    
    # Common location fields
    city, state, lga, postal_code, branch_address
```

#### API Schemas (`app/api/schemas.py`)

Added corresponding Pydantic schemas for API responses:

- `DirectorInfo`, `ShareholderInfo`, `ProprietorInfo`, `TrusteeInfo`
- Enhanced `CACData` with all entity-specific fields

#### Database Model (`app/models/verification_result.py`)

Added new columns:

- `cac_entity_type` - Stores the entity type (LIMITED, PLC, BUSINESS_NAME, etc.)
- `cac_registered_address` - Full registered office address
- `cac_entity_data` - JSONB field storing all entity-specific structured data

### 2. VerifyMe Provider Enhancement (`app/services/providers/verifyme.py`)

Updated the `verify_cac` method to:

1. Detect entity type from the API response
2. Parse entity-specific fields based on the detected type:
   - **Limited/PLC**: Directors, shareholders, share capital, contact info
   - **Business Names**: Proprietors, commencement date, nature of business
   - **NGOs/IT**: Trustees, aims and objectives

```python
# Normalize entity type from various possible formats
if "business name" in company_type.lower():
    entity_type = "BUSINESS_NAME"
elif "ngo" in company_type.lower():
    entity_type = "NGO"
elif "incorporated trustees" in company_type.lower():
    entity_type = "INCORPORATED_TRUSTEES"
# ... parse entity-specific fields accordingly
```

### 3. Mock Provider Enhancement (`app/services/providers/mock.py`)

Added test data for all entity types:

- **RC123456**: Limited company with directors and shareholders
- **BN-prefixed**: Business name with proprietor
- **IT-prefixed or RC555777**: NGO with trustees

### 4. UBO Analyzer Enhancement (`app/services/ubo_analyzer.py`)

Updated to handle different ownership structures:

```python
if entity_type in ["LIMITED", "PLC"]:
    # Analyze shareholders for UBOs
elif entity_type == "BUSINESS_NAME":
    # Analyze proprietors as UBOs
elif entity_type in ["NGO", "INCORPORATED_TRUSTEES"]:
    # Analyze trustees (not traditional UBOs but persons of interest)
```

### 5. Verification Orchestrator (`app/services/verification_orchestrator.py`)

Enhanced to store entity-specific data in the database:

- Converts directors/shareholders/proprietors/trustees to JSONB format
- Stores in `cac_entity_data` field for retrieval
- Preserves all entity-specific information

### 6. API Endpoint (`app/api/external/v1/verification.py`)

Added helper function `_build_cac_data()` to:

- Convert database records to API response format
- Include all entity-specific fields based on entity type
- Properly serialize directors, shareholders, proprietors, trustees

### 7. Frontend Types (`frontend/src/types/api.ts`)

Updated TypeScript interfaces to match backend schema:

```typescript
export interface CACData {
  entity_type?: 'LIMITED' | 'PLC' | 'BUSINESS_NAME' | 'NGO' | 'INCORPORATED_TRUSTEES';
  
  // Ltd/PLC fields
  directors?: DirectorInfo[];
  shareholders?: ShareholderInfo[];
  share_capital?: number;
  
  // Business Name fields
  proprietors?: ProprietorInfo[];
  nature_of_business?: string;
  
  // NGO fields
  trustees?: TrusteeInfo[];
  aims_and_objectives?: string;
  
  // Location data
  city?: string;
  state?: string;
  lga?: string;
}
```

## Database Migration

Created Alembic migration `001_add_cac_entity_type_fields.py`:

```python
def upgrade():
    op.add_column('verification_results', 
        sa.Column('cac_entity_type', sa.String(50), nullable=True))
    op.add_column('verification_results', 
        sa.Column('cac_registered_address', sa.String(500), nullable=True))
    op.add_column('verification_results', 
        sa.Column('cac_entity_data', sa.dialects.postgresql.JSONB, nullable=True))
```

To apply migration (when database is set up):
```bash
cd backend
alembic upgrade head
```

## API Response Examples

### Limited Company (Ltd)

```json
{
  "cac_data": {
    "verified": true,
    "company_name": "ALPHA TRADING LIMITED",
    "entity_type": "LIMITED",
    "status": "ACTIVE",
    "incorporation_date": "2018-06-12",
    "registered_address": "Plot 15, Adeola Odeku Street, Victoria Island, Lagos",
    "directors": [
      {
        "name": "John Paul Obi",
        "position": "Managing Director",
        "appointment_date": "2018-06-12"
      }
    ],
    "shareholders": [
      {
        "name": "John Paul Obi",
        "percentage": 60.0,
        "is_corporate": false
      }
    ],
    "share_capital": 1000000.00,
    "company_email": "info@alphatrading.ng",
    "city": "Lagos",
    "state": "Lagos"
  }
}
```

### Business Name

```json
{
  "cac_data": {
    "verified": true,
    "company_name": "PRECIOUS VENTURES",
    "entity_type": "BUSINESS_NAME",
    "status": "ACTIVE",
    "incorporation_date": "2020-09-05",
    "business_commencement_date": "2020-09-15",
    "registered_address": "23 Market Road, Aba, Abia State",
    "nature_of_business": "General Trading and Commerce",
    "proprietors": [
      {
        "name": "Precious Okoro",
        "percentage": 100.0,
        "address": "23 Market Road, Aba, Abia State",
        "nationality": "Nigerian"
      }
    ],
    "city": "Aba",
    "state": "Abia"
  }
}
```

### NGO/Incorporated Trustees

```json
{
  "cac_data": {
    "verified": true,
    "company_name": "HOPE FOR THE FUTURE FOUNDATION",
    "entity_type": "INCORPORATED_TRUSTEES",
    "status": "ACTIVE",
    "incorporation_date": "2017-03-10",
    "registered_address": "56 Community Road, Surulere, Lagos",
    "aims_and_objectives": "To provide educational support and scholarships to underprivileged children in Nigeria",
    "trustees": [
      {
        "name": "Dr. Folake Adeyemi",
        "appointment_date": "2017-03-10",
        "address": "12 Palm Avenue, Victoria Island, Lagos"
      },
      {
        "name": "Chief Michael Okonkwo",
        "appointment_date": "2017-03-10",
        "address": "34 Iju Road, Agege, Lagos"
      }
    ],
    "city": "Lagos",
    "state": "Lagos"
  }
}
```

## Testing

### Manual Testing with Mock Provider

Test different entity types:

```bash
# Limited Company
curl -X POST http://localhost:8000/api/v1/verify/corporate \
  -H "Authorization: Bearer <token>" \
  -d '{"rc_number": "RC123456"}'

# Business Name
curl -X POST http://localhost:8000/api/v1/verify/corporate \
  -H "Authorization: Bearer <token>" \
  -d '{"rc_number": "BN12345"}'

# NGO
curl -X POST http://localhost:8000/api/v1/verify/corporate \
  -H "Authorization: Bearer <token>" \
  -d '{"rc_number": "IT54321"}'
```

## Benefits

1. **Accuracy**: Responses now match actual CAC document structures
2. **Completeness**: All entity-specific information is preserved
3. **Flexibility**: Easy to add new entity types in the future
4. **Compliance**: Proper storage of trustee/proprietor info for regulatory reporting
5. **UBO Analysis**: Correctly identifies beneficial owners based on entity structure

## Files Modified

### Backend
- `app/services/providers/base.py` - Added entity-specific dataclasses
- `app/api/schemas.py` - Added API response schemas
- `app/models/verification_result.py` - Added database columns
- `app/services/providers/verifyme.py` - Enhanced CAC parsing
- `app/services/providers/mock.py` - Added test data for all entity types
- `app/services/ubo_analyzer.py` - Enhanced UBO analysis for different entities
- `app/services/verification_orchestrator.py` - Store entity-specific data
- `app/api/external/v1/verification.py` - Build complete CAC responses

### Frontend
- `src/types/api.ts` - Updated TypeScript interfaces

### Database
- `alembic/versions/001_add_cac_entity_type_fields.py` - Migration for new fields

## Next Steps

1. **Run migration** when database is available
2. **Test with real VerifyMe.ng API** to verify actual response formats
3. **Update frontend UI** to display entity-specific fields appropriately
4. **Update report templates** to include entity-specific sections
5. **Add entity type filter** to verification search/listing

## Notes

- The system maintains backward compatibility - existing records without entity_type will still work
- Raw CAC data is still preserved in `cac_data` JSONB field for audit purposes
- Entity-specific data is normalized in `cac_entity_data` for easy querying and display
