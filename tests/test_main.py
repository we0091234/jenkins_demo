import asyncio

from httpx import ASGITransport, AsyncClient, Response
from main import app


async def get(path: str) -> Response:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        return await client.get(path)


def test_home_page_displays_service_status() -> None:
    response = asyncio.run(get("/"))

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/html")
    assert "Jenkins Demo" in response.text
    assert "Service Online" in response.text


def test_health_check_returns_ok() -> None:
    response = asyncio.run(get("/health"))

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
