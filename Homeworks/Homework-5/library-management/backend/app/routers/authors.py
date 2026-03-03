from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from ..database import get_db
from .. import models, schemas

router = APIRouter(prefix="/authors", tags=["Authors"])


@router.post("", response_model=schemas.AuthorOut, status_code=status.HTTP_201_CREATED)
def create_author(payload: schemas.AuthorCreate, db: Session = Depends(get_db)):
    author = models.Author(**payload.model_dump())
    db.add(author)
    try:
        db.commit()
        db.refresh(author)
        return author
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Author email must be unique.")


@router.get("", response_model=list[schemas.AuthorOut])
def list_authors(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
):
    return db.query(models.Author).offset(skip).limit(limit).all()


@router.get("/{author_id}", response_model=schemas.AuthorOut)
def get_author(author_id: int, db: Session = Depends(get_db)):
    author = db.query(models.Author).filter(models.Author.id == author_id).first()
    if not author:
        raise HTTPException(status_code=404, detail="Author not found.")
    return author


@router.put("/{author_id}", response_model=schemas.AuthorOut)
def update_author(author_id: int, payload: schemas.AuthorUpdate, db: Session = Depends(get_db)):
    author = db.query(models.Author).filter(models.Author.id == author_id).first()
    if not author:
        raise HTTPException(status_code=404, detail="Author not found.")

    data = payload.model_dump(exclude_unset=True)
    for k, v in data.items():
        setattr(author, k, v)

    try:
        db.commit()
        db.refresh(author)
        return author
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Author email must be unique.")


@router.delete("/{author_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_author(author_id: int, db: Session = Depends(get_db)):
    author = db.query(models.Author).filter(models.Author.id == author_id).first()
    if not author:
        raise HTTPException(status_code=404, detail="Author not found.")

    book_count = db.query(models.Book).filter(models.Book.author_id == author_id).count()
    if book_count > 0:
        raise HTTPException(status_code=409, detail="Cannot delete author with associated books.")

    db.delete(author)
    db.commit()
    return
