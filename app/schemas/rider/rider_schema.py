# -*- coding: utf-8 -*-

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, EmailStr, validator, confloat, conint
from enum import Enum
from app.schemas import BaseSchema

class RiderAssignmentStatus(str, Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    CANCELED = "canceled"

class VehicleType(str, Enum):
    BIKE = "bike"
    MOTORCYCLE = "motorcycle"
    CAR = "car"
    SCOOTER = "scooter"


class RiderSchema(BaseSchema):
    name: str = Field(..., max_length=50)
    phone: str = Field(..., max_length=20, regex=r'^\+?[0-9\s\-]+$')
    email: EmailStr = Field(..., max_length=100)
    avatar: Optional[str] = Field(None, max_length=200)
    vehicle_type: Optional[VehicleType] = None
    license_plate: Optional[str] = Field(None, max_length=20, example="京A12345")
    delivery_radius: Optional[int] = Field(None, gt=0, description="最大配送距离(米)", example=5000)
    is_available: bool = True
    is_online: bool = True

    @validator('license_plate')
    def validate_plate(cls, v):
        if v and len(v.strip()) < 2:
            raise ValueError("车牌号过短")
        return v


class RiderLocationSchema(BaseSchema):
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    accuracy: Optional[float] = Field(None, gt=0)
    speed: Optional[float] = Field(None, ge=0)


class RiderAssignmentBase(BaseSchema):
        status: RiderAssignmentStatus = RiderAssignmentStatus.PENDING
        note: Optional[str] = Field(None, max_length=500, description="状态变更备注")



