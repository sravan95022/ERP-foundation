import os
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.models.document import Document

router = APIRouter(prefix="/api/v1/documents", tags=["Document Management"])

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    entity_type: Optional[str] = None,
    entity_id: Optional[int] = None,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    # Access control: tenant-scoped storage path (Phase 23 access control requirement)
    tenant_dir = os.path.join(UPLOAD_DIR, str(user.tenant_id))
    os.makedirs(tenant_dir, exist_ok=True)

    # Versioning: if a document with this filename+entity already exists, increment version
    existing = db.query(Document).filter(
        Document.tenant_id == user.tenant_id, Document.filename == file.filename,
        Document.entity_type == entity_type, Document.entity_id == entity_id,
    ).order_by(Document.version.desc()).first()
    version = (existing.version + 1) if existing else 1

    stored_name = f"{version}_{file.filename}"
    path = os.path.join(tenant_dir, stored_name)
    content = await file.read()
    with open(path, "wb") as f:
        f.write(content)

    doc = Document(
        tenant_id=user.tenant_id, uploaded_by=user.id, filename=file.filename,
        file_path=path, version=version, entity_type=entity_type, entity_id=entity_id,
    )
    db.add(doc); db.commit(); db.refresh(doc)
    return {"id": doc.id, "filename": doc.filename, "version": doc.version, "size_bytes": len(content)}


@router.get("/")
def list_documents(entity_type: Optional[str] = None, entity_id: Optional[int] = None, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    q = db.query(Document).filter(Document.tenant_id == user.tenant_id)
    if entity_type:
        q = q.filter(Document.entity_type == entity_type)
    if entity_id:
        q = q.filter(Document.entity_id == entity_id)
    return [{"id": d.id, "filename": d.filename, "version": d.version, "created_at": d.created_at} for d in q.all()]
