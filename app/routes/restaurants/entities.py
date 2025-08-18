# -*- coding: utf-8 -*-
from flask_jwt_extended import create_access_token

from app import db
from app.models import Restaurant, MenuItem
from app.utils.validation import BusinessValidationError
from lib.ecode import ECode


class RestaurantEntity:
    def __init__(self, current_user=None):
        self.current_user = current_user

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


    def create_restaurant(self, data):
        if not self.current_user or self.current_user.is_admin:
            raise BusinessValidationError("Permission denied", ECode.FORBID)

        if Restaurant.query.filter_by(name=data['name']).first():
            raise BusinessValidationError('name already exists', ECode.CONFLICT)

        if Restaurant.query.filter_by(address=data['address']).first():
            raise BusinessValidationError('address already exists', ECode.CONFLICT)

        restaurant = Restaurant(
            name = data['name'],
            address = data['address'],
            phone = data.get('phone'),
            is_active = data.get('is_active', False)
        )

        restaurant.generate_password_hash(data['password_hash'])

        db.session.add(restaurant)
        db.seesion.commit()
        return restaurant.to_dict(), ECode.SUCC

    def Rlogin(self, data):
        restaurant = Restaurant.query.filter_by(name= data['email']).first()

        if not restaurant or not restaurant.check_password(data['password_hash']):
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
        self.restaurant = Restaurant.query.get(restaurant_id, Restaurant.deleted == False )


    def get_restaurant(self):
        if not self.restaurant_id and not self.current_user.is_admin:
            raise BusinessValidationError("Permission denied", ECode.FORBID)

        return self.restaurant.to_dict(), ECode.SUCC


    def update_restaurant(self, data):
        if not self.restaurant_id and not self.current_user.is_admin:
            raise BusinessValidationError("Permission denied", ECode.FORBID)

        if  'name' in data:
            if data['name'] != self.restaurant.name and Restaurant.query.filter_by(name=data['name']).first():
                raise BusinessValidationError('name already exists', ECode.FORBID)

        if 'address' in data:
            if data['address'] != self.restaurant.address and Restaurant.query.filter_by(address=data['address']).first():
                raise BusinessValidationError('address already exists', ECode.FORBID)

        if 'password_hash' in data:
                self.restaurant.password_hash = data['password_hash']

        db.session.commit()

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


class MenuItemEnity:
    def __init__(self, current_user, restaurant_id, menuitem_id):
        self.current_user = current_user
        self.restaurant_id = restaurant_id
        self.menuitem = MenuItem.query.get(menuitem_id, MenuItem.deleted == False )

    def create_menu(self, data):
        if not self.current_user.id != self.restaurant_id:
            raise BusinessValidationError("Permission denied", ECode.ERROR)

        if MenuItem.query.filter_by(name=data['name']).first():
            raise BusinessValidationError('name already exists', ECode.ERROR)

        menuitem = MenuItem(
            name = data['name'],
            description = data['description'],
            price = data['price'],
        )
        db.session.add(menuitem)
        db.session.commit()
        return menuitem.to_dict(), ECode.SUCC

    def get_menuitem(self):
         query = MenuItem.query.filter_by(restaurant_id=self.restaurant_id, is_deleted=False)
         return query.MenuItem.to_dict(), ECode.SUCC

    def update_menuitem(self, data):
        if not self.restaurant_id :
            raise BusinessValidationError("Permission denied", ECode.FORBID)
        if 'name' in data:
            if  data['name'] != self.menuitem.name and MenuItem.query.filter_by(name=data['name']).first():
                raise BusinessValidationError('name already exists', ECode.CONFLICT)
        db.session.commit()
        return self.menuitem.to_dict(), ECode.SUCC












