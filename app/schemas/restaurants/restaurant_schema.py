from datetime import time, datetime,date
from enum import Enum
from typing import Optional, Dict, Any

from pydantic import Field, EmailStr, confloat, validator

from app.schemas import BaseSchema

class DayOfWeek(int, Enum):
    SUNDAY = 0
    MONDAY = 1
    TUESDAY = 2
    WEDNESDAY = 3
    THURSDAY = 4
    FRIDAY = 5
    SATURDAY = 6

class RestaurantBase(BaseSchema):
    name: str = Field(..., max_length=100)
    email: EmailStr = Field(..., max_length=100)
    description: Optional[str] = None
    address: str = Field(..., max_length=200)
    phone: str = Field(..., max_length=20, regex=r'^\+?[0-9\s\-]+$')
    logo: Optional[str] = Field(None, max_length=200)
    banner: Optional[str] = Field(None, max_length=200)
    rating: confloat(ge=0, le=5) = 0.0
    is_active: bool = True
    is_online: bool = True


class MenuCategoryBase(BaseSchema):
    name: str = Field(..., max_length=50)
    description: Optional[str] = None
    display_order: int = 0


class MenuItemBase(BaseSchema):
    name: str = Field(..., max_length=100)
    description: Optional[str] = None
    price: confloat(gt=0)
    image: Optional[str] = Field(None, max_length=200)
    preparation_time: Optional[int] = Field(None, gt=0)
    is_available: bool = True
    is_featured: bool = False


class MenuOptionGroupBase(BaseSchema):
    name: str = Field(..., max_length=50)
    is_required: bool = False
    min_selections: int = Field(1, ge=1)
    max_selections: int = Field(1, ge=1)

    @validator('max_selections')
    def validate_max_selections(cls, v, values):
        if 'min_selections' in values and v < values['min_selections']:
            raise ValueError('max_selections must be >= min_selections')
        return v


class DeliveryZoneBase(BaseSchema):
    name: str = Field(..., max_length=50)
    delivery_fee: confloat(ge=0) = 0.0
    min_order_amount: confloat(ge=0) = 0.0
    delivery_time: Optional[int] = Field(None, gt=0)


class OperatingHoursBase(BaseSchema):
    day_of_week: DayOfWeek
    open_time: time
    close_time: time
    is_closed: bool = False

    @validator('close_time')
    def validate_times(cls, v, values):
        if 'open_time' in values and not values['is_closed']:
            if v <= values['open_time']:
                raise ValueError('close_time must be after open_time')
        return v


class PromotionBase(BaseSchema):
    title: str = Field(..., max_length=100)
    description: Optional[str] = None
    image: Optional[str] = Field(None, max_length=200)
    start_date: datetime
    end_date: datetime
    is_active: bool = True

    @validator('end_date')
    def validate_dates(cls, v, values):
        if 'start_date' in values and v <= values['start_date']:
            raise ValueError('end_date must be after start_date')
        return v


class RestaurantStatisticsBase(BaseSchema):
    date: date
    total_orders: int = 0
    completed_orders: int = 0
    canceled_orders: int = 0
    total_revenue: confloat(ge=0) = 0.0
    average_rating: confloat(ge=0, le=5) = 0.0
    popular_items: Optional[Dict[str, Any]] = None  # 热门菜品JSON