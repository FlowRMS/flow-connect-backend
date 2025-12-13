# Flow CRM Backend

Backend API for Flow CRM built with FastAPI and Strawberry GraphQL.

## S3 Bucket CORS Configuration

For spec sheet PDFs to load directly in the frontend, the S3 bucket must have CORS configured.

### Configuration

| Setting | Value |
|---------|-------|
| **Origin** | `*` (or add specific origins: `http://localhost:3000`, `https://flowrms.com`, etc.) |
| **Allowed Methods** | `GET`, `HEAD` |
| **Allowed Headers** | `Content-Type`, `Range`, `Accept` |
| **Access Control Max Age** | `3600` |

### DigitalOcean Spaces

1. Go to your Space settings
2. Navigate to **CORS Configuration**
3. Click **Add** and configure with the values above
4. Save the configuration
