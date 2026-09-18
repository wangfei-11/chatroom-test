# -*- coding: utf-8 -*-
"""消息模块测试（HTTP）：历史消息查询 /message（参数 sessionId）。"""
import allure


@allure.feature("消息模块")
@allure.story("历史消息")
class TestGetMessage:
    """查询历史消息 /message"""

    def test_history_empty(self, two_friends):
        """新会话无消息 → code=0，列表为空"""
        a, b = two_friends["a"], two_friends["b"]
        session_id = a[0].create_session(b[3])["data"]["sessionId"]
        res = a[0].get_messages(session_id)
        assert res["code"] == 0
        assert res["data"] == []

    def test_no_permission_for_third_user(self, two_friends, new_user):
        """会话外用户查别人会话 → code=1003 无权查看（越权场景）"""
        a, b = two_friends["a"], two_friends["b"]
        session_id = a[0].create_session(b[3])["data"]["sessionId"]
        third_client = new_user[0]          # 第三个无关用户
        assert third_client.get_messages(session_id)["code"] == 1003

    def test_not_exist_session(self, new_user):
        """不存在的会话 → code=1003"""
        client, username, password, user_id = new_user
        assert client.get_messages(999999)["code"] == 1003

    def test_missing_session_id(self, new_user):
        """缺 sessionId → code=1003"""
        client, username, password, user_id = new_user
        assert client._get("/message")["code"] == 1003

    def test_not_login(self, api):
        """未登录 → code=401"""
        assert api.get_messages(1)["code"] == 401
