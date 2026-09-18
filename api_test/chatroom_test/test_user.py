# -*- coding: utf-8 -*-
"""用户模块测试：注册 /register、登录 /login、获取用户信息 /userInfo。

结构：class = 一个接口，def test_xxx = 一条用例（对应 Excel 里的用例）。
断言规则：assert 实际结果 == 预期结果。
"""
import allure

from chatroom_test.conftest import make_username


@allure.feature("用户模块")
@allure.story("注册")
class TestRegister:
    """注册接口 /register"""

    def test_register_success(self, api):
        """正常注册：唯一用户名+合法密码 → code=0，密码返回脱敏"""
        username = make_username()
        res = api.register(username, "123456")
        assert res["code"] == 0
        assert res["data"]["username"] == username
        assert res["data"]["password"] == ""

    def test_register_missing_username(self, api):
        """缺用户名 → code=1003"""
        res = api.register("", "123456")
        assert res["code"] == 1003

    def test_register_missing_password(self, api):
        """缺密码 → code=1003"""
        res = api.register(make_username(), "")
        assert res["code"] == 1003

    def test_register_username_over_20(self, api):
        """username 超 20 字符 → code=1003（BUG-001 修复后行为）"""
        res = api.register("a" * 21, "123456")
        assert res["code"] == 1003

    def test_register_password_over_20(self, api):
        """password 超 20 字符 → code=1003"""
        res = api.register(make_username(), "a" * 21)
        assert res["code"] == 1003

    def test_register_duplicate_username(self, api):
        """重复用户名注册 → code=1001 用户名已存在"""
        username = make_username()
        assert api.register(username, "123456")["code"] == 0   # 第一次成功
        res = api.register(username, "123456")                  # 第二次重名
        assert res["code"] == 1001


@allure.feature("用户模块")
@allure.story("登录")
class TestLogin:
    """登录接口 /login"""

    def test_login_success(self, api):
        """正确用户名密码 → code=0，密码返回脱敏"""
        username = make_username()
        api.register(username, "123456")
        res = api.login(username, "123456")
        assert res["code"] == 0
        assert res["data"]["username"] == username
        assert res["data"]["password"] == ""

    def test_login_wrong_password(self, api):
        """密码错误 → code=1002"""
        username = make_username()
        api.register(username, "123456")
        res = api.login(username, "abc123")
        assert res["code"] == 1002

    def test_login_not_exist_user(self, api):
        """用户不存在 → code=1002"""
        res = api.login(make_username(), "123456")
        assert res["code"] == 1002

    def test_login_missing_username(self, api):
        """缺用户名 → code=1003"""
        res = api.login("", "123456")
        assert res["code"] == 1003

    def test_login_missing_password(self, api):
        """缺密码 → code=1003"""
        res = api.login(make_username(), "")
        assert res["code"] == 1003


@allure.feature("用户模块")
@allure.story("用户信息")
class TestUserInfo:
    """获取用户信息接口 /userInfo"""

    def test_userinfo_logged_in(self, new_user):
        """已登录 → code=0，返回当前用户名"""
        client, username, password, user_id = new_user
        res = client.get_user_info()
        assert res["code"] == 0
        assert res["data"]["username"] == username

    def test_userinfo_not_login(self, api):
        """未登录 → code=401"""
        res = api.get_user_info()
        assert res["code"] == 401
