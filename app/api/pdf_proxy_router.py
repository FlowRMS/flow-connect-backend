"""PDF Proxy Router - Downloads and serves external PDFs to avoid CORS issues."""

import httpx
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import Response

router = APIRouter()


@router.get("/pdf-proxy")
async def pdf_proxy(url: str = Query(..., description="URL of the PDF to proxy")):
    """
    Proxy endpoint to fetch external PDFs and serve them locally.
    This avoids CORS issues when trying to load PDFs from external domains.
    """
    if not url:
        raise HTTPException(status_code=400, detail="URL parameter is required")

    # Validate URL starts with http/https
    if not url.startswith(("http://", "https://")):
        raise HTTPException(status_code=400, detail="Invalid URL format")

    try:
        async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
            response = await client.get(url)
            response.raise_for_status()

            # Get content type from response, default to PDF
            content_type = response.headers.get("content-type", "application/pdf")

            # Return the PDF content with proper headers
            return Response(
                content=response.content,
                media_type=content_type,
                headers={
                    "Content-Disposition": "inline",
                    "Access-Control-Allow-Origin": "*",
                },
            )

    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="Request to external PDF timed out")
    except httpx.HTTPStatusError as e:
        raise HTTPException(
            status_code=e.response.status_code,
            detail=f"External server returned error: {e.response.status_code}",
        )
    except httpx.RequestError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch PDF: {str(e)}",
        )
