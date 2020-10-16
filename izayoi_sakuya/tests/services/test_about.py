import unittest

from httpx import AsyncClient

from ...factory import generate_app


class TestCaseForAbout(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        app = generate_app()
        self.client = AsyncClient(app=app, base_url="http://127.0.0.1")

    async def test_request_ok(self):
        response = await self.client.get("/about_us")
        assert response.status_code == 200

    async def asyncTearDown(self) -> None:
        await self.client.aclose()
