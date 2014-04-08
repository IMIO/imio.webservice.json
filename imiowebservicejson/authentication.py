# -*- coding: utf-8 -*-
import hashlib


def check_authentication(userid, passwd, request):
    user = get_user(userid, request)
    salt = request.registry.settings.get('auth.secret')
    pwd = hashlib.md5('%(salt)s%(pwd)s%(salt)s' % {'salt': salt,
                                                   'pwd': passwd}).hexdigest()
    if user and user.check_password(pwd) is True:
        return []


class User(object):

    def __init__(self, userid, password):
        self.userid = userid
        self.password = password

    def check_password(self, passwd):
        return self.password == passwd


def get_user(userid, request):
    user = User(request.registry.settings.get('auth.login'),
                request.registry.settings.get('auth.password'))
    if user.userid == userid:
        return user
