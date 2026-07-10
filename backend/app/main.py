import urllib.parse
from typing import Optional
from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from app.storage import storage
from app.logic import is_valid_url, is_valid_alias, generate_short_code

app = FastAPI(
    title="URL Shortener API",
    description="A minimal and clean Python backend for shortening URLs.",
    version="1.0.0"
)

# Enable CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for dev simplicity
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ShortenRequest(BaseModel):
    url: str = Field(..., description="The long URL to shorten.")
    custom_alias: Optional[str] = Field(None, description="Optional custom alphanumeric alias.")
    generate_qr: Optional[bool] = Field(False, description="Whether to generate a QR code.")

class ShortenResponse(BaseModel):
    short_code: str
    short_url: str
    original_url: str
    qr_code: Optional[str] = None

@app.post("/shorten", response_model=ShortenResponse, status_code=201)
async def shorten_url(payload: ShortenRequest, request: Request):
    url = payload.url.strip()
    custom_alias = payload.custom_alias.strip() if payload.custom_alias else None
    
    # 1. Validate the original URL
    if not is_valid_url(url):
        raise HTTPException(
            status_code=400,
            detail="Invalid URL format. Make sure it includes http:// or https:// and a valid domain name."
        )
        
    # 2. Check if this exact long URL is already shortened (only if no custom alias is requested)
    base_url = str(request.base_url)
    if not custom_alias:
        existing_link = storage.get_link_by_url(url)
        if existing_link:
            if payload.generate_qr and not existing_link.get("qr_code"):
                existing_link["qr_code"] = f"https://api.qrserver.com/v1/create-qr-code/?size=150x150&data={urllib.parse.quote(url)}"
            return ShortenResponse(
                short_code=existing_link["short_code"],
                short_url=f"{base_url}{existing_link['short_code']}",
                original_url=existing_link["original_url"],
                qr_code=existing_link.get("qr_code")
            )

    # 3. Handle custom alias if provided
    if custom_alias:
        # Validate custom alias format
        if not is_valid_alias(custom_alias):
            raise HTTPException(
                status_code=400,
                detail="Invalid custom alias. It must be alphanumeric and hyphens only, and between 1-30 characters."
            )
            
        # Check if alias is already taken
        if storage.get_link_by_code(custom_alias) is not None:
            raise HTTPException(
                status_code=400,
                detail=f"Custom alias '{custom_alias}' is already taken."
            )
            
        short_code = custom_alias
    else:
        # 4. Generate short code with collision retry logic (up to 10 attempts)
        short_code = None
        for _ in range(10):
            candidate = generate_short_code()
            if storage.get_link_by_code(candidate) is None:
                short_code = candidate
                break
                
        if not short_code:
            raise HTTPException(
                status_code=500,
                detail="Failed to generate a unique short code. Please try again."
            )

    # 5. Save and return
    short_url = f"{base_url}{short_code}"
    qr_code_url = None
    if payload.generate_qr:
        qr_code_url = f"https://api.qrserver.com/v1/create-qr-code/?size=150x150&data={urllib.parse.quote(url)}"
    saved_link = storage.save_link(short_code, url, qr_code=qr_code_url)
    return ShortenResponse(
        short_code=saved_link["short_code"],
        short_url=short_url,
        original_url=saved_link["original_url"],
        qr_code=saved_link.get("qr_code")
    )

@app.get("/links")
async def get_all_links(request: Request, clear: Optional[bool] = None):
    if clear:
        storage.clear()
    links = storage.get_all_links()
    base_url = str(request.base_url)
    
    # Map stored links to include full short_url for frontend convenience
    return [
        {
            "short_code": link["short_code"],
            "original_url": link["original_url"],
            "clicks": link["clicks"],
            "created_at": link["created_at"],
            "short_url": f"{base_url}{link['short_code']}",
            "qr_code": link.get("qr_code")
        }
        for link in links
    ]

@app.get("/{code}")
async def redirect_to_url(code: str):
    link = storage.get_link_by_code(code)
    if not link:
        raise HTTPException(
            status_code=404,
            detail="Short URL code not found."
        )
    
    storage.increment_clicks(code)
    return RedirectResponse(url=link["original_url"])

@app.get("/stats/{code}")
async def get_link_stats(code: str):
    link = storage.get_link_by_code(code)
    if not link:
        raise HTTPException(
            status_code=404,
            detail="Short URL code not found."
        )
    return {
        "short_code": link["short_code"],
        "original_url": link["original_url"],
        "clicks": link["clicks"],
        "created_at": link["created_at"]
    }
