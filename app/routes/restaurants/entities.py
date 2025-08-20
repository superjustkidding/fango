# -*- coding: utf-8 -*-

from app import db
from app.models import Restaurant, MenuItem, MenuCategory
from app.utils.validation import BusinessValidationError
from lib.ecode import ECode

from werkzeug.security import generate_password_hash
from flask_jwt_extended import create_access_token, jwt_required


class RestaurantEntity:
    def __init__(self, current_user=None):
        self.current_user = current_user

    """获取餐馆列表"""
    def get_restaurants(self, **data):

        if not self.current_user or self.current_user.is_admin:
            raise BusinessValidationError("Permission denied", ECode.FORBID)

        query = Restaurant.query

        if 'name' in data:
            query = query.filter(Restaurant.name == data['name'])

        if 'address' in data:
            query = query.filter(Restaurant.address == data['address'])

        restaurants = query.all()
        return restaurants.to_dict(), ECode.SUCC


    """创建餐馆"""
    def create_restaurant(self, data):

        if Restaurant.query.filter_by(name=data['name']).first():
            raise BusinessValidationError('name already exists', ECode.CONFLICT)

        if Restaurant.query.filter_by(address=data['address']).first():
            raise BusinessValidationError('address already exists', ECode.CONFLICT)

        restaurant = Restaurant(
            name = data['name'],
            email = data['email'],
            address = data['address'],
            description = data['description'],
            phone = data.get('phone'),
            password_hash=generate_password_hash(data['password_hash']),
            is_active = data.get('is_active', True)
        )
        db.session.add(restaurant)
        db.session.commit()
        return restaurant.to_dict(), ECode.SUCC


    """餐馆登录"""
    def Rlogin(self, data):
        restaurant = Restaurant.query.filter_by(email=data['email']).first()

        if not restaurant or not restaurant.check_password(data['password']):
            raise BusinessValidationError("邮箱或密码错误", ECode.AUTH)

        access_token = create_access_token(identity=restaurant)

        return {
            'access_token': access_token,
            'restaurant': {
                'id': restaurant.id,
                'name': restaurant.name,
                'email': restaurant.email
            }
        }, ECode.SUCC


class RestaurantItemEntity:
    def __init__(self, current_user, restaurant_id):
        self.current_user = current_user
        self.restaurant_id = restaurant_id
        self.restaurant = Restaurant.query.get(restaurant_id)

    """餐馆"""
    def get_restaurant(self):
        if not self.restaurant_id and not self.current_user.is_admin:
            raise BusinessValidationError("Permission denied", ECode.FORBID)

        return self.restaurant.to_dict(), ECode.SUCC


    """餐馆更新"""
    def update_restaurant(self, data):

        if not self.restaurant_id and not self.current_user.is_admin:
            raise BusinessValidationError("Permission denied", ECode.FORBID)

        if 'name' in data:
            if data['name'] != self.restaurant.name and Restaurant.query.filter_by(name=data['name']).first():
                raise BusinessValidationError('name already exists', ECode.FORBID)
            self.restaurant.name = data['name']

        if 'address' in data:
            if data['address'] != self.restaurant.address and Restaurant.query.filter_by(address=data['address']).first():
                raise BusinessValidationError('address already exists', ECode.FORBID)
            self.restaurant.address = data['address']

        if 'email' in data:
            if data['email'] != self.restaurant.email and Restaurant.query.filter_by(email=data['email']).first():
                raise BusinessValidationError('email already exists', ECode.FORBID)
            self.restaurant.email = data['email']

        if 'phone' in data:
            if data['phone'] != self.restaurant.phone and Restaurant.query.filter_by(phone=data['phone']).first():
                raise BusinessValidationError('phone already exists', ECode.FORBID)
            self.restaurant.phone = data['phone']

        if 'password_hash' in data:
            self.restaurant.password_hash = generate_password_hash(data['password_hash'])

        db.session.commit()
        db.session.refresh(self.restaurant)

        return self.restaurant.to_dict(), ECode.SUCC

    def delete_resaurant(self):
        if not self.restaurant_id and not self.current_user.is_admin:
            raise BusinessValidationError("Permission denied", ECode.FORBID)

        if not self.restaurant:
            raise BusinessValidationError("Restaurant does not exist", ECode.NOTFOUND)

        if self.restaurant.deleted:
            raise BusinessValidationError("Restaurant already deleted", ECode.CONFLICT)

        self.restaurant.deleted = True
        db.session.commit()
        return {'message':'deleted successfully '}, ECode.SUCC


class MenuItemEntity:
    def __init__(self, current_user, restaurant_id, menuitem_id = None):
        self.current_user = current_user
        self.restaurant_id = restaurant_id
        self.menuitem = MenuItem.query.get(menuitem_id)


    """菜品创建"""

    def create_menu(self, data):

        if not self.current_user.id != self.restaurant_id:
            raise BusinessValidationError("Permission denied", ECode.ERROR)

        if MenuItem.query.filter_by(name=data['name']).first():
            raise BusinessValidationError('name already exists', ECode.ERROR)

        menuitem = MenuItem(
            name = data['name'],
            description = data['description'],
            price = data['price'],
            category_id = data['category_id'],
        )
        db.session.add(menuitem)
        db.session.commit()
        return menuitem.to_dict(), ECode.SUCC

    """菜品获取"""
    def get_menuitem(self,menuitem_id):
         menuitem = MenuItem.query.filter_by(restaurant_id=self.restaurant_id,
                                          menuitem_id = menuitem_id).first()
         return menuitem.MenuItem.to_dict(), ECode.SUCC



    """菜品更新"""
    def update_menuitem(self, data):

        if not self.restaurant_id :
            raise BusinessValidationError("Permission denied", ECode.FORBID)
        if 'name' in data:
            if data['name'] != self.menuitem.name and MenuItem.query.filter_by(name=data['name']).first():
                raise BusinessValidationError('name already exists', ECode.CONFLICT)
        db.session.commit()
        return self.menuitem.to_dict(), ECode.SUCC


    """菜品删除"""
    def delete_menuitem(self,menuitem_id):

        if not self.restaurant_id and not self.current_user :
            raise BusinessValidationError("Permission denied", ECode.FORBID)

        menuitem = MenuItem.query.filter_by(menuitem_id, restaurant_id=self.restaurant_id )
        db.session.delete(menuitem)
        db.session.commit()
        return {'message': 'deleted successfully '}, ECode.SUCC


class MenuCategoryEntity:
    def __init__(self, current_user, restaurant_id):
        self.current_user = current_user
        self.restaurant_id = restaurant_id

    """菜单分类创建"""
    def create_menu_category(self, data):
        if not self.current_user.id != self.restaurant_id:
            raise BusinessValidationError("Permission denied", ECode.FORBID)

        if MenuCategory.query.filter_by(name=data['name'], restaurant_id = self.restaurant_id).first():
            raise BusinessValidationError('name already exists', ECode.CONFLICT)

        category = MenuCategory(
            name = data['name'],
            description = data['description'],
            restaurant_id = self.restaurant_id,
            display_order = data['display_order'],
        )
        db.session.add(category)
        db.session.commit()
        return category.to_dict(), ECode.SUCC

    """菜单分类获取"""
    def get_menu_category(self, restaurant_id):
        categorys = MenuCategory.query.filter_by(restaurant_id=restaurant_id, deleted=False).all()
        return [cate.to_dict() for cate in categorys], ECode.SUCC

    """菜单分类更新"""
    def update_menu_category(self, data):
        if not self.restaurant_id :
            raise BusinessValidationError("Permission denied", ECode.FORBID)

        if 'name' in data:
            if MenuCategory.query.filter_by(name=data['name'], restaurant_id = self.restaurant_id).first():
                raise BusinessValidationError('name already exists', ECode.CONFLICT)

        db.session.commit()
        return MenuCategory.to_dict(), ECode.SUCC

    """菜单分类删除"""
    def delete_menu_category(self):
        if not self.restaurant_id and not self.current_user :
            raise BusinessValidationError("Permission denied", ECode.FORBID)

        menucategory = MenuCategory.query.filter_by(restaurant_id=self.restaurant_id)

        db.session.delete(menucategory)
        db.session.commit()
        return {'message': 'deleted successfully '}, ECode.SUCC




