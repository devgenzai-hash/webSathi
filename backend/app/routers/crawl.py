"""
Web crawler router — Phase 1.
POST /sites/{site_id}/crawl        start a new crawl job
GET  /sites/{site_id}/crawl        list crawl jobs
GET  /sites/{site_id}/crawl/{job}  check one job
"""
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.middleware.auth import get_current_user
from app.models.models import CrawlJob, Site, User
from app.schemas.schemas import CrawlJobResponse, CrawlRequest
from app.services.crawler_service import start_crawl
from app.services.audit_service import log_action

router = APIRouter(tags=["Crawler"])


@router.post("/sites/{site_id}/crawl", response_model=CrawlJobResponse, status_code=202)
async def create_crawl_job(
    site_id: str,
    payload: CrawlRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    site = db.query(Site).filter(Site.id == site_id, Site.user_id == current_user.id).first()
    if not site:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Site not found")

    job = CrawlJob(site_id=site_id, root_url=payload.url)
    db.add(job)
    db.commit()
    db.refresh(job)

    background_tasks.add_task(start_crawl, db, job.id, payload.url, site_id)

    log_action(db, "crawl.start", user_id=current_user.id, site_id=site_id,
               detail=f"url={payload.url}")
    return CrawlJobResponse.model_validate(job)


@router.get("/sites/{site_id}/crawl", response_model=List[CrawlJobResponse])
def list_crawl_jobs(
    site_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    site = db.query(Site).filter(Site.id == site_id, Site.user_id == current_user.id).first()
    if not site:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Site not found")

    jobs = (
        db.query(CrawlJob)
        .filter(CrawlJob.site_id == site_id)
        .order_by(CrawlJob.created_at.desc())
        .limit(20)
        .all()
    )
    return [CrawlJobResponse.model_validate(j) for j in jobs]


@router.get("/sites/{site_id}/crawl/{job_id}", response_model=CrawlJobResponse)
def get_crawl_job(
    site_id: str,
    job_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    job = db.query(CrawlJob).filter(CrawlJob.id == job_id, CrawlJob.site_id == site_id).first()
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Crawl job not found")
    return CrawlJobResponse.model_validate(job)
