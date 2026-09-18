# -*- coding: utf-8 -*-
"""WebSocket 模块测试：发送、转发、落库 + BUG-004/BUG-005 修复后的回归用例。"""
import json
import time

import allure
import pytest
import websocket
from chatroom_test.helpers import db


WS_URL = "ws://localhost:8080/WebSocketMessage"


def connect_ws(client, timeout=3):
    """用 client 的登录态（JSESSIONID）建立 WebSocket 连接。

    后端握手时通过 HttpSessionHandshakeInterceptor 把登录用户
    复制进 WS 连接，所以只要 Cookie 带上 JSESSIONID 就能"以该用户身份"连上。
    """
    cookie = client.s.cookies.get("JSESSIONID")
    return websocket.create_connection(
        WS_URL, header=[f"Cookie: JSESSIONID={cookie}"], timeout=timeout)


def build_msg(session_id, content):
    """构造前端发消息用的 JSON 报文。"""
    return json.dumps({"type": "message", "sessionId": session_id, "content": content})


@pytest.fixture
def ws_env(two_friends):
    """准备：A、B 是好友 + 建好会话 + 两人都已连上 WS。

    返回 (a, b, session_id, ws_a, ws_b)。
    """
    a, b = two_friends["a"], two_friends["b"]
    session_id = a[0].create_session(b[3])["data"]["sessionId"]
    ws_b = connect_ws(b[0])   # B 必须先上线，A 发消息时才能收到转发
    ws_a = connect_ws(a[0])
    yield a, b, session_id, ws_a, ws_b
    ws_a.close()              # 用例结束后关闭连接（无论用例是否失败都会执行）
    ws_b.close()


@allure.feature("消息模块")
@allure.story("WebSocket 发送")
class TestWebSocketSend:
    """WebSocket 发送消息"""

    def test_send_echo_and_broadcast(self, ws_env):
        """A 发消息 → A 收到自己回显，B 也收到转发"""
        a, b, session_id, ws_a, ws_b = ws_env
        ws_a.send(build_msg(session_id, "hello ws"))
        echo = json.loads(ws_a.recv())       # 自己的回显
        assert echo["type"] == "message"
        assert echo["fromId"] == a[3]
        assert echo["content"] == "hello ws"
        got = json.loads(ws_b.recv())        # B 收到的转发
        assert got["type"] == "message"
        assert got["content"] == "hello ws"
        assert got["fromName"] == a[1]

    def test_send_saved_to_history(self, ws_env):
        """WS 发消息后，HTTP /message 能查到历史（落库验证）"""
        a, b, session_id, ws_a, ws_b = ws_env
        ws_a.send(build_msg(session_id, "历史消息验证"))
        ws_a.recv()                          # 吃掉回显，保持连接干净
        time.sleep(0.5)                      # 后端"先转发回显、后落库"，等半秒再查历史
        history = a[0].get_messages(session_id)

        assert history["code"] == 0
        assert "历史消息验证" in [m["content"] for m in history["data"]]

    def test_invalid_session_id(self, ws_env):
        """发无效 sessionId → 只收到 error 提示，会话内好友收不到（BUG-004 回归）"""
        a, b, session_id, ws_a, ws_b = ws_env
        ws_a.send(build_msg(999999, "幽灵消息"))
        err = json.loads(ws_a.recv())
        assert err["type"] == "error"
        assert "无权" in err["content"]
        # B 收不到 = 消息没被转发（recv 超时抛异常 = 断言通过）
        with pytest.raises(websocket.WebSocketTimeoutException):
            ws_b.recv()
        # 数据库侧证：sessionId=999999 的"幽灵消息"没有落库（BUG-004 修复验证）
        assert db.count("SELECT COUNT(*) FROM message WHERE sessionId = %s", (999999,)) == 0


    def test_oversize_content(self, ws_env):
        """content 超 2048 → 收到 error，连接不断、还能正常收发（BUG-005 回归）"""
        a, b, session_id, ws_a, ws_b = ws_env
        ws_a.send(build_msg(session_id, "a" * 2049))
        err = json.loads(ws_a.recv())
        assert err["type"] == "error"
        assert "2048" in err["content"]
        # 修复前这里连接会断（1011），修复后应能继续发正常消息
        ws_a.send(build_msg(session_id, "连接没断"))
        assert json.loads(ws_a.recv())["content"] == "连接没断"
        # 数据库侧证：超长消息没有落库（BUG-005 修复验证）
        # 注意：本用例第 2 步发的"连接没断"是正常消息、会落库，所以只断言"超长的没落库"
        assert db.count(
            "SELECT COUNT(*) FROM message WHERE sessionId = %s AND CHAR_LENGTH(content) > 2048",
            (session_id,)) == 0



    def test_not_login_send_no_response(self):
        """未登录连接（不带 Cookie）发消息 → 无任何回显（后端静默丢弃）"""
        ws = websocket.create_connection(WS_URL, timeout=3)
        ws.send(build_msg(1, "未登录消息"))
        with pytest.raises(websocket.WebSocketTimeoutException):
            ws.recv()        # 3 秒内没回应 = 后端静默丢弃，不报错
        ws.close()
