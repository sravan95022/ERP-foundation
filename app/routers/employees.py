from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.models.employee import Employee, Attendance, LeaveRequest, PerformanceReview, LeaveStatus
from app.schemas.employee import (
    EmployeeCreate, EmployeeOut, AttendanceMark, AttendanceOut,
    LeaveCreate, LeaveOut, PerformanceReviewCreate, PerformanceReviewOut,
)

router = APIRouter(prefix="/api/v1/employees", tags=["Employee Management"])


@router.post("/", response_model=EmployeeOut, status_code=201)
def create_employee(payload: EmployeeCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    if db.query(Employee).filter(Employee.employee_code == payload.employee_code).first():
        raise HTTPException(status_code=400, detail="Employee code already exists")
    emp = Employee(tenant_id=user.tenant_id, **payload.model_dump())
    db.add(emp); db.commit(); db.refresh(emp)
    return emp


@router.get("/", response_model=List[EmployeeOut])
def list_employees(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return db.query(Employee).filter(Employee.tenant_id == user.tenant_id).all()


@router.post("/attendance", response_model=AttendanceOut)
def mark_attendance(payload: AttendanceMark, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    record = Attendance(tenant_id=user.tenant_id, **payload.model_dump())
    db.add(record); db.commit(); db.refresh(record)
    return record


@router.get("/attendance/{employee_id}", response_model=List[AttendanceOut])
def get_attendance(employee_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return db.query(Attendance).filter(Attendance.employee_id == employee_id, Attendance.tenant_id == user.tenant_id).all()


@router.post("/leave", response_model=LeaveOut, status_code=201)
def request_leave(payload: LeaveCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    leave = LeaveRequest(tenant_id=user.tenant_id, **payload.model_dump())
    db.add(leave); db.commit(); db.refresh(leave)
    return leave


@router.post("/leave/{leave_id}/approve", response_model=LeaveOut)
def approve_leave(leave_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    leave = db.query(LeaveRequest).filter(LeaveRequest.id == leave_id, LeaveRequest.tenant_id == user.tenant_id).first()
    if not leave:
        raise HTTPException(status_code=404, detail="Leave request not found")
    leave.status = LeaveStatus.APPROVED
    db.commit(); db.refresh(leave)
    return leave


@router.post("/performance-reviews", response_model=PerformanceReviewOut, status_code=201)
def add_review(payload: PerformanceReviewCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    review = PerformanceReview(tenant_id=user.tenant_id, **payload.model_dump())
    db.add(review); db.commit(); db.refresh(review)
    return review
