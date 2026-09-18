# chatroom 网页聊天系统 — 测试作品

对基于 Spring Boot + MySQL + WebSocket 的网页聊天系统（注册 / 登录 / 搜索用户 / 好友申请 / 创建会话 / 实时收发消息）进行完整测试，覆盖**功能、接口、UI、性能**四个层面，手工与自动化结合。

## 测试体系

| 层面 | 方式 | 技术栈 | 用例数 | 结果 |
|---|---|---|---|---|
| 功能测试 | 手工（Postman + 浏览器） | Excel 用例管理 | 84 | 全部通过 |
| 接口自动化 | Python | pytest + requests + pymysql + Allure | 48 | 全部通过 |
| UI 自动化 | Java | Selenium 4.18.1 + JUnit 4 + Maven | 15 | 全部通过 |
| 性能测试 | JMeter | 登录 / 注册 / 搜索 3 个高频接口 | 并发 100~200 | 全部达标 |

## 测试结果概要

- **缺陷**：共发现 7 个（6 个已修复并回归通过，1 个轻微缺陷待修复），另 1 条体验优化建议
- **性能**：登录 200 并发平均 2ms / TPS 350；注册 100 并发平均 5ms / TPS 287；搜索 100 并发平均 1ms / TPS 229；错误率均为 0%，未出现性能劣化拐点
- 详情见 `docs/测试总结报告`

## 目录结构

```
chatroom-test/
├── docs/          测试用例（接口测试用例.xlsx、UI测试用例.xlsx）、测试总结报告
├── api_test/      pytest 接口自动化项目（测试代码 + Allure 报告）
├── ui_test/       Selenium UI 自动化项目（Maven 工程 + surefire 报告）
├── jmeter/        JMeter 压测脚本（.jmx）
└── README.md
```

## 运行说明

### 接口自动化（api_test/）

```bash
# 前置：后端 http://localhost:8080 已启动，MySQL 已启动
python -m pip install -r requirements.txt
pytest chatroom_test --alluredir=allure-results
allure serve allure-results
```

### UI 自动化（ui_test/selenium-ui-test/）

```bash
# 前置：后端已启动，本机装有 Chrome
mvn test                # 运行全部 15 条用例
mvn surefire-report:report   # 生成 HTML 报告（target/site/surefire-report.html）
```

### 性能测试（jmeter/）

用 JMeter 5.6+ 打开 `login-压测.jmx`，运行后查看汇总报告。

## 测试数据说明

自动化测试使用 `tu_` / `jm_` 前缀随机账号，不污染业务数据；压测注册接口后建议执行 `docs/` 中的清理 SQL（见测试总结报告）。
