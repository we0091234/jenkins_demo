import asyncio
from unittest.mock import patch

import allure
from httpx import ASGITransport, AsyncClient, Response

from main import LOGIN_LOCK_SECONDS, app, failed_login_attempts, sessions, users


async def get(path: str, follow_redirects: bool = True) -> Response:
    transport = ASGITransport(app=app)
    async with AsyncClient(
        transport=transport,
        base_url="http://test",
        follow_redirects=follow_redirects,
    ) as client:
        return await client.get(path)


async def post(path: str, data: dict[str, str], follow_redirects: bool = True) -> Response:
    transport = ASGITransport(app=app)
    async with AsyncClient(
        transport=transport,
        base_url="http://test",
        follow_redirects=follow_redirects,
    ) as client:
        return await client.post(path, data=data)


def setup_function() -> None:
    users.clear()
    sessions.clear()
    failed_login_attempts.clear()


@allure.feature("首页")
@allure.story("访客态展示")
@allure.title("未登录时首页显示登录入口和注册链接")
def test_home_page_displays_login_page_for_guest() -> None:
    response = asyncio.run(get("/"))

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/html")
    assert "Jenkins Demo" in response.text
    assert "<h2>登录</h2>" in response.text
    assert "立即登录" in response.text
    assert "没有账号？" in response.text
    assert 'href="/register"' in response.text


@allure.feature("注册")
@allure.story("注册页展示")
@allure.title("注册页显示注册表单和登录链接")
def test_register_page_displays_register_form() -> None:
    response = asyncio.run(get("/register"))

    assert response.status_code == 200
    assert "<h2>注册</h2>" in response.text
    assert "立即注册" in response.text
    assert "已有账号？" in response.text
    assert 'href="/"' in response.text


@allure.feature("注册")
@allure.story("新用户创建")
@allure.title("注册成功后返回登录提示")
def test_register_creates_user_and_shows_success_message() -> None:
    response = asyncio.run(post("/register", {"username": "alice", "password": "123456"}))

    assert response.status_code == 200
    assert users["alice"] == "123456"
    assert "注册成功，请登录" in response.text
    assert "<h2>登录</h2>" in response.text


@allure.feature("登录")
@allure.story("成功登录")
@allure.title("登录成功后显示欢迎文案")
def test_login_displays_welcome_message_after_success() -> None:
    users["alice"] = "123456"

    response = asyncio.run(post("/login", {"username": "alice", "password": "123456"}))

    assert response.status_code == 200
    assert "欢迎来到 jenkis 的大家庭" in response.text
    assert "alice" in response.text


@allure.feature("登录")
@allure.story("失败处理")
@allure.title("错误密码时返回失败提示")
def test_login_shows_error_for_invalid_credentials() -> None:
    users["alice"] = "123456"

    response = asyncio.run(post("/login", {"username": "alice", "password": "wrong"}))

    assert response.status_code == 200
    assert "用户名或密码错误" in response.text


@allure.feature("登录")
@allure.story("失败限制")
@allure.title("同一用户名输错三次后被锁定十分钟")
def test_login_locks_user_after_three_failed_attempts() -> None:
    users["alice"] = "123456"

    with patch("main.current_time", return_value=1000.0):
        first_response = asyncio.run(post("/login", {"username": "alice", "password": "wrong-1"}))
        second_response = asyncio.run(post("/login", {"username": "alice", "password": "wrong-2"}))
        third_response = asyncio.run(post("/login", {"username": "alice", "password": "wrong-3"}))

    assert "用户名或密码错误" in first_response.text
    assert "用户名或密码错误" in second_response.text
    assert "密码输入错误三次，请 10 分钟后再试" in third_response.text
    assert failed_login_attempts["alice"]["locked_until"] == 1000.0 + LOGIN_LOCK_SECONDS


@allure.feature("登录")
@allure.story("失败限制")
@allure.title("锁定十分钟后可以重新登录")
def test_login_allows_retry_after_lock_window_expires() -> None:
    users["alice"] = "123456"
    failed_login_attempts["alice"] = {"count": 0, "locked_until": 1000.0 + LOGIN_LOCK_SECONDS}

    with patch("main.current_time", return_value=1000.0 + LOGIN_LOCK_SECONDS - 1):
        locked_response = asyncio.run(post("/login", {"username": "alice", "password": "123456"}))

    with patch("main.current_time", return_value=1000.0 + LOGIN_LOCK_SECONDS + 1):
        unlocked_response = asyncio.run(post("/login", {"username": "alice", "password": "123456"}))

    assert "密码输入错误三次，请 10 分钟后再试" in locked_response.text
    assert "欢迎来到 jenkis 的大家庭" in unlocked_response.text


@allure.feature("健康检查")
@allure.story("接口状态")
@allure.title("健康检查返回 ok")
def test_health_check_returns_ok() -> None:
    response = asyncio.run(get("/health"))

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@allure.feature("健康检查")
@allure.story("响应格式")
@allure.title("健康检查返回 JSON 类型")
def test_health_check_returns_json_content_type() -> None:
    response = asyncio.run(get("/health"))

    assert response.headers["content-type"].startswith("application/json")


@allure.feature("接口文档")
@allure.story("OpenAPI 元信息")
@allure.title("OpenAPI 文档包含应用标题")
def test_openapi_schema_contains_app_title() -> None:
    response = asyncio.run(get("/openapi.json"))

    assert response.status_code == 200
    assert response.json()["info"]["title"] == "Jenkins Demo API"


@allure.feature("异常路径")
@allure.story("404 处理")
@allure.title("未知路由返回 404")
def test_unknown_route_returns_404() -> None:
    response = asyncio.run(get("/not-found"))

    assert response.status_code == 404
    assert response.json() == {"detail": "Not Found"}
