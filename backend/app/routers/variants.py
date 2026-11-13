"""
A/B prompt variant router — Phase 3.
GET    /sites/{site_id}/variants
POST   /sites/{site_id}/variants
PATCH  /sites/{site_id}/variants/{variant_id}
DELETE /sites/{site_id}/variants/{variant_id}
"""
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.middleware.auth import get_current_user
from app.models.models import PromptVariant, Site, User
from app.schemas.schemas import PromptVariantCreate, PromptVariantResponse, PromptVariantUpdate
from app.services.audit_service import log_action

router = APIRouter(tags=["A/B Variants"])


@router.get("/sites/{site_id}/variants", response_model=List[PromptVariantResponse])
def list_variants(
    site_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    site = db.query(Site).filter(Site.id == site_id, Site.user_id == current_user.id).first()
    if not site:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Site not found")

    variants = db.query(PromptVariant).filter(PromptVariant.site_id == site_id).all()
    return [PromptVariantResponse.model_validate(v) for v in variants]


@router.post("/sites/{site_id}/variants", response_model=PromptVariantResponse, status_code=201)
def create_variant(
    site_id: str,
    payload: PromptVariantCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    site = db.query(Site).filter(Site.id == site_id, Site.user_id == current_user.id).first()
    if not site:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Site not found")

    variant = PromptVariant(
        site_id=site_id,
        name=payload.name,
        system_prompt=payload.system_prompt,
        is_control=payload.is_control,
    )
    db.add(variant)
    db.commit()
    db.refresh(variant)
    log_action(db, "variant.create", user_id=current_user.id, site_id=site_id,
               detail=f"name={payload.name}")
    return PromptVariantResponse.model_validate(variant)


@router.patch("/sites/{site_id}/variants/{variant_id}", response_model=PromptVariantResponse)
def update_variant(
    site_id: str,
    variant_id: str,
    payload: PromptVariantUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    site = db.query(Site).filter(Site.id == site_id, Site.user_id == current_user.id).first()
    if not site:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Site not found")

    variant = db.query(PromptVariant).filter(
        PromptVariant.id == variant_id, PromptVariant.site_id == site_id
    ).first()
    if not variant:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Variant not found")

    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(variant, key, value)
    db.commit()
    db.refresh(variant)
    return PromptVariantResponse.model_validate(variant)


@router.delete("/sites/{site_id}/variants/{variant_id}", status_code=204)
def delete_variant(
    site_id: str,
    variant_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    site = db.query(Site).filter(Site.id == site_id, Site.user_id == current_user.id).first()
    if not site:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Site not found")

    variant = db.query(PromptVariant).filter(
        PromptVariant.id == variant_id, PromptVariant.site_id == site_id
    ).first()
    if not variant:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Variant not found")

    db.delete(variant)
    db.commit()
    log_action(db, "variant.delete", user_id=current_user.id, site_id=site_id)
