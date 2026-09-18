# -*- coding: utf-8 -*-
"""chatroom HTTP 接口封装层：一个方法对应一个后端接口，统一返回 dict。

用法：
    client = ApiClient()          # 一个 client = 一个"登录用户"
    client.register("u1", "123456")
    client.login("u1", "123456")  # 登录后 Cookie 自动保存在 client 里
    client.get_friend_list()      # 之后所有需要登录的接口直接用
"""
import requests

BASE_URL = "http://localhost:8080"


class ApiClient:
    def __init__(self, base_url=BASE_URL):
        self.base_url = base_url
        # requests.Session 会自动保存 JSESSIONID Cookie，相当于"保持登录状态"
        self.s = requests.Session()

    # ---------- 内部：发起请求的两个公共方法 ----------
    def _get(self, path, params=None):
        r = self.s.get(self.base_url + path, params=params, timeout=10)
        return r.json()

    def _post(self, path, data=None):
        r = self.s.post(self.base_url + path, data=data, timeout=10)
        return r.json()

    # ---------- 用户模块 ----------
    def register(self, username, password):
        return self._post("/register", {"username": username, "password": password})

    def login(self, username, password):
        return self._post("/login", {"username": username, "password": password})

    def get_user_info(self):
        return self._get("/userInfo")

    # ---------- 好友模块 ----------
    def get_friend_list(self):
        return self._get("/friendList")

    def send_friend_request(self, to_user_id, request_msg=""):
        return self._post("/sendFriendRequest",
                          {"toUserId": to_user_id, "requestMsg": request_msg})

    def accept_friend_request(self, request_id):
        return self._post("/acceptFriendRequest", {"requestId": request_id})

    def reject_friend_request(self, request_id):
        return self._post("/rejectFriendRequest", {"requestId": request_id})

    def get_pending_requests(self):
        return self._get("/getPendingRequests")

    def search_user(self, keyword):
        return self._get("/searchUser", {"keyword": keyword})

    # ---------- 会话模块 ----------
    def get_session_list(self):
        return self._get("/sessionList")

    def create_session(self, to_user_id):
        return self._post("/Session", {"toUserId": to_user_id})

    # ---------- 消息模块 ----------
    def get_messages(self, session_id):
        return self._get("/message", {"sessionId": session_id})
