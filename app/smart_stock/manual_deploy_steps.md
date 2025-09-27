# Manual Deployment Steps for SmartStock App

Since the authentication token is not working from the CLI, here are the manual steps to update your Databricks Apps deployment:

## What Has Been Changed

### 1. Backend Changes
- **Removed all hardcoded values** from `/server/routers/otpr.py`
- **Created new endpoint** `/server/routers/inventory_turnover.py` for inventory turnover metrics
- Both endpoints now read directly from database views with no fallbacks

### 2. Frontend Changes
- **Updated** `client/src/pages/SmartStockDashboard.tsx` to fetch KPIs from database
- Added dynamic trend indicators and previous period comparisons
- Frontend build has been updated in `client/build/`

### 3. Configuration Changes
- **Removed** OTPR override environment variables from `app.yaml`
- Database credentials remain in `app.yaml`

## Files to Deploy

The following files need to be deployed to update your app:

1. `server/routers/otpr.py` - Updated OTPR endpoint
2. `server/routers/inventory_turnover.py` - New inventory turnover endpoint
3. `server/routers/__init__.py` - Router registration
4. `client/build/` - Entire directory with updated frontend build
5. `app.yaml` - Updated configuration

## Expected Results After Deployment

Once deployed, your KPIs should show:
- **OTPR**: 74.3% (current), 97.3% (previous) with red down arrow
- **Inventory Turnover**: 31.49x with 12 days on hand

## Alternative: Direct Database Query

To verify your database views are correct, run these queries:

```sql
-- Check OTPR view
SELECT * FROM public.otpr;

-- Check Inventory Turnover view
SELECT * FROM public.inventory_turnover;
```

The app should display exactly what these views return.

## Testing the Deployed App

After deployment, check the browser console (F12) for these log messages:
- "loadKpis called - starting to load KPIs..."
- "OTPR Data from API: {data}"
- "Inventory Turnover Data from API: {data}"

This will confirm the frontend is calling the correct endpoints.