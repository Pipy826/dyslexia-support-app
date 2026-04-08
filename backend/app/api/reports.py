from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, date

from ..database import get_db
from ..models.screening import Report
from ..models.child import Child
from ..schemas.report import ReportResponse
from .deps import get_current_user
from ..models.user import User

router = APIRouter(prefix="/api/reports", tags=["报告"])


@router.get("/", response_model=List[ReportResponse])
def get_reports(
    child_id: int = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all reports for user's children"""
    query = db.query(Report).join(Child).filter(Child.parent_id == current_user.id)

    if child_id:
        query = query.filter(Report.child_id == child_id)

    reports = query.order_by(Report.created_at.desc()).all()
    return [ReportResponse.model_validate(r) for r in reports]


@router.get("/{report_id}", response_model=ReportResponse)
def get_report(
    report_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific report"""
    report = db.query(Report).join(Child).filter(
        Report.id == report_id,
        Child.parent_id == current_user.id
    ).first()

    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    return ReportResponse.model_validate(report)


@router.get("/{report_id}/dimensions")
def get_report_dimensions(
    report_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get detailed dimension scores for a report"""
    report = db.query(Report).join(Child).filter(
        Report.id == report_id,
        Child.parent_id == current_user.id
    ).first()

    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    import json
    dimensions = json.loads(report.dimensions) if report.dimensions else {}

    return {
        "report_id": report.id,
        "dimensions": dimensions,
        "overall_score": report.overall_score,
        "risk_level": report.risk_level
    }
