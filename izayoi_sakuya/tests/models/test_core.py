import unittest
import random

from tortoise import Tortoise
from tortoise.fields import CharField

from ...models.core import SoftDeleteModel


class TestCoreModel(SoftDeleteModel):
    temp_column = CharField(255)


class TestCaseForModelCore(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        await Tortoise.init(
            db_url="sqlite://db.sqlite3",
            modules={"models": ["izayoi_sakuya.tests.models.test_core"]}
        )
        await Tortoise.generate_schemas()

    async def test_save_and_erasure(self) -> None:
        current_model = TestCoreModel(temp_column="save_and_erasure")
        await current_model.save()
        assert current_model.temp_column == "save_and_erasure"

        await current_model.erasure()
        assert await TestCoreModel.whole() == []

    async def test_bulk_create_and_queryset_erasure(self) -> None:
        await TestCoreModel.bulk_create(
            [TestCoreModel(temp_column=str(random.random())) for _ in range(5)]
        )
        assert (await TestCoreModel.whole()) != []
        await TestCoreModel.whole().erasure()
        assert (await TestCoreModel.whole()) == []

    async def test_create_and_soft_delete(self) -> None:
        current_model = await TestCoreModel.create(
            temp_column="create_and_soft_delete"
        )
        assert current_model.temp_column == "create_and_soft_delete"
        assert current_model.deleted_time is None

        await current_model.delete()
        assert (await TestCoreModel.all() == []) and \
            (await TestCoreModel.whole() != [])

    async def test_queryset_delete(self) -> None:
        await TestCoreModel.bulk_create(
            [TestCoreModel(temp_column=str(random.random())) for _ in range(5)]
        )
        assert await TestCoreModel.all() != []
        await TestCoreModel.all().delete()
        assert await TestCoreModel.all() == [] and \
            await TestCoreModel.whole() != []

    async def asyncTearDown(self) -> None:
        await TestCoreModel.whole().erasure()
        await Tortoise.close_connections()
