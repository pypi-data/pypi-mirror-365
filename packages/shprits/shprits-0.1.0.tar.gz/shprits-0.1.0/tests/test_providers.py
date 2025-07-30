import pytest

from shprits.core.container import Container
from shprits.core.entities import Depends
from shprits.decorators import provide


def test_sync_generator_provider():
    class Gen(Container):
        @provide()
        def res(self) -> str:
            yield "ok"

    c = Gen()
    inject = c.injector()

    @inject
    def handler(res: Depends[str]):
        return res

    assert handler() == "ok"


@pytest.mark.asyncio
async def test_async_generator_provider():
    class Gen(Container):
        @provide()
        async def res(self) -> str:
            yield "async_ok"

    c = Gen()
    inject = c.injector()

    @inject
    async def handler(res: Depends[str]):
        return res

    assert await handler() == "async_ok"
