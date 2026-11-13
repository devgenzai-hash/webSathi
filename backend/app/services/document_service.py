import os
import uuid
from typing import List
from sqlalchemy.orm import Session
from fastapi import UploadFile, HTTPException, status

from app.config import settings
from app.models.models import Document, Site
from app.services.rag_service import process_document_for_rag


ALLOWED_FILE_TYPES = {
    "application/pdf": "pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": "docx",
    "text/plain": "txt",
    "text/csv": "csv",
    "image/png": "image",
    "image/jpeg": "image",
    "image/webp": "image",
}

ALLOWED_EXTENSIONS = {".pdf", ".docx", ".txt", ".csv", ".png", ".jpg", ".jpeg", ".webp"}


def validate_file(file: UploadFile) -> str:
    """Validate file type and size. Returns file_type."""
    ext = os.path.splitext(file.filename or "")[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type '{ext}' not supported. Allowed: {', '.join(ALLOWED_EXTENSIONS)}",
        )
    
    content_type = file.content_type or ""
    file_type = ALLOWED_FILE_TYPES.get(content_type)
    if not file_type:
        # Fallback to extension-based detection
        ext_to_type = {
            ".pdf": "pdf", ".docx": "docx", ".txt": "txt",
            ".csv": "csv", ".png": "image", ".jpg": "image",
            ".jpeg": "image", ".webp": "image",
        }
        file_type = ext_to_type.get(ext, "txt")
    
    return file_type


async def upload_document(db: Session, site_id: str, user_id: str, file: UploadFile) -> Document:
    """Upload and process a document for a site."""
    # Verify site belongs to user
    site = db.query(Site).filter(Site.id == site_id, Site.user_id == user_id).first()
    if not site:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Site not found")
    
    file_type = validate_file(file)
    
    # Read file content
    content = await file.read()
    file_size = len(content)
    
    # Check file size
    max_size = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
    if file_size > max_size:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File too large. Maximum size: {settings.MAX_UPLOAD_SIZE_MB}MB",
        )
    
    # Save file to disk
    upload_dir = os.path.join(settings.UPLOAD_DIR, user_id, site_id)
    os.makedirs(upload_dir, exist_ok=True)
    
    file_id = str(uuid.uuid4())
    ext = os.path.splitext(file.filename or "")[1].lower()
    file_path = os.path.join(upload_dir, f"{file_id}{ext}")
    
    with open(file_path, "wb") as f:
        f.write(content)
    
    # Create document record
    document = Document(
        site_id=site_id,
        filename=file.filename or "unknown",
        file_type=file_type,
        file_size=file_size,
        file_path=file_path,
        status="processing",
    )
    db.add(document)
    db.commit()
    db.refresh(document)
    
    # Process document for RAG (extract text, chunk, embed)
    try:
        chunk_count = await process_document_for_rag(
            document_id=document.id,
            site_id=site_id,
            file_path=file_path,
            file_type=file_type,
            content=content,
        )
        document.status = "ready"
        document.chunk_count = chunk_count
    except Exception as e:
        document.status = "failed"
        document.error_message = str(e)
    
    db.commit()
    db.refresh(document)
    return document


def get_site_documents(db: Session, site_id: str, user_id: str) -> List[Document]:
    """Get all documents for a site."""
    site = db.query(Site).filter(Site.id == site_id, Site.user_id == user_id).first()
    if not site:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Site not found")
    
    return db.query(Document).filter(Document.site_id == site_id).all()


def delete_document(db: Session, document_id: str, site_id: str, user_id: str) -> None:
    """Delete a document and its embeddings."""
    site = db.query(Site).filter(Site.id == site_id, Site.user_id == user_id).first()
    if not site:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Site not found")
    
    document = db.query(Document).filter(Document.id == document_id, Document.site_id == site_id).first()
    if not document:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    
    # Delete file from disk
    if os.path.exists(document.file_path):
        os.remove(document.file_path)
    
    # Delete from vector store
    from app.services.rag_service import delete_document_embeddings
    delete_document_embeddings(site_id=site_id, document_id=document_id)
    
    # Delete from DB
    db.delete(document)
    db.commit()
