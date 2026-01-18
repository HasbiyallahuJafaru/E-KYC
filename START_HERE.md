# E-KYC Platform - Quick Start

## One-Command Startup

Simply run:

```powershell
.\start.ps1
```

This will:
- Start the backend API on http://localhost:8000
- Start the frontend UI on http://localhost:5173
- Open two PowerShell windows (one for backend, one for frontend)

**Important**: Keep both PowerShell windows open while using the application.

## Alternative: Run Backend Only

```powershell
cd backend
.\run_backend.ps1
```

## Alternative: Run Frontend Only

```powershell
cd frontend
.\run_frontend.ps1
```

## Stopping the Application

Close both PowerShell windows, or press `Ctrl+C` in each window.

## First Time Setup

If this is your first time running the platform:

1. Make sure Python virtual environment is set up:
   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   pip install -r backend\requirements.txt
   ```

2. Install frontend dependencies:
   ```powershell
   cd frontend
   npm install
   ```

3. Create an API key for testing:
   ```powershell
   cd backend
   python scripts\create_test_client.py
   ```

4. Copy the API key and update `frontend\.env`:
   ```
   VITE_API_KEY=your-api-key-here
   ```

## Testing

Once running, visit:
- **Frontend**: http://localhost:5173
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

Test with these sample RC numbers:
- `RC123456` - Standard company (Low risk ~7/30)
- `BN12345` - Business name
- `IT54321` - NGO
- `RC999999` - High-risk company (demonstrates risk factors)
