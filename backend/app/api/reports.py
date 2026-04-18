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
    """Get all reports for user's children, with game_type attached"""
    from ..models.screening import Screening
    import json as _json

    query = db.query(Report).join(Child).filter(Child.parent_id == current_user.id)
    if child_id:
        query = query.filter(Report.child_id == child_id)

    reports = query.order_by(Report.created_at.desc()).all()

    # 批量查询关联的 Screening，避免 N+1
    screening_ids = [r.screening_id for r in reports if r.screening_id]
    screenings = {
        s.id: s for s in db.query(Screening).filter(Screening.id.in_(screening_ids)).all()
    } if screening_ids else {}

    results = []
    for r in reports:
        item = ReportResponse.model_validate(r)
        sc = screenings.get(r.screening_id)
        if sc:
            item.game_type = sc.game_type
        results.append(item)
    return results


@router.get("/by-screening/{screening_id}", response_model=ReportResponse)
def get_report_by_screening(
    screening_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get report by screening_id"""
    report = db.query(Report).join(Child).filter(
        Report.screening_id == screening_id,
        Child.parent_id == current_user.id
    ).first()

    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    return ReportResponse.model_validate(report)


@router.get("/{report_id}", response_model=ReportResponse)
def get_report(
    report_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific report"""
    from ..models.screening import Screening
    report = db.query(Report).join(Child).filter(
        Report.id == report_id,
        Child.parent_id == current_user.id
    ).first()

    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    # 附加 game_type（来自关联的 Screening）
    result = ReportResponse.model_validate(report)
    if report.screening_id:
        screening = db.query(Screening).filter(Screening.id == report.screening_id).first()
        if screening:
            result.game_type = screening.game_type
    return result


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
    try:
        dimensions = json.loads(report.dimensions) if report.dimensions else {}
    except (json.JSONDecodeError, TypeError):
        dimensions = {}

    return {
        "report_id": report.id,
        "dimensions": dimensions,
        "overall_score": report.overall_score,
        "risk_level": report.risk_level
    }


@router.get("/child/{child_id}/merged-dimensions")
def get_merged_dimensions(
    child_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    合并该孩子所有筛查报告的维度得分。
    每个维度取最新一次筛查的得分，返回完整的多维度能力图谱。
    """
    import json

    # 验证孩子归属
    child = db.query(Child).filter(
        Child.id == child_id,
        Child.parent_id == current_user.id
    ).first()
    if not child:
        raise HTTPException(status_code=404, detail="孩子档案不存在")

    # 按时间升序取所有报告（后面的会覆盖前面的，保证取最新值）
    reports = db.query(Report).filter(
        Report.child_id == child_id
    ).order_by(Report.created_at.asc()).all()

    merged: dict = {}
    game_type_map: dict = {}  # dim -> game_type，用于标注来源

    from ..models.screening import Screening
    for report in reports:
        if not report.dimensions:
            continue
        try:
            dims = json.loads(report.dimensions)
        except (json.JSONDecodeError, TypeError):
            continue
        # 获取该报告对应的 game_type
        game_type = None
        if report.screening_id:
            sc = db.query(Screening).filter(Screening.id == report.screening_id).first()
            if sc:
                game_type = sc.game_type
        for dim, score in dims.items():
            if isinstance(score, (int, float)):
                merged[dim] = int(score)
                if game_type:
                    game_type_map[dim] = game_type

    # 统计已完成的游戏类型
    from ..models.screening import Screening as SC
    completed_game_types = [
        row[0] for row in db.query(SC.game_type).filter(
            SC.child_id == child_id,
            SC.completed_at.isnot(None)
        ).distinct().all()
    ]

    all_game_types = ["visual", "spelling", "comprehension", "working_memory", "rapid_naming", "motor_coordination"]
    pending_game_types = [g for g in all_game_types if g not in completed_game_types]

    return {
        "child_id": child_id,
        "child_name": child.name,
        "merged_dimensions": merged,
        "dimension_sources": game_type_map,
        "completed_game_types": completed_game_types,
        "pending_game_types": pending_game_types,
        "is_complete": len(pending_game_types) == 0,
    }
