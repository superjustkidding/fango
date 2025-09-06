# -*- coding: utf-8 -*-
from decimal import Decimal
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from app import db
from app.models import Restaurant, MenuItem, MenuCategory, MenuOptionGroup, MenuOption, DeliveryZone, OperatingHours, \
    Promotion, DeliveryPolygon, RestaurantStatistics
from app.routes.logger import logger
from app.utils.validation import BusinessValidationError
from lib.ecode import ECode
from werkzeug.security import generate_password_hash
from app.routes.jwt import create_auth_token


class RestaurantEntity:
    def __init__(self, current_user=None):
        self.current_user = current_user

    def get_restaurants(self, **data):
        try:
            query = Restaurant.query.filter_by(deleted=False)  # 添加已删除过滤

            if 'name' in data and data['name']:
                query = query.filter(Restaurant.name.ilike(f"%{data['name']}%"))  # 改为模糊查询
                logger.debug("按餐馆名称模糊查询: %s", data['name'])

            if 'address' in data and data['address']:
                query = query.filter(Restaurant.address.ilike(f"%{data['address']}%"))  # 改为模糊查询
                logger.debug("按餐馆地址模糊查询: %s", data['address'])

            restaurants = query.all()
            logger.info("餐馆查询完成，共 %d 条结果", len(restaurants))
            return [restaurant.to_dict() for restaurant in restaurants], ECode.SUCC  # 修复to_dict()调用
        except Exception as e:
            logger.error("餐馆查询失败，条件: %s，错误: %s", data, str(e), exc_info=True)
            raise BusinessValidationError("服务器内部错误", ECode.INTER)
    """创建餐馆"""
    def create_restaurant(self, data):
        try:
            if Restaurant.query.filter_by(name=data['name']).first():
                logger.warning(f"餐馆创建失败：name={data['name']} 已存在")
                raise BusinessValidationError('name already exists', ECode.CONFLICT)

            if Restaurant.query.filter_by(address=data['address']).first():
                logger.warning(f"餐馆创建失败：address={data['address']} 已存在")
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
            logger.info(f"餐馆创建成功：id={restaurant.id}, name={restaurant.name}")
            return restaurant.to_dict(), ECode.SUCC
        except IntegrityError as e:
            db.session.rollback()
            logger.error(f"餐馆创建失败(数据库唯一约束错误)：{str(e)}", exc_info=True)
            raise BusinessValidationError('数据库约束错误,请检查输入', ECode.CONFLICT)
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f"餐馆创建失败(SQLAlchemy错误)：{str(e)}", exc_info=True)
            raise BusinessValidationError('数据库错误', ECode.INTER)

    """餐馆登录"""
    def Rlogin(self, data):
        try:
            restaurant = Restaurant.query.filter_by(email=data['email']).first()

            if not restaurant or not restaurant.check_password(data['password']):
                logger.warning(f"餐馆登录失败： email={data['email']} , 原因：邮箱或密码错误")
                raise BusinessValidationError("邮箱或密码错误", ECode.AUTH)

            access_token = create_auth_token(restaurant)
            logger.info(f"餐馆登录成功：id={restaurant.id}, email={data['email']}")

            return {
                'access_token': access_token,
                'restaurant': {
                    'id': restaurant.id,
                    'name': restaurant.name,
                    'email': restaurant.email
                }
            }, ECode.SUCC
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f"餐馆创建失败(SQLAlchemy错误)：{str(e)}", exc_info=True)
            raise BusinessValidationError('数据库错误', ECode.INTER)


class RestaurantItemEntity:
    def __init__(self, current_user, restaurant_id):
        self.current_user = current_user
        self.restaurant_id = restaurant_id
        self.restaurant = Restaurant.query.get(restaurant_id)

    """获取单个餐馆"""
    def get_restaurant(self):
        try:
            if not self.restaurant:
                logger.warning(f"获取餐馆失败， ID=%s， 不存在", getattr(self.restaurant, 'id', None))
                raise BusinessValidationError("Restaurant not found", ECode.NOTFOUND)

            if not self.restaurant_id and not self.current_user.is_admin:
                logger.warning("获取餐馆失败：无权限", getattr(self.restaurant, 'id', None))
                raise BusinessValidationError("Permission denied", ECode.FORBID)
            logger.info('获取餐馆成功')
            return self.restaurant.to_dict(), ECode.SUCC
        except Exception as e:
            logger.error("获取餐馆异常", getattr(self.restaurant, 'id', None))
            raise

    """餐馆更新"""
    def update_restaurant(self, data):
        try:
            if not self.restaurant:
                logger.warning("更新餐馆失败：ID=%s，不存在", getattr(self.restaurant, 'id', None))
                raise BusinessValidationError("Restaurant does not currently exist", ECode.FORBID)

            if not self.current_user.is_admin and self.current_user.id != self.restaurant.id:
                logger.warning("用户尝试更新餐馆失败：无权限", getattr(self.restaurant, 'id', None))
                raise BusinessValidationError("Permission denied", ECode.FORBID)

            if 'name' in data:
                if data['name'] != self.restaurant.name and Restaurant.query.filter_by(name=data['name']).first():
                    logger.warning("餐馆名称已存在：%s", data['name'])
                    raise BusinessValidationError('name already exists', ECode.FORBID)
                self.restaurant.name = data['name']

            if 'address' in data:
                if data['address'] != self.restaurant.address and Restaurant.query.filter_by(address=data['address']).first():
                    logger.warning('餐馆地址已存在：%s', data['address'])
                    raise BusinessValidationError('address already exists', ECode.FORBID)
                self.restaurant.address = data['address']

            if 'email' in data:
                if data['email'] != self.restaurant.email and Restaurant.query.filter_by(email=data['email']).first():
                    logger.warning("餐馆邮箱已存在：%s", data['email'])
                    raise BusinessValidationError('email already exists', ECode.FORBID)
                self.restaurant.email = data['email']

            if 'phone' in data:
                if data['phone'] != self.restaurant.phone and Restaurant.query.filter_by(phone=data['phone']).first():
                    logger.warning("餐馆手机号已存在：%s", data['phone'])
                    raise BusinessValidationError('phone already exists', ECode.FORBID)
                self.restaurant.phone = data['phone']

            if 'password_hash' in data:
                logger.debug('用户(ID%s)更新餐馆密码',self.restaurant.id, self.current_user.id)
                self.restaurant.password_hash = generate_password_hash(data['password_hash'])

            db.session.commit()
            db.session.refresh(self.restaurant)
            logger.info("更新餐馆成功", self.restaurant.id)
            return self.restaurant.to_dict(), ECode.SUCC
        except Exception as e:
            logger.error("更新餐馆(ID=%s)异常: %s", getattr(self, "restaurant_id", None), str(e), exc_info=True)
            raise


    def delete_restaurant(self):
        if not self.restaurant:
            logger.warning("删除餐馆失败，ID=%s，不存在", getattr(self, "restaurant_id", None))
            raise BusinessValidationError("Restaurant does not exist", ECode.NOTFOUND)

        if self.restaurant.deleted:
            logger.warning("删除餐馆失败，ID=%s 已经被删除", self.restaurant.id)
            raise BusinessValidationError("Restaurant already deleted", ECode.CONFLICT)

        self.restaurant.deleted = True
        db.session.commit()
        logger.info("餐馆(ID=%s)删除成功", self.restaurant.id)
        return {'message': 'deleted successfully '}, ECode.SUCC


class MenuItemListEntity:
    def __init__(self, current_user, restaurant_id):
        self.current_user = current_user
        self.restaurant_id = restaurant_id
        self.restaurant = Restaurant.query.get(restaurant_id)

    """ 菜品创建 """
    def create_menuitem(self, data):

        # 避免重名
        if MenuItem.query.filter_by(name=data['name'], restaurant_id=self.restaurant_id).first():
            logger.warning("创建菜品失败，餐馆ID=%s，菜品名称=%s 已存在",
                           getattr(self.restaurant, 'id', None),
                           data['name'])
            raise BusinessValidationError('name already exists', ECode.ERROR)

        # 分类校验
        category = MenuCategory.query.get(data["category_id"])
        if not category or category.restaurant_id != self.restaurant_id:
            logger.error("创建菜品失败，餐馆ID=%s，提供的分类ID=%s 无效",
                         getattr(self.restaurant, 'id', None),
                         data["category_id"])
            raise BusinessValidationError("Invalid category_id", ECode.ERROR)

        menuitem = MenuItem(
            name=data['name'],
            description=data['description'],
            price=Decimal(data["price"]),
            image=data.get('image'),
            preparation_time=data['preparation_time'],
            is_available=data.get('is_available', True),
            is_featured=data.get('is_featured', False),
            restaurant_id=self.restaurant_id,
            category_id=data['category_id'],
        )

        db.session.add(menuitem)
        db.session.commit()
        logger.info("菜品创建成功",
                    getattr(self.restaurant, 'id', None),
                    id={menuitem.id},
                    name={menuitem.name})
        return menuitem.to_dict(), ECode.SUCC

    """ 获取餐厅所有菜品 """
    def get_all_menuitem(self):
        menus = MenuItem.query.filter_by(restaurant_id=self.restaurant_id, deleted=False).all()
        logger.info("获取餐馆ID=%s 的所有菜品，总数=%s",
                    self.restaurant_id, len(menus))
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
            logger.warning("获取菜品失败，菜品不存在或已被删除 (menuitem_id=%s, restaurant_id=%s)",
                           getattr(self.menuitem, 'id', None), self.restaurant_id)
            raise BusinessValidationError("Menu item not found", ECode.ERROR)
        logger.info('获取菜品ID%s(menuitem_id=%s, restaurant_id=%s)')
        return self.menuitem.to_dict(), ECode.SUCC


    """菜品更新"""
    def update_menuitem(self, data):

        if not self.restaurant:
            logger.error("菜品更新失败，无权限 (user_id=%s)", getattr(self.current_user, 'id', None))
            raise BusinessValidationError("Permission denied", ECode.ERROR)

        # 菜品是否存在
        if not self.menuitem or self.menuitem.restaurant_id != self.restaurant_id:
            logger.warning("菜品更新失败，菜品不存在 (menuitem_id=%s, restaurant_id=%s)",
                           getattr(self.menuitem, 'id', None), self.restaurant_id)
            raise BusinessValidationError("Menu item not found", ECode.ERROR)

        # 分类校验（如果传了 category_id）
        if "category_id" in data:
            category = MenuCategory.query.get(data["category_id"])
            if not category or category.restaurant_id != self.restaurant_id:
                logger.error("菜品更新失败，分类非法 (menuitem_id=%s, category_id=%s, restaurant_id=%s)",
                             self.menuitem.id, data["category_id"], self.restaurant_id)
                raise BusinessValidationError("Invalid category_id", ECode.AUTH)
            self.menuitem.category_id = data["category_id"]

        # 字段更新
        if "name" in data:
            # 避免重名
            existing = MenuItem.query.filter_by(name=data["name"], restaurant_id=self.restaurant_id).first()
            if existing and existing.id != self.menuitem.id:
                logger.warning("菜品更新失败，名称已存在 (restaurant_id=%s, name=%s)",
                               self.restaurant_id, data["name"])
                raise BusinessValidationError("name already exists", ECode.ERROR)
            self.menuitem.name = data["name"]

        if "description" in data:
            self.menuitem.description = data["description"]

        if "price" in data:
            self.menuitem.price = Decimal(data["price"])

        if "image" in data:
            self.menuitem.image = data["image"]

        if "is_available" in data:
            self.menuitem.is_available = data["is_available"]

        if "is_featured" in data:
            self.menuitem.is_featured = data["is_featured"]

        db.session.commit()
        logger.info("菜品更新成功 (menuitem_id=%s, restaurant_id=%s)",
                    self.menuitem.id, self.restaurant_id)
        return self.menuitem.to_dict(), ECode.SUCC

    """菜品删除"""
    def delete_menuitem(self ):

        if not self.menuitem:
            logger.warning("菜品未找到(restaurant_id=%s)", self.restaurant_id)
            raise BusinessValidationError("Menu item not found", ECode.ERROR)

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

        if MenuCategory.query.filter_by(name=data['name'], restaurant_id = self.restaurant_id).first():
            logger.warning("菜单分类创建失败，分类已存在 (restaurant_id=%s, name=%s)",
                           self.restaurant_id, data['name'])
            raise BusinessValidationError('name already exists', ECode.CONFLICT)

        category = MenuCategory(
            name=data['name'],
            description=data['description'],
            restaurant_id=self.restaurant_id,
            display_order=data['display_order'],
        )
        db.session.add(category)
        db.session.commit()
        logger.info("菜单分类创建成功 (category_id=%s, restaurant_id=%s, name=%s)",
                    category.id, self.restaurant_id, category.name)
        return category.to_dict(), ECode.SUCC

    """菜单分类获取"""
    def get_menu_category(self, restaurant_id):
        category = MenuCategory.query.filter_by(restaurant_id=restaurant_id, deleted=False).all()
        logger.info("获取菜单分类成功，共 %s 个 (restaurant_id=%s)", len(category), restaurant_id)
        return [cate.to_dict() for cate in category], ECode.SUCC


class MenuCategoryEntity:
    def __init__(self, current_user, menucategory_id=None):
        self.current_user = current_user
        self.menucategory = MenuCategory.query.get(menucategory_id)
        self.restaurant_id = self.menucategory.restaurant_id if self.menucategory else None
        self.restaurant = Restaurant.query.get(self.restaurant_id) if self.restaurant_id else None

    """菜单分类更新"""
    def update_menu_category(self, data):
        if not self.menucategory:
            logger.warning("菜品分类更新失败，菜品分类不存在 (menucategory_id=%s, restaurant_id=%s)",
                           getattr(self.menucategory, 'id', None), self.restaurant_id)
            raise BusinessValidationError("Category not found", ECode.ERROR)

        if not self.restaurant:
            logger.error("菜品更新失败，无权限 (user_id=%s)", getattr(self.current_user, 'id', None))
            raise BusinessValidationError("Permission denied", ECode.FORBID)

        if 'name' in data:
            if MenuCategory.query.filter_by(name=data['name'], restaurant_id=self.restaurant_id).first():
                logger.warning("菜品分类更新失败，名称已存在 (restaurant_id=%s, name=%s)",
                               self.restaurant_id, data["name"])
                raise BusinessValidationError('name already exists', ECode.CONFLICT)
            self.menucategory.name = data['name']

        if 'description' in data:
            self.menucategory.description = data['description']

        if 'display_order' in data:
            self.menucategory.display_order = data['display_order']

        db.session.commit()
        logger.info("menu_category updated successfully")
        return self.menucategory.to_dict(), ECode.SUCC

    """菜单分类删除"""
    def delete_menu_category(self):

        if not self.menucategory:
            logger.error('menu category not found')
            raise BusinessValidationError("Menu category not found", ECode.ERROR)

        self.menucategory.deleted = True
        db.session.commit()
        logger.info("menu_category deleted successfully")
        return {'message': 'deleted successfully '}, ECode.SUCC


class MenuOptionGroupListEntity:
     def __init__(self, current_user, menu_item_id):
         self.current_user = current_user
         self.menuitem_id = menu_item_id
         self.menuitem = MenuItem.query.get(menu_item_id) if self.menuitem_id else None
         self.restaurant_id = self.menuitem.restaurant_id if self.menuitem else None

     def get_menu_group(self):
         if not self.menuitem:
             logger.error('menu item not found')
             raise BusinessValidationError("Menu item not found", ECode.ERROR)

         groups = MenuOptionGroup.query.filter_by(menu_item_id=self.menuitem_id, deleted=False).all()
         logger.info('acquire success')
         return [g.to_dict() for g in groups], ECode.SUCC

     def create_menu_group(self, data):
         if not self.menuitem:
             logger.error('menu item not found')
             raise BusinessValidationError("Menu item not found", ECode.ERROR)

         group = MenuOptionGroup(
             name=data['name'],
             is_required=data.get("is_required", False),
             max_selections=data.get("max_selections", 1),  # 给默认值，避免 KeyError
             min_selections=data.get("min_selections", 1),
             menu_item_id=self.menuitem_id
         )
         db.session.add(group)
         db.session.commit()
         logger.info("menu_group created successfully")
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
                logger.warning("Option group not found")
                raise BusinessValidationError("Option group not found", ECode.ERROR)

            if "name" in data:
                existing = MenuOptionGroup.query.filter_by(
                    name=data['name'],
                    menu_item_id=self.group.menu_item_id
                ).first()
                if existing and existing.id != self.group.id:
                    logger.warning("Option group name already exists")
                    raise BusinessValidationError('name already exists', ECode.CONFLICT)
                self.group.name = data["name"]

            if "is_required" in data:
                self.group.is_required = data["is_required"]

            if "max_selections" in data:
                self.group.max_selections = data["max_selections"]

            if "min_selections" in data:
                self.group.min_selections = data["min_selections"]

            db.session.commit()
            logger.info("menu_group updated successfully")
            return self.group.to_dict(), ECode.SUCC

        """删除选项组"""
        def delete_menu_group(self):
            if not self.group:
                logger.warning("Option group not found")
                raise BusinessValidationError("Option group not found", ECode.ERROR)

            self.group.deleted = True
            db.session.commit()
            logger.info("menu_group deleted successfully")
            return {"message": "deleted successfully"}, ECode.SUCC


class MenuOptionListEntity:
    def __init__(self, current_user, group_id):
        self.current_user = current_user
        self.group = MenuOptionGroup.query.get(group_id) if group_id else None
        # self.restaurant_id = self.group.restaurant_id if self.group else None

    def get_options(self):
        if not self.group:
            logger.warning("Option not found")
            raise BusinessValidationError("Option group not found", ECode.ERROR)

        options = MenuOption.query.filter_by(option_group_id=self.group.id, deleted=False).all()
        logger.info('acquire success')
        return [o.to_dict() for o in options], ECode.SUCC

    def create_option(self, data):
        if not self.group:
            logger.warning("Option not found")
            raise BusinessValidationError("Option group not found", ECode.ERROR)

        # if current_user.id != self.restaurant_id:
        #     raise BusinessValidationError("Permission denied", ECode.FORBID)

        option = MenuOption(
            name=data['name'],
            price=Decimal(data['price']),
            option_group_id=self.group.id
        )
        db.session.add(option)
        db.session.commit()
        logger.info("option created successfully")
        return option.to_dict(), ECode.SUCC


class MenuOptionEntity:
    def __init__(self, current_user, menu_option_id):
        self.current_user = current_user
        self.menu_option_id = menu_option_id
        self.option = MenuOption.query.get(menu_option_id) if menu_option_id else None

    def update_menu_option(self, data):
        if not self.option:
            logger.warning("Option not found")
            raise BusinessValidationError("Option not found", ECode.ERROR)

        if 'name' in data:
            existing = MenuOption.query.filter_by(
                name=data['name'],
                option_group_id=self.option.option_group_id
            ).first()
            if existing and existing.id != self.option.id:
                logger.warning("Option name already exists")
                raise BusinessValidationError('name already exists', ECode.CONFLICT)
            self.option.name = data["name"]

        if 'price' in data:
            self.option.price = Decimal(data['price'])
        db.session.commit()
        logger.info("menu_option updated successfully")
        return self.option.to_dict(), ECode.SUCC

    def delete_menu_option(self):
        if not self.option:
            logger.warning('Option not found')
            raise BusinessValidationError("Option not found", ECode.ERROR)

        self.option.deleted = True
        db.session.commit()
        logger.info("menu_option deleted successfully")
        return {"message": "deleted successfully"}, ECode.SUCC


class DeliveryZoneListEntity:
    def __init__(self, current_user, restaurant_id):
        self.current_user = current_user
        self.restaurant_id = restaurant_id
        self.restaurant = Restaurant.query.get(restaurant_id)

    def get_delivery_zones(self):
        if not self.restaurant:
            logger.warning("Restaurant not found")
            raise BusinessValidationError("Restaurant not found", ECode.ERROR)
        delivery_zones =DeliveryZone.query.filter_by(restaurant_id=self.restaurant.id).all()
        logger.info('acquire success')
        return [d.to_dict() for d in delivery_zones], ECode.SUCC

    def create_delivery_zone(self, data):
        if not self.restaurant:
            logger.warning("Restaurant not found")
            raise BusinessValidationError("Restaurant not found", ECode.ERROR)
        delivery_zone = DeliveryZone(
            name=data['name'],
            delivery_fee=Decimal(data['delivery_fee']),
            min_order_amount=Decimal(data['min_order_amount']),
            delivery_time=data['delivery_time'],
            restaurant_id=self.restaurant.id,
        )
        db.session.add(delivery_zone)
        db.session.commit()
        logger.info("delivery_zone created successfully")
        return delivery_zone.to_dict(), ECode.SUCC


class DeliveryZoneEntity:
    def __init__(self, current_user, delivery_zone_id):
        self.current_user = current_user
        self.delivery_zone = DeliveryZone.query.get(delivery_zone_id)
        self.restaurant_id = self.delivery_zone.restaurant_id if self.delivery_zone else None
        self.restaurant = Restaurant.query.get(self.restaurant_id) if self.restaurant_id else None

    def update_delivery_zone(self, data):
        if not self.restaurant:
            logger.warning("Restaurant not found")
            raise BusinessValidationError("Restaurant not found", ECode.ERROR)
        if "name" in data:
            # 去掉前后空格，统一大小写，避免误判
            new_name = data["name"].strip()

            existing = DeliveryZone.query.filter(
                DeliveryZone.restaurant_id == self.restaurant.id,
                DeliveryZone.name == new_name,
                DeliveryZone.id != self.delivery_zone.id
            ).first()

            if existing:
                logger.warning("DeliveryZone already exists")
                raise BusinessValidationError("Name already exists", ECode.CONFLICT)

            self.delivery_zone.name = new_name

        if 'delivery_fee' in data:
            self.delivery_zone.delivery_fee = Decimal(data['delivery_fee'])

        if 'min_order_amount' in data:
            self.delivery_zone.min_order_amount = Decimal(data['min_order_amount'])

        if 'delivery_time' in data:
            self.delivery_zone.delivery_time = data['delivery_time']

        db.session.commit()
        logger.info("delivery_zone updated successfully")
        return self.delivery_zone.to_dict(), ECode.SUCC

    def delete_delivery_zone(self):
        if not self.restaurant:
            logger.warning("Restaurant not found")
            raise BusinessValidationError("Restaurant not found", ECode.ERROR)

        self.delivery_zone.deleted = True
        db.session.commit()
        logger.info('delivery_zone deleted successfully')
        return {"message": "deleted successfully"}, ECode.SUCC

class DeliveryPolygonListEntity:
    def __init__(self, current_user, zone_id):
        self.current_user = current_user
        self.zone_id = zone_id
        self.zone = DeliveryZone.query.get(zone_id)

    def create_polygon(self, data):
        if not self.current_user.is_admin:
            logger.warning('Permission denied')
            raise BusinessValidationError("Permission denied", ECode.FORBID)

        polygon = DeliveryPolygon(
            coordinates=data["coordinates"],
            zone_id=self.zone_id
        )
        db.session.add(polygon)
        db.session.commit()
        logger.info("polygon created successfully")
        return polygon.to_dict(), ECode.SUCC


class DeliveryPolygonEntity:
    def __init__(self, current_user, polygon_id):
        self.current_user = current_user
        self.polygon = DeliveryPolygon.query.get(polygon_id)

        if not self.polygon:
            logger.warning("Polygon not found")
            raise BusinessValidationError("Polygon not found", ECode.NOTFOUND)

    def get_polygon(self, polygon_id):
        """
        获取单个多边形
        """
        polygon = DeliveryPolygon.query.get(polygon_id)

        return polygon.to_dict(), ECode.SUCC

    def delete_polygon(self, polygon_id):
        """
        删除多边形
        """
        polygon = DeliveryPolygon.query.get(polygon_id)
        db.session.delete(polygon)
        db.session.commit()
        return {"message": "Deleted"}, ECode.SUCC

class OperatingHoursListEntity:
    def __init__(self, current_user, restaurant_id):
        self.current_user = current_user
        self.restaurant_id = restaurant_id
        self.restaurant = Restaurant.query.get(restaurant_id)

        if not self.restaurant:
            logger.warning("Restaurant not found")
            raise BusinessValidationError("Restaurant not found", ECode.ERROR)

    def get_operating_hour(self):
        operating_hour = OperatingHours.query.filter_by(restaurant_id=self.restaurant.id)
        logger.info('acquire success')
        return [o.to_dict() for o in operating_hour], ECode.SUCC

    def create_operating_hour(self, data):
        operating_hour = OperatingHours(
            day_of_week=data['day_of_week'],
            open_time=data['open_time'],
            close_time=data['close_time'],
            is_closed=data['is_closed'],
            restaurant_id=self.restaurant.id,
        )
        db.session.add(operating_hour)
        db.session.commit()
        logger.info("operating_hour created successfully")
        return operating_hour.to_dict(), ECode.SUCC


class OperatingHoursEntity:
    def __init__(self, current_user, operating_hours_id):
        self.current_user = current_user
        self.operating_hour = OperatingHours.query.get(operating_hours_id)
        self.restaurant_id = self.operating_hour.restaurant_id if self.operating_hour else None
        self.restaurant = Restaurant.query.get(self.restaurant_id) if self.restaurant_id else None

    def update_operating_hour(self, data):
        if not self.restaurant:
            logger.warning("Restaurant not found")
            raise BusinessValidationError("Restaurant not found", ECode.ERROR)
            # 更新 day_of_week
        if "day_of_week" in data:
            self.operating_hour.day_of_week = data["day_of_week"]

            # 更新 open_time
        if "open_time" in data:
            self.operating_hour.open_time = data["open_time"]

            # 更新 close_time
        if "close_time" in data:
            self.operating_hour.close_time = data["close_time"]

            # 校验时间范围
        if (
                self.operating_hour.open_time
                and self.operating_hour.close_time
                and self.operating_hour.open_time >= self.operating_hour.close_time
            ):
                logger.warning("Open time must be earlier than close time")
                raise BusinessValidationError("Open time must be earlier than close time", ECode.ERROR)

        db.session.commit()
        logger.info("operating_hour updated successfully")
        return self.operating_hour.to_dict(), ECode.SUCC

    def delete_operating_hour(self):
        if not self.operating_hour:
            logger.warning("Operating hour not found")
            raise BusinessValidationError("Operating hours not found", ECode.NOTFOUND)

        self.operating_hour.deleted = True
        db.session.commit()
        logger.info("Operating hour deleted successfully")
        return {"message": "Operating hours deleted successfully"}, ECode.SUCC


class PromotionListEntity:
    def __init__(self, current_user, restaurant_id):
        self.current_user = current_user
        self.restaurant_id = restaurant_id
        self.restaurant = Restaurant.query.get(restaurant_id)

    def get_promotion(self):
        if not self.restaurant:
            logger.warning("Restaurant not found")
            raise BusinessValidationError("Restaurant not found", ECode.ERROR)
        promotion = Promotion.query.filter_by(restaurant_id=self.restaurant.id).all()
        logger.info('acquire success')
        return [p.to_dict() for p in promotion], ECode.SUCC

    def post_promotion(self, data):
        if not self.restaurant:
            logger.warning("Restaurant not found")
            raise BusinessValidationError("Restaurant not found", ECode.ERROR)
        promotion = Promotion(
            title=data['title'],
            description=data['description'],
            image=data['image'],
            start_date=data['start_date'],
            end_date=data['end_date'],
            is_active=data.get('is_active'),
            restaurant_id=self.restaurant.id,
        )
        db.session.add(promotion)
        db.session.commit()
        logger.info("promotion created successfully")
        return promotion.to_dict(), ECode.SUCC


class PromotionEntity:
    def __init__(self, current_user, promotion_id):
        self.current_user = current_user
        self.promotion = Promotion.query.get(promotion_id)
        self.restaurant_id = self.promotion.restaurant_id if self.promotion else None
        self.restaurant = Restaurant.query.get(self.restaurant_id) if self.restaurant_id else None

    def update_promotion(self, data):
        if not self.restaurant:
            logger.warning("Restaurant not found")
            raise BusinessValidationError("Restaurant not found", ECode.ERROR)

        if 'title' in data:
            existing = Promotion.query.filter(
                Promotion.title == data['title'],
                Promotion.restaurant_id == self.restaurant_id,
                Promotion.id != self.promotion.id,
                Promotion.deleted == False
            ).first()
            if existing:
                logger.warning("Promotion already exists")
                raise BusinessValidationError('Promotion title already exists', ECode.CONFLICT)
            self.promotion.title = data['title'].strip()

        if 'description' in data:
            self.promotion.description = data['description']

        if 'image' in data:
            self.promotion.image = data['image']

        if 'start_date' in data:
            self.promotion.start_date = data['start_date']

        if 'end_date' in data:
            self.promotion.end_date = data['end_date']

            # 验证时间逻辑
            if (self.promotion.start_date and self.promotion.end_date and
                    self.promotion.end_date <= self.promotion.start_date):
                raise BusinessValidationError('结束时间必须晚于开始时间', ECode.BAD_REQUEST)

        if 'is_active' in data:
            self.promotion.is_active = data['is_active']

        db.session.commit()
        logger.info("promotion updated successfully")
        return self.promotion.to_dict(), ECode.SUCC

    def delete_promotion(self):
        if not self.restaurant:
            logger.warning("Restaurant not found")
            raise BusinessValidationError("Restaurant not found", ECode.ERROR)
        self.promotion.deleted = True
        db.session.commit()
        return {'message':"deleted successfully"}, ECode.SUCC


class RestaurantStatisticsEntity:
    def __init__(self, current_user, restaurant_id):
        self.current_user = current_user
        self.restaurant_id = restaurant_id
        self.restaurant = Restaurant.query.get(restaurant_id)

        if not self.restaurant:
            logger.warning('Restaurant not found')
            raise BusinessValidationError("Restaurant not found", ECode.NOTFOUND)

    def list_statistics(self):
        """
        获取餐馆的所有统计历史数据（管理员专用）
        """
        if not self.current_user.is_admin and self.restaurant_id:
            logger.warning("Permission denied")
            raise BusinessValidationError("Permission denied", ECode.FORBID)

        stats = RestaurantStatistics.query.filter_by(restaurant_id=self.restaurant_id).order_by(
            RestaurantStatistics.date.desc()
        ).all()
        logger.info('acquire list statistics')
        return [s.to_dict() for s in stats], ECode.SUCC

    def get_statistics(self, date):
        if not self.current_user.is_admin and self.restaurant_id:
            logger.warning("Permission denied")
            raise BusinessValidationError("Permission denied", ECode.FORBID)

        query = RestaurantStatistics.query.filter_by(restaurant_id=self.restaurant_id)

        if date:
            query = query.filter_by(date=date)
            stat = query.first()
        else:
            # 默认获取最新一条
            stat = query.order_by(RestaurantStatistics.date.desc()).first()

        if not stat:
            logger.warning("Statistics not found")
            raise BusinessValidationError("Statistics not found", ECode.NOTFOUND)
        logger.info('acquire success')
        return stat.to_dict(), ECode.SUCC

