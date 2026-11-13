from typing import List
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.schemas import SiteCreate, SiteUpdate, SiteResponse
from app.middleware.auth import get_current_user
from app.models.models import User, Site
from app.services.domain_service import normalize_domain
from app.services.audit_service import log_action

router = APIRouter(prefix="/sites", tags=["Sites"])


@router.post("/", response_model=SiteResponse, status_code=201)
def create_site(
    request: Request,
    payload: SiteCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    normalized_domain = normalize_domain(payload.domain)
    if not normalized_domain:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Enter a valid domain or base URL.",
        )

    existing_count = db.query(Site).filter(Site.user_id == current_user.id).count()
    plan_limits = {"free": 2, "starter": 5, "pro": 20, "enterprise": 100}
    limit = plan_limits.get(current_user.plan, 2)
    if existing_count >= limit:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Site limit reached for your plan ({limit} sites). Please upgrade.",
        )

    site = Site(user_id=current_user.id, site_name=payload.site_name, domain=normalized_domain)
    db.add(site)
    db.commit()
    db.refresh(site)
    log_action(db, "site.create", user_id=current_user.id, site_id=site.id,
               detail=payload.site_name,
               ip_address=request.client.host if request.client else None)
    return SiteResponse.model_validate(site)


@router.get("/", response_model=List[SiteResponse])
def list_sites(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """List all sites for the current user."""
    sites = db.query(Site).filter(Site.user_id == current_user.id).all()
    return [SiteResponse.model_validate(s) for s in sites]


@router.get("/{site_id}", response_model=SiteResponse)
def get_site(site_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Get a specific site."""
    site = db.query(Site).filter(Site.id == site_id, Site.user_id == current_user.id).first()
    if not site:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Site not found")
    return SiteResponse.model_validate(site)


@router.patch("/{site_id}", response_model=SiteResponse)
def update_site(
    site_id: str,
    request: Request,
    payload: SiteUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    site = db.query(Site).filter(Site.id == site_id, Site.user_id == current_user.id).first()
    if not site:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Site not found")

    update_data = payload.model_dump(exclude_unset=True)
    if "domain" in update_data:
        normalized_domain = normalize_domain(update_data["domain"])
        if not normalized_domain:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Enter a valid domain or base URL.",
            )
        update_data["domain"] = normalized_domain

    for key, value in update_data.items():
        setattr(site, key, value)

    db.commit()
    db.refresh(site)
    log_action(db, "site.update", user_id=current_user.id, site_id=site_id,
               detail=str(list(update_data.keys())),
               ip_address=request.client.host if request.client else None)
    return SiteResponse.model_validate(site)


@router.delete("/{site_id}", status_code=204)
def delete_site(
    site_id: str,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    site = db.query(Site).filter(Site.id == site_id, Site.user_id == current_user.id).first()
    if not site:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Site not found")
    log_action(db, "site.delete", user_id=current_user.id, site_id=site_id,
               ip_address=request.client.host if request.client else None)
    db.delete(site)
    db.commit()


@router.post("/{site_id}/verify")
def verify_site(site_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Mark site as verified (simplified for MVP - in production, verify DNS/meta tag)."""
    site = db.query(Site).filter(Site.id == site_id, Site.user_id == current_user.id).first()
    if not site:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Site not found")
    
    site.is_verified = True
    db.commit()
    return {"message": "Site verified successfully", "site_key": site.site_key}
