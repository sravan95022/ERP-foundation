from pydantic import BaseModel
from typing import Optional
from datetime import date, datetime
from decimal import Decimal
from app.models.employee import LeaveStatus


class EmployeeCreate(BaseModel):
    employee_code: str
    full_name: str
    designation: Optional[str] = None
    date_of_joining: Optional[date] = None
    salary: Optional[Decimal] = None
    branch_id: Optional[int] = None
    department_id: Optional[int] = None
    user_id: Optional[int] = None


class EmployeeOut(BaseModel):
    id: int
    employee_code: str
    full_name: str
    designation: Optional[str] = None
    is_active: int
    class Config:
        from_attributes = True


class AttendanceMark(BaseModel):
    employee_id: int
    date: date
    status: str = "present"


class AttendanceOut(BaseModel):
    id: int
    employee_id: int
    date: date
    status: str
    class Config:
        from_attributes = True


class LeaveCreate(BaseModel):
    employee_id: int
    start_date: date
    end_date: date
    reason: Optional[str] = None


class LeaveOut(BaseModel):
    id: int
    employee_id: int
    start_date: date
    end_date: date
    status: LeaveStatus
    class Config:
        from_attributes = True


class PerformanceReviewCreate(BaseModel):
    employee_id: int
    review_period: str
    rating: Optional[Decimal] = None
    comments: Optional[str] = None


class PerformanceReviewOut(BaseModel):
    id: int
    employee_id: int
    review_period: str
    rating: Optional[Decimal] = None
    created_at: datetime
    class Config:
        from_attributes = True
