# -*- coding: utf-8 -*-
"""会话模块测试：会话列表 /sessionList、创建会话 /Session。"""
import allure


@allure.feature("会话模块")
@allure.story("会话列表")
class TestSessionList:
    """会话列表 /sessionList"""

    def test_session_list_empty(self, new_user):
        """新用户无会话 → code=0，列表为空"""
        client, username, password, user_id = new_user
        res = client.get_session_list()
        assert res["code"] == 0
        assert res["data"] == []

    def test_session_list_not_login(self, api):
        """未登录 → code=401"""
        assert api.get_session_list()["code"] == 401


@allure.feature("会话模块")
@allure.story("创建会话")
class TestCreateSession:
    """创建会话 /Session（参数 toUserId）"""

    def test_create_success(self, two_friends):
        """好友间建会话 → code=0，返回 sessionId>0，双方会话列表都出现该会话"""
        a, b = two_friends["a"], two_friends["b"]
        res = a[0].create_session(b[3])
        assert res["code"] == 0
        session_id = res["data"]["sessionId"]
        assert session_id > 0
        assert any(s["sessionId"] == session_id for s in a[0].get_session_list()["data"])
        assert any(s["sessionId"] == session_id for s in b[0].get_session_list()["data"])

    def test_create_returns_existing_session(self, two_friends):
        """重复建会话 → code=0，返回同一个 sessionId（幂等，不产生新会话）"""
        a, b = two_friends["a"], two_friends["b"]
        first = a[0].create_session(b[3])
        second = a[0].create_session(b[3])
        assert first["code"] == 0 and second["code"] == 0
        assert first["data"]["sessionId"] == second["data"]["sessionId"]

    def test_create_with_self(self, new_user):
        """给自己建会话 → code=1003"""
        client, username, password, user_id = new_user
        assert client.create_session(user_id)["code"] == 1003

    def test_create_with_nonexistent_user(self, new_user):
        """给不存在的用户建会话 → code=1003"""
        client, username, password, user_id = new_user
        assert client.create_session(999999)["code"] == 1003

    def test_create_missing_to_user_id(self, new_user):
        """缺 toUserId → code=1003"""
        client, username, password, user_id = new_user
        assert client._post("/Session", {})["code"] == 1003

    def test_create_with_non_friend(self, two_users):
        """非好友建会话 → code=1003（非好友不能创建会话）"""
        a, b = two_users["a"], two_users["b"]
        assert a[0].create_session(b[3])["code"] == 1003

    def test_create_not_login(self, api):
        """未登录 → code=401"""
        assert api.create_session(1)["code"] == 401
