from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from datetime import datetime, date
from typing import Optional
from decimal import Decimal
import calendar
import io
from ..database import SessionLocal
from ..models.user import User
from ..models.record import Record
from ..schemas.record import RecordCreate, RecordUpdate, RecordResponse, SummaryResponse
from ..deps import get_current_user
from ..services.excel_service import (
    build_import_template, parse_import_excel,
    export_to_excel, export_to_csv,
)

router = APIRouter()


def _get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def _build_filter(query, user_id: int, month: str = "", type_filter: str = "", keyword: str = ""):
    query = query.filter(Record.user_id == user_id)
    if month:
        # 计算下个月的第一天作为截止日期
        year, mon = map(int, month.split("-"))
        if mon == 12:
            next_month = f"{year + 1}-01-01"
        else:
            next_month = f"{year}-{mon + 1:02d}-01"
        
        query = query.filter(
            Record.record_date >= f"{month}-01",
            Record.record_date < next_month,
        )
    if type_filter:
        query = query.filter(Record.type == type_filter)
    if keyword:
        kw = f"%{keyword}%"
        query = query.filter(
            (Record.category.like(kw)) |
            (Record.account.like(kw)) |
            (Record.note.like(kw))
        )
    return query


@router.get("", response_model=dict)
def list_records(
    month: str = "",
    type: str = "",
    keyword: str = "",
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(_get_db),
):
    query = db.query(Record)
    query = _build_filter(query, current_user.id, month, type, keyword)
    total = query.count()
    items = query.order_by(Record.record_date.desc(), Record.id.desc()) \
        .offset((page - 1) * page_size).limit(page_size).all()
    return {
        "items": [RecordResponse.model_validate(r).model_dump() for r in items],
        "total": total,
        "page": page,
        "page_size": page_size,
    }


@router.post("", response_model=RecordResponse, status_code=201)
def create_record(
    data: RecordCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(_get_db),
):
    record = Record(
        user_id=current_user.id,
        **data.model_dump(),
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


@router.put("/{record_id}", response_model=RecordResponse)
def update_record(
    record_id: int,
    data: RecordUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(_get_db),
):
    record = db.query(Record).filter(
        Record.id == record_id, Record.user_id == current_user.id
    ).first()
    if not record:
        raise HTTPException(status_code=404, detail="记录不存在")
    for key, value in data.model_dump().items():
        setattr(record, key, value)
    record.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(record)
    return record


@router.delete("/{record_id}")
def delete_record(
    record_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(_get_db),
):
    record = db.query(Record).filter(
        Record.id == record_id, Record.user_id == current_user.id
    ).first()
    if not record:
        raise HTTPException(status_code=404, detail="记录不存在")
    db.delete(record)
    db.commit()
    return {"ok": True}


@router.delete("")
def clear_all_records(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(_get_db),
):
    count = db.query(Record).filter(Record.user_id == current_user.id).delete()
    db.commit()
    return {"ok": True, "deleted_count": count}


@router.get("/summary", response_model=SummaryResponse)
def get_summary(
    month: str = "",
    type: str = "",
    keyword: str = "",
    current_user: User = Depends(get_current_user),
    db: Session = Depends(_get_db),
):
    query = db.query(Record)
    query = _build_filter(query, current_user.id, month, type, keyword)

    income = Decimal("0")
    expense = Decimal("0")
    cat_map: dict[str, Decimal] = {}

    for r in query.all():
        if r.type == "income":
            income += r.amount
        else:
            expense += r.amount
        cat_key = f"{r.type}:{r.category}"
        cat_map[cat_key] = cat_map.get(cat_key, Decimal("0")) + r.amount

    categories = [
        {"type": k.split(":")[0], "category": k.split(":")[1], "total": float(v)}
        for k, v in sorted(cat_map.items(), key=lambda x: -x[1])
    ]

    return SummaryResponse(
        income=float(income),
        expense=float(expense),
        balance=float(income - expense),
        categories=categories,
    )


@router.get("/stats")
def get_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(_get_db),
):
    from sqlalchemy import func

    monthly = db.query(
        func.to_char(Record.record_date, "YYYY-MM").label("month"),
        Record.type,
        func.sum(Record.amount).label("total"),
    ).filter(Record.user_id == current_user.id) \
     .group_by("month", Record.type) \
     .order_by("month") \
     .all()

    monthly_trend: dict[str, dict] = {}
    for row in monthly:
        m = row.month
        if m not in monthly_trend:
            monthly_trend[m] = {"month": m, "income": 0, "expense": 0}
        monthly_trend[m][row.type] = float(row.total)

    cat_pie = db.query(
        Record.type,
        Record.category,
        func.sum(Record.amount).label("total"),
    ).filter(Record.user_id == current_user.id) \
     .group_by(Record.type, Record.category) \
     .order_by(func.sum(Record.amount).desc()) \
     .limit(20) \
     .all()

    return {
        "monthly_trend": list(monthly_trend.values()),
        "category_pie": [
            {"type": r.type, "category": r.category, "total": float(r.total)}
            for r in cat_pie
        ],
        "top_categories": [
            {"type": r.type, "category": r.category, "total": float(r.total)}
            for r in cat_pie[:10]
        ],
    }


@router.get("/import-template")
def download_template(current_user: User = Depends(get_current_user)):
    content = build_import_template()
    return StreamingResponse(
        io.BytesIO(content),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=import_template.xlsx"},
    )


@router.post("/import")
async def import_records(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(_get_db),
):
    if not file.filename or not file.filename.endswith((".xlsx", ".xls")):
        raise HTTPException(status_code=400, detail="请上传 xlsx 格式的 Excel 文件")
    content = await file.read()
    try:
        records, errors = parse_import_excel(content)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"文件解析失败：{str(e)}")

    success_count = 0
    for rec_data in records:
        try:
            record = Record(user_id=current_user.id, **rec_data)
            db.add(record)
            success_count += 1
        except Exception as e:
            errors.append(f"导入失败：{str(e)}")
    db.commit()
    return {"success": success_count, "errors": errors, "total": len(records)}


@router.get("/export")
def export_records(
    format: str = Query("xlsx", pattern="^(xlsx|csv)$"),
    month: str = "",
    type: str = "",
    keyword: str = "",
    current_user: User = Depends(get_current_user),
    db: Session = Depends(_get_db),
):
    query = db.query(Record)
    query = _build_filter(query, current_user.id, month, type, keyword)
    records = query.order_by(Record.record_date.desc(), Record.id.desc()).all()
    record_dicts = [RecordResponse.model_validate(r).model_dump() for r in records]

    if format == "xlsx":
        content = export_to_excel(record_dicts)
        return StreamingResponse(
            io.BytesIO(content),
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": "attachment; filename=records.xlsx"},
        )
    else:
        csv_content = export_to_csv(record_dicts)
        return StreamingResponse(
            io.BytesIO(("\ufeff" + csv_content).encode("utf-8-sig")),
            media_type="text/csv; charset=utf-8",
            headers={"Content-Disposition": "attachment; filename=records.csv"},
        )
