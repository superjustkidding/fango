from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import constr, Field, EmailStr, validator

from app.schemas import BaseSchema

class UserCouponStatus(str, Enum):
    UNUSED = "unused"
    USED = "used"
    EXPIRED = "expired"

class AddressLabel(str, Enum):
    HOME = "home"
    WORK = "work"
    OTHER = "other"



class UserBase(BaseSchema):
        username: constr(min_length=3, max_length=50) = Field(
            ...,
            regex=r'^[a-zA-Z0-9_]+$',
            example="john_doe",
            description="用户名(只允许字母数字和下划线)"
        )
        email: EmailStr = Field(..., example="user@example.com")
        phone: constr(min_length=10, max_length=20) = Field(
            ...,
            regex=r'^\+?[0-9\s\-]+$',
            example="+8613812345678"
        )
        avatar: Optional[str] = Field(
            None,
            max_length=200,
            example="https://example.com/avatar.jpg"
        )
        is_admin: bool = Field(False, description="是否管理员")

        @validator('username')
        def username_not_email(cls, v):
            if '@' in v:
                raise ValueError("用户名不能包含@符号")
            return v


class UserAddressBase(BaseSchema):
    label: Optional[AddressLabel] = Field(
        None,
        example="home",
        description="地址标签: home/work/other"
    )
    recipient: constr(min_length=2, max_length=50) = Field(
        ...,
        example="张三",
        description="收件人姓名"
    )
    phone: constr(min_length=10, max_length=20) = Field(
        ...,
        regex=r'^\+?[0-9\s\-]+$',
        example="13800138000"
    )
    address: constr(max_length=200) = Field(
        ...,
        example="北京市朝阳区建国路88号"
    )
    details: Optional[constr(max_length=200)] = Field(
        None,
        example="SOHO现代城A座1001室"
    )
    is_default: bool = Field(False, description="是否默认地址")

    @validator('phone')
    def validate_phone(cls, v):
        if not any(c.isdigit() for c in v):
            raise ValueError("必须包含数字")
        return v


class UserCouponBase(BaseSchema):
    status: UserCouponStatus = UserCouponStatus.UNUSED
    used_at: Optional[datetime] = None