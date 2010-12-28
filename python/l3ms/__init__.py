# Module initialization for l3ms project.

from hashlib import md5
from django.contrib.admin.models import User

# Monkey-patch django User class to dumb down the password storage for
# compatibility with pgsql Apache auth module, which understands only
# unsalted MD5, crypt (yuk), or base64 (not one-way).

def set_bland_md5_password(user, raw_password):
    user.password = md5(raw_password).hexdigest()

def check_bland_md5_password(user, raw_password):
    return user.password == md5(raw_password).hexdigest()

User.set_password = set_bland_md5_password
User.check_password = check_bland_md5_password
