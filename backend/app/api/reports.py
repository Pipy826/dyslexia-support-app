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


@router.get("/{report_id}/export-text")
def export_report_text(
    report_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    导出报告为纯文字格式（服务端生成，前端直接展示或下载）。
    返回 JSON { content: "..." }，前端可复制到剪贴板或写入文件。
    """
    import json as _json
    from ..models.screening import Screening

    report = db.query(Report).join(Child).filter(
        Report.id == report_id,
        Child.parent_id == current_user.id
    ).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    child = db.query(Child).filter(Child.id == report.child_id).first()
    child_name = child.name if child else "未知"

    # 获取 game_type
    game_type = "综合"
    game_type_names = {
        "visual": "视觉辨识", "spelling": "拼字识别", "comprehension": "文字理解",
        "working_memory": "工作记忆", "rapid_naming": "快速命名", "motor_coordination": "精细动作",
    }
    if report.screening_id:
        sc = db.query(Screening).filter(Screening.id == report.screening_id).first()
        if sc:
            game_type = game_type_names.get(sc.game_type, sc.game_type)

    risk_labels = {"low": "低风险", "medium": "中风险", "high": "高风险"}
    dim_names = {
        "visual_discrimination": "视觉辨识能力", "phonological": "音形映射能力",
        "character_order": "字序组织能力", "spelling": "拼写输出能力",
        "reading_comprehension": "阅读理解能力", "semantic_integration": "语义整合能力",
        "information_extraction": "信息提取能力", "attention": "任务注意力",
        "working_memory_capacity": "工作记忆容量", "short_term_memory": "短时记忆能力",
        "rapid_naming_speed": "快速命名速度", "phonological_awareness": "音韵意识",
        "fine_motor_control": "精细动作控制", "visual_motor_integration": "视动整合能力",
    }

    try:
        dimensions = _json.loads(report.dimensions) if report.dimensions else {}
    except Exception:
        dimensions = {}

    created_str = report.created_at.strftime("%Y-%m-%d") if report.created_at else ""

    lines = [
        "═══════════════════════════════",
        "  悦读小灯塔 · 筛查评估报告",
        "═══════════════════════════════",
        f"孩子姓名：{child_name}",
        f"游戏类型：{game_type}",
        f"评估日期：{created_str}",
        f"综合得分：{report.overall_score} 分",
        f"风险等级：{risk_labels.get(report.risk_level, report.risk_level)}",
        "───────────────────────────────",
        "【评估总结】",
        report.summary or "暂无",
        "───────────────────────────────",
        "【各维度得分】",
    ]
    if dimensions:
        for dim, score in dimensions.items():
            bar = "█" * round(score / 10) + "░" * (10 - round(score / 10))
            name = dim_names.get(dim, dim).ljust(10)
            lines.append(f"{name}  {bar}  {score}分")
    else:
        lines.append("暂无维度数据")
    lines += [
        "───────────────────────────────",
        "【干预建议】",
        report.recommendations or "暂无",
        "───────────────────────────────",
        "⚠️ 本报告仅供参考，不构成医学诊断",
        "═══════════════════════════════",
    ]

    return {"content": "\n".join(lines), "child_name": child_name, "created_at": created_str}
