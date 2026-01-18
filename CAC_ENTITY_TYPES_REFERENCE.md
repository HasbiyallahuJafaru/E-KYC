# Quick Reference: CAC Entity Types

## Entity Type Detection

The system automatically detects and handles these CAC entity types:

| Entity Type | Identifier | Key Fields | Example RC Number |
|------------|-----------|------------|------------------|
| **Limited Company** | `LIMITED` | Directors, Shareholders, Share Capital | RC123456 |
| **Public Limited Company** | `PLC` | Directors, Shareholders, Share Capital | RC789012 |
| **Business Name** | `BUSINESS_NAME` | Proprietors, Nature of Business | BN12345 |
| **NGO** | `NGO` | Trustees, Aims & Objectives | RC555777 |
| **Incorporated Trustees** | `INCORPORATED_TRUSTEES` | Trustees, Aims & Objectives | IT54321 |

## Response Structure by Entity Type

### LIMITED / PLC
```json
{
  "entity_type": "LIMITED",
  "directors": [...],
  "shareholders": [...],
  "share_capital": 1000000.00,
  "company_email": "...",
  "company_phone": "..."
}
```

### BUSINESS_NAME
```json
{
  "entity_type": "BUSINESS_NAME",
  "proprietors": [...],
  "business_commencement_date": "2020-09-15",
  "nature_of_business": "General Trading"
}
```

### NGO / INCORPORATED_TRUSTEES
```json
{
  "entity_type": "INCORPORATED_TRUSTEES",
  "trustees": [...],
  "aims_and_objectives": "Educational support..."
}
```

## Database Schema

### New Columns in `verification_results`

```sql
-- Entity type identifier
cac_entity_type VARCHAR(50) -- LIMITED, PLC, BUSINESS_NAME, NGO, INCORPORATED_TRUSTEES

-- Full registered address
cac_registered_address VARCHAR(500)

-- Entity-specific structured data (JSONB)
cac_entity_data JSONB
```

### Entity Data Structure

The `cac_entity_data` JSONB field stores:

**For Limited/PLC:**
```json
{
  "directors": [{"name": "...", "position": "...", "appointment_date": "..."}],
  "shareholders": [{"name": "...", "percentage": 60.0, "is_corporate": false}],
  "share_capital": 1000000.00,
  "company_email": "...",
  "company_phone": "...",
  "city": "...",
  "state": "...",
  "lga": "..."
}
```

**For Business Names:**
```json
{
  "proprietors": [{"name": "...", "percentage": 100.0, "address": "...", "nationality": "..."}],
  "business_commencement_date": "...",
  "nature_of_business": "...",
  "city": "...",
  "state": "...",
  "lga": "..."
}
```

**For NGOs/IT:**
```json
{
  "trustees": [{"name": "...", "appointment_date": "...", "address": "..."}],
  "aims_and_objectives": "...",
  "city": "...",
  "state": "...",
  "lga": "..."
}
```

## Migration

Run this command when database is available:

```bash
cd backend
alembic upgrade head
```

## Testing Entity Types

Use these RC numbers with the mock provider:

- `RC123456` - Limited Company
- `RC789012` - PLC with corporate shareholder
- `BN12345` - Business Name
- `IT54321` - NGO/Incorporated Trustees
- `RC555777` - Alternative NGO

## UBO Analysis by Entity Type

| Entity Type | UBO Source | Notes |
|------------|-----------|-------|
| LIMITED/PLC | Shareholders ≥25% | Standard FATF rules apply |
| BUSINESS_NAME | Proprietors | Usually 100% for sole proprietor |
| NGO/IT | Trustees | Not traditional UBOs but key persons |

## Frontend Display

Entity-specific fields can be conditionally rendered:

```typescript
if (cac_data.entity_type === 'LIMITED' || cac_data.entity_type === 'PLC') {
  // Show directors, shareholders, share capital
} else if (cac_data.entity_type === 'BUSINESS_NAME') {
  // Show proprietors, nature of business
} else if (cac_data.entity_type === 'NGO' || cac_data.entity_type === 'INCORPORATED_TRUSTEES') {
  // Show trustees, aims and objectives
}
```
