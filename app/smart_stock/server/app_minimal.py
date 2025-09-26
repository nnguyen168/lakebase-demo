"""Minimal FastAPI application for debugging deployment issues."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
  title='Databricks App API (Minimal)',
  description='Minimal FastAPI application for debugging deployment',
  version='0.1.0',
)

app.add_middleware(
  CORSMiddleware,
  allow_origins=['*'],
  allow_credentials=True,
  allow_methods=['*'],
  allow_headers=['*'],
)

@app.get('/health')
async def health():
  """Health check endpoint."""
  return {'status': 'healthy', 'message': 'Minimal app is running'}

@app.get('/')
async def root():
  """Root endpoint."""
  return {'message': 'Databricks App is running!'}