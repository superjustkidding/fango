from app import db
from app.models import Restaurant
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






