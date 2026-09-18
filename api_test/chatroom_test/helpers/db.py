# -*- coding: utf-8 -*-
"""数据库工具：pymysql 直连 MySQL，用于数据库断言 + 清理自动化测试数据。"""
import pymysql

DB_CONFIG = {
    "host": "localhost",
    "port": 3306,
    "user": "root",
    "password": "123456",
    "database": "chatroom",
    "charset": "utf8mb4",
}


def get_conn():
    """新建一个 MySQL 连接。"""
    return pymysql.connect(**DB_CONFIG)


def query_all(sql, args=None):
    """查询，返回全部行（列表套元组）。"""
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(sql, args)
            return cur.fetchall()
    finally:
        conn.close()


def query_one(sql, args=None):
    """查询，返回第一行；没有结果返回 None。"""
    rows = query_all(sql, args)
    return rows[0] if rows else None


def count(sql, args=None):
    """执行 count(*) 查询，返回整数。"""
    return query_one(sql, args)[0]


def clean_test_data(prefix="test_"):
    """清理自动化测试数据：删除所有 test_ 前缀用户及其关联数据。

    这些表之间没有外键约束，必须按"先删依赖表、再删主表"的顺序手动清理，
    否则会留下孤儿数据（无主好友记录、幽灵消息）。
    返回删除的用户数量。
    """
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            # 1. 找出所有测试用户的 userId
            cur.execute("SELECT userId FROM user WHERE username LIKE %s", (prefix + "%",))
            ids = [row[0] for row in cur.fetchall()]
            if not ids:
                return 0
            ph = ",".join(["%s"] * len(ids))      # 拼出 IN (...) 的占位符
            args = tuple(ids)

            # 2. 找出这些用户参与的会话（必须在删成员之前先查出来）
            cur.execute(f"SELECT sessionId FROM message_session_user WHERE userId IN ({ph})", args)
            session_ids = [row[0] for row in cur.fetchall()]

            # 3. 删消息：测试用户发的 + 测试会话里的
            cur.execute(f"DELETE FROM message WHERE fromId IN ({ph})", args)
            if session_ids:
                sph = ",".join(["%s"] * len(session_ids))
                cur.execute(f"DELETE FROM message WHERE sessionId IN ({sph})", tuple(session_ids))

            # 4. 删好友关系、好友请求
            cur.execute(f"DELETE FROM friend WHERE userId IN ({ph}) OR friendId IN ({ph})", args + args)
            cur.execute(
                f"DELETE FROM friend_request WHERE fromUserId IN ({ph}) OR toUserId IN ({ph})",
                args + args)

            # 5. 删会话成员、会话本身
            if session_ids:
                sph = ",".join(["%s"] * len(session_ids))
                cur.execute(f"DELETE FROM message_session_user WHERE sessionId IN ({sph})", tuple(session_ids))
                cur.execute(f"DELETE FROM message_session WHERE sessionId IN ({sph})", tuple(session_ids))

            # 6. 最后删用户本身
            cur.execute(f"DELETE FROM user WHERE userId IN ({ph})", args)

        conn.commit()
        return len(ids)
    finally:
        conn.close()
