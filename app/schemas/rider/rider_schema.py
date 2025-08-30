# -*- coding: utf-8 -*-
from flask_marshmallow import Schema
from marshmallow import fields, validate, validates, ValidationError


class RiderSchema(Schema):
    name = fields.Str(required=True, validate=validate.Length(min=1, max=50))
    phone = fields.Str(required=True, validate=validate.Length(min=10, max=20))
    email = fields.Email(required=True, validate=validate.Length(max=100))
    password_hash = fields.Str(required=True,  validate=validate.Length(min=6))  # 只用于输入
    avatar = fields.Str(allow_none=True, validate=validate.Length(max=200))
    vehicle_type = fields.Str(allow_none=True, validate=validate.Length(max=50))
    license_plate = fields.Str(allow_none=True, validate=validate.Length(max=20))
    delivery_radius = fields.Int(allow_none=True, validate=validate.Range(min=0))
    is_available = fields.Bool(missing=True)
    is_online = fields.Bool(missing=True)


class UpdateRiderSchema(Schema):
    name = fields.Str(required=True, validate=validate.Length(min=1, max=50))
    phone = fields.Str(required=True, validate=validate.Length(min=10, max=20))
    email = fields.Email(required=True, validate=validate.Length(max=100))
    password_hash = fields.Str(required=True, validate=validate.Length(min=6))
    avatar = fields.Str(allow_none=True, validate=validate.Length(max=200))
    vehicle_type = fields.Str(allow_none=True, validate=validate.Length(max=50))
    license_plate = fields.Str(allow_none=True, validate=validate.Length(max=20))
    delivery_radius = fields.Int(allow_none=True, validate=validate.Range(min=0))
    is_available = fields.Bool(missing=True)
    is_online = fields.Bool(missing=True)
class RiderLoginSchema(Schema):
    email = fields.Email(required=True)
    password = fields.Str(
        required=True,
        validate=validate.Length(min=6, max=20),
        error_messages={"required": "密码不能为空"}
    )


class RiderLocationSchema(Schema):
    """骑手位置 Schema"""

    latitude = fields.Float(required=True, validate=validate.Range(min=-90, max=90))
    longitude = fields.Float(required=True, validate=validate.Range(min=-180, max=180))
    accuracy = fields.Float(allow_none=True, validate=validate.Range(min=0))
    speed = fields.Float(allow_none=True, validate=validate.Range(min=0))
    timestamp = fields.DateTime(allow_none=True)

    @validates('latitude')
    def validate_latitude(self, value):
        """验证纬度范围"""
        if not -90 <= value <= 90:
            raise ValidationError('纬度必须在 -90 到 90 之间')

    @validates('longitude')
    def validate_longitude(self, value):
        """验证经度范围"""
        if not -180 <= value <= 180:
            raise ValidationError('经度必须在 -180 到 180 之间')



class GetNearbySchema(Schema):
    lat = fields.Float(required=True)
    lon = fields.Float(required=True)
    radius = fields.Float()