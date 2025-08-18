from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field
from enum import Enum


class DeletedStatus(str, Enum):
    ACTIVE = "active"
    DELETED = "deleted"

class BaseSchema(BaseModel):
    """基础 Pydantic 模型 (对应 SQLAlchemy 的 BaseModel)"""
    class Config:
        orm_mode = True
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }
        arbitrary_types_allowed = True

    # 基础字段
    id: Optional[int] = Field(None, description="主键ID")
    created_at: Optional[datetime] = Field(None, description="创建时间")
    updated_at: Optional[datetime] = Field(None, description="更新时间")
    deleted_at: Optional[datetime] = Field(None, description="删除时间")
    deleted_status: Optional[DeletedStatus] = Field(DeletedStatus.ACTIVE, description="软删除状态")

    # 对应 SQLAlchemy 的 save() 方法
    @classmethod
    def validate_from_orm(cls, db_obj):
        """从 ORM 对象加载并验证数据"""
        return cls.from_orm(db_obj)

    # 对应 SQLAlchemy 的 delete() 方法
    class DeleteRequest(BaseModel):
        hard_delete: bool = Field(False, description="是否硬删除")