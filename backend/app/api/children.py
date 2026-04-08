from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import date

from ..database import get_db
from ..models.child import Child
from ..schemas.child import ChildCreate, ChildUpdate, ChildResponse
from .deps import get_current_user
from ..models.user import User

router = APIRouter(prefix="/api/children", tags=["儿童档案"])


@router.get("/", response_model=List[ChildResponse])
def get_children(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all children for current user"""
    children = db.query(Child).filter(Child.parent_id == current_user.id).all()
    return [ChildResponse.model_validate(c) for c in children]


@router.post("/", response_model=ChildResponse)
def create_child(
    child_data: ChildCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new child profile"""
    child = Child(
        parent_id=current_user.id,
        name=child_data.name,
        gender=child_data.gender,
        birth_date=child_data.birth_date,
        grade=child_data.grade,
        avatar_url=child_data.avatar_url
    )
    db.add(child)
    db.commit()
    db.refresh(child)
    return ChildResponse.model_validate(child)


@router.get("/{child_id}", response_model=ChildResponse)
def get_child(
    child_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific child profile"""
    child = db.query(Child).filter(
        Child.id == child_id,
        Child.parent_id == current_user.id
    ).first()

    if not child:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Child not found"
        )

    return ChildResponse.model_validate(child)


@router.put("/{child_id}", response_model=ChildResponse)
def update_child(
    child_id: int,
    child_data: ChildUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a child profile"""
    child = db.query(Child).filter(
        Child.id == child_id,
        Child.parent_id == current_user.id
    ).first()

    if not child:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Child not found"
        )

    update_data = child_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(child, field, value)

    db.commit()
    db.refresh(child)
    return ChildResponse.model_validate(child)


@router.delete("/{child_id}")
def delete_child(
    child_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a child profile"""
    child = db.query(Child).filter(
        Child.id == child_id,
        Child.parent_id == current_user.id
    ).first()

    if not child:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Child not found"
        )

    db.delete(child)
    db.commit()
    return {"message": "Child deleted successfully"}
