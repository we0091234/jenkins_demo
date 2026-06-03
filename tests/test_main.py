import asyncio

import allure
from httpx import ASGITransport, AsyncClient, Response
from main import app


async def get(path: str) -> Response:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        return await client.get(path)


@allure.feature("首页")
@allure.story("服务状态展示")
@allure.title("首页展示服务在线状态")
def test_home_page_displays_service_status() -> None:
    response = asyncio.run(get("/"))

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/html")
    assert "Jenkins Demo" in response.text
    assert "Service Online" in response.text


@allure.feature("首页")
@allure.story("页面结构")
@allure.title("首页包含基础 HTML 结构")
def test_home_page_has_expected_html_structure() -> None:
    response = asyncio.run(get("/"))

    assert "<!DOCTYPE html>" in response.text
    assert '<html lang="zh-CN">' in response.text
    assert '<meta name="viewport"' in response.text
    assert "<main>" in response.text


@allure.feature("首页")
@allure.story("页面文案")
@allure.title("首页展示中文介绍文案")
def test_home_page_displays_chinese_intro_text() -> None:
    response = asyncio.run(get("/"))

    assert response.status_code == 200
    assert "FastAPI 你好 jenkins" in response.text


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
