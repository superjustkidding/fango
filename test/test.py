# -*- coding: utf-8 -*-
# @Time    : 2025/8/18 15:17
# @Author  : JustKidding
# @Email   : superjustkidding@gmail.com
# @File    : test.py
# @Software: PyCharm


from werkzeug.security import generate_password_hash, check_password_hash


ss = "admin123"

gen = generate_password_hash(ss)
print(gen)

check_password = check_password_hash(gen, ss)
print(check_password)