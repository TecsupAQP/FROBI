from httpx import AsyncClient

FRONT_ORIGIN = "http://front.test"  # same origin the settings fixture allows


async def test_preflight_from_the_front_origin_is_allowed(client: AsyncClient) -> None:
    response = await client.options(
        "/api/v1/health",
        headers={
            "Origin": FRONT_ORIGIN,
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "authorization,content-type",
        },
    )

    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == FRONT_ORIGIN


async def test_unknown_origin_gets_no_cors_header(client: AsyncClient) -> None:
    response = await client.options(
        "/api/v1/health",
        headers={"Origin": "http://evil.test", "Access-Control-Request-Method": "GET"},
    )

    assert "access-control-allow-origin" not in response.headers
