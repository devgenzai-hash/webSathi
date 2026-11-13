from typing import List
from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.schemas import DocumentResponse
from app.middleware.auth import get_current_user
from app.services.document_service import upload_document, get_site_documents, delete_document
from app.models.models import User

router = APIRouter(prefix="/sites/{site_id}/documents", tags=["Documents"])


@router.post("/", response_model=DocumentResponse, status_code=201)
async def upload_doc(
    site_id: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Upload a document (PDF, DOCX, TXT, CSV, Image) for RAG processing."""
    document = await upload_document(db, site_id=site_id, user_id=current_user.id, file=file)
    return DocumentResponse.model_validate(document)


@router.get("/", response_model=List[DocumentResponse])
def list_documents(
    site_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List all documents for a site."""
    documents = get_site_documents(db, site_id=site_id, user_id=current_user.id)
    return [DocumentResponse.model_validate(d) for d in documents]


@router.delete("/{document_id}", status_code=204)
def remove_document(
    site_id: str,
    document_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a document and its embeddings."""
    delete_document(db, document_id=document_id, site_id=site_id, user_id=current_user.id)
