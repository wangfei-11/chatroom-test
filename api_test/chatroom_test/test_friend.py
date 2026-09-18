# -*- coding: utf-8 -*-
"""好友模块测试：好友列表、发送/接受/拒绝好友请求、待处理列表、搜索用户。"""
import allure


@allure.feature("好友模块")
@allure.story("好友列表")
class TestFriendList:
    """好友列表 /friendList"""

    def test_friend_list_empty(self, new_user):
        """新用户无好友 → code=0，列表为空"""
        client, username, password, user_id = new_user
        res = client.get_friend_list()
        assert res["code"] == 0
        assert res["data"] == []

    def test_friend_list_not_login(self, api):
        """未登录 → code=401"""
        assert api.get_friend_list()["code"] == 401


@allure.feature("好友模块")
@allure.story("发送好友请求")
class TestSendFriendRequest:
    """发送好友请求 /sendFriendRequest"""

    def test_send_success(self, two_users):
        """正常发送 → code=0，接收方待处理列表出现该请求"""
        a, b = two_users["a"], two_users["b"]
        res = a[0].send_friend_request(b[3], "你好，加个好友")
        assert res["code"] == 0
        # 接收方 B 的待处理列表里应有一条 fromUserId == A 的请求
        pending = b[0].get_pending_requests()
        assert pending["code"] == 0
        assert a[3] in [r["fromUserId"] for r in pending["data"]]

    def test_send_to_self(self, new_user):
        """给自己发 → code=1003"""
        client, username, password, user_id = new_user
        assert client.send_friend_request(user_id)["code"] == 1003

    def test_send_to_nonexistent_user(self, new_user):
        """给不存在的用户发 → code=1003（缺陷 BUG-002 修复后行为）"""
        client, username, password, user_id = new_user
        assert client.send_friend_request(999999)["code"] == 1003

    def test_send_duplicate(self, two_users):
        """已有待处理请求时重复发送 → code=1003"""
        a, b = two_users["a"], two_users["b"]
        assert a[0].send_friend_request(b[3])["code"] == 0
        assert a[0].send_friend_request(b[3])["code"] == 1003

    def test_send_missing_to_user_id(self, new_user):
        """缺 toUserId 参数 → code=1003（用 _post 绕过封装模拟缺参）"""
        client, username, password, user_id = new_user
        assert client._post("/sendFriendRequest", {"requestMsg": "hi"})["code"] == 1003

    def test_send_request_msg_over_200(self, two_users):
        """requestMsg 超 200 字符 → code=1003"""
        a, b = two_users["a"], two_users["b"]
        assert a[0].send_friend_request(b[3], "a" * 201)["code"] == 1003


@allure.feature("好友模块")
@allure.story("待处理请求")
class TestPendingRequests:
    """待处理好友请求 /getPendingRequests"""

    def test_pending_not_login(self, api):
        """未登录 → code=401"""
        assert api.get_pending_requests()["code"] == 401


@allure.feature("好友模块")
@allure.story("接受/拒绝请求")
class TestAcceptAndReject:
    """接受/拒绝好友请求"""

    def _send_and_get_request_id(self, two_users):
        """准备动作：A 向 B 发请求，返回 (a, b, request_id)。"""
        a, b = two_users["a"], two_users["b"]
        a[0].send_friend_request(b[3])
        request_id = b[0].get_pending_requests()["data"][0]["id"]
        return a, b, request_id

    def test_accept_success(self, two_users):
        """B 接受 → code=0，双方好友列表互含对方"""
        a, b, request_id = self._send_and_get_request_id(two_users)
        assert b[0].accept_friend_request(request_id)["code"] == 0
        assert any(f["friendId"] == b[3] for f in a[0].get_friend_list()["data"])
        assert any(f["friendId"] == a[3] for f in b[0].get_friend_list()["data"])

    def test_reject_success(self, two_users):
        """B 拒绝 → code=0，待处理列表清空，双方不成为好友"""
        a, b, request_id = self._send_and_get_request_id(two_users)
        assert b[0].reject_friend_request(request_id)["code"] == 0
        assert b[0].get_pending_requests()["data"] == []
        assert all(f["friendId"] != b[3] for f in a[0].get_friend_list()["data"])

    def test_accept_missing_request_id(self, new_user):
        """缺 requestId → code=1003"""
        client, username, password, user_id = new_user
        assert client._post("/acceptFriendRequest", {})["code"] == 1003

    def test_accept_not_login(self, api):
        """未登录 → code=401"""
        assert api.accept_friend_request(1)["code"] == 401


@allure.feature("好友模块")
@allure.story("搜索用户")
class TestSearchUser:
    """搜索用户 /searchUser"""

    def test_search_success(self, two_users):
        """B 搜索 A 的用户名 → code=0，结果包含 A"""
        a, b = two_users["a"], two_users["b"]
        res = b[0].search_user(a[1])
        assert res["code"] == 0
        assert any(u["userId"] == a[3] for u in res["data"])

    def test_search_empty_keyword(self, new_user):
        """空关键词 → code=1003"""
        client, username, password, user_id = new_user
        assert client.search_user("")["code"] == 1003

    def test_search_not_login(self, api):
        """未登录 → code=401"""
        assert api.search_user("test")["code"] == 401
