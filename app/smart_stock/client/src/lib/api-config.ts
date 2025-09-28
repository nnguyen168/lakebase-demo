import { OpenAPI } from '@/fastapi_client/core/OpenAPI';

// Configure API client for both local development and Databricks Apps deployment
export function configureApiClient() {
  // Determine if we're in production (Databricks Apps) or local development
  const isProduction = window.location.hostname !== 'localhost' &&
                      window.location.hostname !== '127.0.0.1';

  if (isProduction) {
    // In production (Databricks Apps), use relative path for API calls
    // The app proxy will handle authentication
    OpenAPI.BASE = '';
    OpenAPI.WITH_CREDENTIALS = true;
    OpenAPI.CREDENTIALS = 'include';
  } else {
    // In development, use the local backend URL
    OpenAPI.BASE = 'http://localhost:8000';
    OpenAPI.WITH_CREDENTIALS = true;
    OpenAPI.CREDENTIALS = 'include';
  }

  console.log('API configured:', {
    base: OpenAPI.BASE,
    withCredentials: OpenAPI.WITH_CREDENTIALS,
    credentials: OpenAPI.CREDENTIALS,
    environment: isProduction ? 'production' : 'development'
  });
}