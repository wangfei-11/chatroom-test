# -*- coding: utf-8 -*-
"""pytest 公共 fixture：所有测试文件共享，用的时候直接写 fixture 名当参数。"""
import time
from uuid import uuid4

import pytest

from chatroom_test.helpers.api import ApiClient


def make_username(prefix="test"):
    """生成唯一的测试用户名（时间戳+随机串），避免注册重名，不污染手测数据。

    注意：纯时间戳在同一毫秒内可能撞名（two_users 连续注册时出现过 1001），
    所以追加 10 位随机串。总长度 16，远小于 username 上限 20。
    """
    return f"{prefix}_{uuid4().hex[:10]}"



def _register_and_login():
    """注册+登录一个随机新用户，返回 (client, username, password, user_id)。"""
    client = ApiClient()
    username = make_username()
    password = "123456"

    reg = client.register(username, password)
    assert reg["code"] == 0, f"注册失败: {reg}"

    login = client.login(username, password)
    assert login["code"] == 0, f"登录失败: {login}"

    return client, username, password, login["data"]["userId"]


@pytest.fixture
def api():
    """未登录的 ApiClient：需要登录态的用例，自己调 login 即可。"""
    return ApiClient()


@pytest.fixture
def new_user():
    """注册并登录一个 test_ 前缀新用户，返回 (client, username, password, user_id)。"""
    return _register_and_login()


@pytest.fixture
def two_users():
    """注册并登录两个新用户 A、B。

    返回 {"a": (...), "b": (...)}，每个值都是 (client, username, password, user_id)。
    """
    return {"a": _register_and_login(), "b": _register_and_login()}


@pytest.fixture
def two_friends():
    """注册两个新用户并互相成为好友，返回 {"a": (...), "b": (...)}。

    会话、消息模块的用例都需要"两个好友"的基础关系，用它省去重复的加好友代码。
    """
    users = {"a": _register_and_login(), "b": _register_and_login()}
    a, b = users["a"], users["b"]
    a[0].send_friend_request(b[3])
    request_id = b[0].get_pending_requests()["data"][0]["id"]
    b[0].accept_friend_request(request_id)
    return users

@pytest.fixture(scope="session", autouse=True)
def cleanup_test_data():
    """跑完全部用例后自动清理自动化产生的 test_ 数据（session 级别只执行一次）。"""
    yield
    from chatroom_test.helpers import db
    print(f"\n[清理] 已删除 {db.clean_test_data()} 个测试用户及其关联数据")
