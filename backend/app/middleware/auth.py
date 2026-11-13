from fastapi import Request, HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.auth_service import decode_token, get_user_by_id
from app.services.domain_service import domains_match, normalize_domain
from app.models.models import User

security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> User:
    """Extract and validate the current user from JWT token."""
    token = credentials.credentials
    payload = decode_token(token)
    
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
        )
    
    user = get_user_by_id(db, user_id)
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is deactivated",
        )
    
    return user


async def validate_site_key(request: Request, db: Session = Depends(get_db)):
    """Validate site key from widget requests (used for public chat endpoint)."""
    site_key = request.headers.get("X-Site-Key")
    if not site_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing X-Site-Key header",
        )
    
    from app.models.models import Site
    site = db.query(Site).filter(Site.site_key == site_key, Site.is_active == True).first()
    if not site:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid site key",
        )
    
    return site


def get_widget_request_domain(request: Request, page_url: str | None = None) -> str | None:
    """Extract the best available browser origin for widget domain validation."""
    candidates = [
        request.headers.get("origin"),
        request.headers.get("referer"),
        request.headers.get("x-widget-origin"),
        request.headers.get("x-widget-page"),
        page_url,
    ]

    for candidate in candidates:
        normalized = normalize_domain(candidate)
        if normalized:
            return normalized

    return None


def validate_widget_domain(site, request: Request, page_url: str | None = None) -> None:
    """Ensure the public site key is being used from the registered domain."""
    request_domain = get_widget_request_domain(request, page_url)
    if not domains_match(site.domain, request_domain):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This site key is not authorized for the current domain.",
        )
