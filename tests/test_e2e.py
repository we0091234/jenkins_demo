import os

import allure
import httpx
import pytest


pytestmark = pytest.mark.e2e

BASE_URL = os.getenv("E2E_BASE_URL", "http://127.0.0.1:9875")


def request(path: str) -> httpx.Response:
    return httpx.get(f"{BASE_URL}{path}", timeout=5.0, trust_env=False)


@allure.feature("端到端测试")
@allure.story("真实服务访问")
@allure.title("真实服务健康检查可访问")
def test_running_service_health_check() -> None:
    response = request("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@allure.feature("端到端测试")
@allure.story("真实服务访问")
@allure.title("真实服务首页可访问")
def test_running_service_home_page() -> None:
    response = request("/")

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/html")
    assert "Jenkins Demo" in response.text
    assert "Service Online" in response.text
    assert "立即注册" in response.text
    assert "立即登录" in response.text
