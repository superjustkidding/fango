# -*- coding: utf-8 -*-

from app import db
from app.models import Restaurant, MenuItem, MenuCategory, MenuOptionGroup, MenuOption
from app.utils.validation import BusinessValidationError
from lib.ecode import ECode

from werkzeug.security import generate_password_hash
from app.routes.jwt import create_auth_token, current_user


class RestaurantEntity:
    def __init__(self, current_user=None):
        self.current_user = current_user

    """获取餐馆列表"""
    def get_restaurants(self, **data):

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

        access_token = create_auth_token(restaurant)

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

    """获取单个餐馆"""
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
        return {'message': 'deleted successfully '}, ECode.SUCC


class MenuItemListEntity:
    def __init__(self, current_user, restaurant_id, menuitem_id = None):
        self.current_user = current_user
        self.restaurant_id = restaurant_id
        if menuitem_id is not None:
            self.menuitem = MenuItem.query.get(menuitem_id)
        else:
            self.menuitem = None

    """ 菜品创建 """
    def create_menuitem(self, data):
        # 权限校验
        if self.current_user.id != self.restaurant_id:
            raise BusinessValidationError("Permission denied", ECode.ERROR)

        # 避免重名
        if MenuItem.query.filter_by(name=data['name'], restaurant_id=self.restaurant_id).first():
            raise BusinessValidationError('name already exists', ECode.ERROR)

        # 分类校验
        category = MenuCategory.query.get(data["category_id"])
        if not category or category.restaurant_id != self.restaurant_id:
            raise BusinessValidationError("Invalid category_id", ECode.ERROR)

        menuitem = MenuItem(
            name=data['name'],
            description=data['description'],
            price=data['price'],
            image=data.get('image'),
            preparation_time=data['preparation_time'],
            is_available=data.get('is_available', True),
            is_featured=data.get('is_featured', False),
            restaurant_id=self.restaurant_id,
            category_id=data['category_id'],
        )

        db.session.add(menuitem)
        db.session.commit()

        return menuitem.to_dict(), ECode.SUCC

    """ 获取餐厅所有菜品 """
    def get_menuitems(self):
        menus = MenuItem.query.filter_by(restaurant_id=self.restaurant_id, deleted=False).all()
        return [menu.to_dict() for menu in menus], ECode.SUCC

class MenuItemEntity:
    def __init__(self, current_user, menuitem_id=None):
        self.current_user = current_user
        self.menuitem = MenuItem.query.get(menuitem_id) if menuitem_id else None
        self.restaurant_id = self.menuitem.restaurant_id if self.menuitem else None
        self.restaurant = Restaurant.query.get(self.restaurant_id) if self.restaurant_id else None

    """ 获取单个菜品 """
    def get_menuitem(self):

        if not self.menuitem or self.menuitem.deleted:
            raise BusinessValidationError("Menu item not found", ECode.ERROR)
        return self.menuitem.to_dict(), ECode.SUCC


    """菜品更新"""
    def update_menuitem(self, data):

        if not self.restaurant:
            raise BusinessValidationError("Permission denied", ECode.ERROR)

        # 菜品是否存在
        if not self.menuitem or self.menuitem.restaurant_id != self.restaurant_id:
            raise BusinessValidationError("Menu item not found", ECode.ERROR)

        # 分类校验（如果传了 category_id）
        if "category_id" in data:
            category = MenuCategory.query.get(data["category_id"])
            if not category or category.restaurant_id != self.restaurant_id:
                raise BusinessValidationError("Invalid category_id", ECode.ERROR)
            self.menuitem.category_id = data["category_id"]

        # 字段更新
        if "name" in data:
            # 避免重名
            existing = MenuItem.query.filter_by(name=data["name"], restaurant_id=self.restaurant_id).first()
            if existing and existing.id != self.menuitem.id:
                raise BusinessValidationError("name already exists", ECode.ERROR)
            self.menuitem.name = data["name"]

        if "description" in data:
            self.menuitem.description = data["description"]

        if "price" in data:
            self.menuitem.price = data["price"]

        if "image" in data:
            self.menuitem.image = data["image"]

        if "is_available" in data:
            self.menuitem.is_available = data["is_available"]

        if "is_featured" in data:
            self.menuitem.is_featured = data["is_featured"]

        db.session.commit()

        return self.menuitem.to_dict(), ECode.SUCC

    """菜品删除"""
    def delete_menuitem(self ):

        if not self.menuitem:
            raise BusinessValidationError("Menu item not found", ECode.ERROR)

            # 权限校验：当前用户只能删除自己餐厅的菜品
        if self.restaurant.id != self.current_user.id:
            raise BusinessValidationError("Permission denied", ECode.ERROR)

            # 逻辑删除
        self.menuitem.deleted = True

        db.session.commit()
        return {"message": "Menu item deleted successfully"}, ECode.SUCC


class MenuCategoryListEntity:
    def __init__(self, current_user, restaurant_id):
        self.current_user = current_user
        self.restaurant_id = restaurant_id
        self.restaurant = Restaurant.query.get(restaurant_id) if self.restaurant_id else None

    """菜单分类创建"""
    def create_menu_category(self, data):

        if  self.current_user.id != self.restaurant_id:
            raise BusinessValidationError("Permission denied", ECode.FORBID)

        if MenuCategory.query.filter_by(name=data['name'], restaurant_id = self.restaurant_id).first():
            raise BusinessValidationError('name already exists', ECode.CONFLICT)

        category = MenuCategory(
            name=data['name'],
            description=data['description'],
            restaurant_id=self.restaurant_id,
            display_order=data['display_order'],
        )
        db.session.add(category)
        db.session.commit()
        return category.to_dict(), ECode.SUCC

    """菜单分类获取"""
    def get_menu_category(self, restaurant_id):
        categorys = MenuCategory.query.filter_by(restaurant_id=restaurant_id, deleted=False).all()
        return [cate.to_dict() for cate in categorys], ECode.SUCC


class MenuCategoryEntity:
    def __init__(self, current_user, menucategory_id=None):
        self.current_user = current_user
        self.menucategory = MenuCategory.query.get(menucategory_id)
        self.restaurant_id = self.menucategory.restaurant_id if self.menucategory else None
        self.restaurant = Restaurant.query.get(self.restaurant_id) if self.restaurant_id else None

    """菜单分类更新"""
    def update_menu_category(self, data):
        if not self.menucategory :
            raise BusinessValidationError("Category not found", ECode.ERROR)

        if  not self.restaurant:
            raise BusinessValidationError("Permission denied", ECode.FORBID)

        if 'name' in data:
            if MenuCategory.query.filter_by(name=data['name'], restaurant_id = self.restaurant_id).first():
                raise BusinessValidationError('name already exists', ECode.CONFLICT)
            self.menucategory.name = data['name']

        if 'description' in data:
            self.menucategory.description = data['description']

        if 'display_order' in data:
            self.menucategory.display_order = data['display_order']

        db.session.commit()
        return self.menucategory.to_dict(), ECode.SUCC

    """菜单分类删除"""
    def delete_menu_category(self):

        if not self.menucategory:
            raise BusinessValidationError("Menu category not found", ECode.ERROR)

        if  not self.current_user.id != self.restaurant_id:
            raise BusinessValidationError("Permission denied", ECode.FORBID)

        self.menucategory.deleted = True
        db.session.commit()
        return {'message': 'deleted successfully '}, ECode.SUCC


class MenuOptionGroupListEntity:
     def __init__(self, current_user, menu_item_id):
         self.current_user = current_user
         self.menuitem_id = menu_item_id
         self.menuitem = MenuItem.query.get(menu_item_id) if self.menuitem_id else None
         self.restaurant_id = self.menuitem.restaurant_id if self.menuitem else None


     def get_menu_group(self):

         if not self.menuitem:
             raise BusinessValidationError("Menu item not found", ECode.ERROR)

         groups = MenuOptionGroup.query.filter_by(menu_item_id=self.menuitem_id, deleted=False).all()
         return [g.to_dict() for g in groups], ECode.SUCC

     def create_menu_group(self, data):
         if not self.menuitem:
             raise BusinessValidationError("Menu item not found", ECode.ERROR)

         if self.current_user.id != self.restaurant_id:
             raise BusinessValidationError("Permission denied", ECode.FORBID)

         group = MenuOptionGroup(
             name=data['name'],
             is_required=data.get("is_required", False),
             max_selections=data.get("max_selections", 1),  # 给默认值，避免 KeyError
             min_selections=data.get("min_selections", 1),
             menu_item_id=self.menuitem_id
         )
         db.session.add(group)
         db.session.commit()
         return group.to_dict(), ECode.SUCC


class MenuOptionGroupEntity:

        def __init__(self, current_user, group_id):
            self.current_user = current_user
            self.group = MenuOptionGroup.query.get(group_id) if group_id else None
            self.menuitem = MenuItem.query.get(self.group.menu_item_id) if self.group else None
            self.restaurant_id = self.menuitem.restaurant_id if self.menuitem else None

        """更新选项组"""
        def update_menu_group(self, data):
            if not self.group:
                raise BusinessValidationError("Option group not found", ECode.ERROR)

            if self.current_user.id != self.restaurant_id:
                raise BusinessValidationError("Permission denied", ECode.FORBID)

            if "name" in data:
                if MenuOptionGroup.query.filter_by(name=data['name'], restaurant_id=self.restaurant_id).first():
                    raise BusinessValidationError('name already exists', ECode.CONFLICT)
                self.group.name = data["name"]

            if "is_required" in data:
                self.group.is_required = data["is_required"]

            if "max_selections" in data:
                self.group.max_selections = data["max_selections"]

            if "min_selections" in data:
                self.group.min_selections = data["min_selections"]

            db.session.commit()
            return self.group.to_dict(), ECode.SUCC

        """删除选项组"""
        def delete_menu_group(self):
            if not self.group:
                raise BusinessValidationError("Option group not found", ECode.ERROR)

            if self.current_user.id != self.restaurant_id:
                raise BusinessValidationError("Permission denied", ECode.FORBID)

            self.group.deleted = True
            db.session.commit()
            return {"message": "deleted successfully"}, ECode.SUCC


class MenuOptionListEntity:
    def __init__(self, current_user, option_group_id):
        self.current_user = current_user
        self.group = MenuOptionGroup.query.get(option_group_id) if option_group_id else None
        self.restaurant_id = self.group.menuitem.restaurant_id if self.group else None

    def get_options(self):
        if not self.group:
            raise BusinessValidationError("Option group not found", ECode.ERROR)

        options = MenuOption.query.filter_by(menu_item_id=self.group.menu_item_id, deleted=False).all()
        return [o.to_dict() for o in options]

    def create_option(self, data):
        if not self.group:
            raise BusinessValidationError("Option group not found", ECode.ERROR)

        if current_user.id != self.restaurant_id:
            raise BusinessValidationError("Permission denied", ECode.FORBID)

        option = MenuOption(
            name=data['name'],
            price=data['price'],
            option_group_id=self.group.id

        )
        db.session.add(option)
        db.session.commit()
        return option.to_dict(), ECode.SUCC








