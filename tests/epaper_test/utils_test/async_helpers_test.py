from concurrent.futures import ProcessPoolExecutor
import pytest

from epaper.utils.async_wrapper import (
    SyncToAsyncWrapper,
    AsyncToSyncWrapper,
    run_sync_method_in_async_pool,
    run_async_method_sync,
)


class ExampleSync:
    def __init__(self):
        self.field = 15

    def add(self, x, y):
        return x + y

    def bar(self):
        return "bar"

    def mult(self, x, y):
        return x * y

    def exn(self):
        raise ValueError("Heyo")

    async def div(self, x, y):
        return x / y


class ExampleAsync:
    def __init__(self):
        self.field = 20

    async def foo(self):
        return 2

    async def bar(self):
        return 3

    async def add(self, v):
        x = await self.foo()
        y = await self.bar()
        return x + y + v

    async def exn(self):
        raise ValueError("Heyo")

    def s(self):
        return 4


def test_run_async_method_sync():
    e = ExampleAsync()

    result = run_async_method_sync(e.add, 1)
    assert result == 6


def test_AsyncToSyncWrapper():
    foo = ExampleAsync()
    wrapped = AsyncToSyncWrapper(foo)
    assert wrapped.foo() == 2
    assert wrapped.bar() == 3
    assert wrapped.add(3) == 8
    assert wrapped.s() == 4
    assert wrapped.field == 20
    with pytest.raises(ValueError):
        wrapped.exn()


@pytest.mark.asyncio
async def test_run_sync_method_in_async_pool():
    pool = ProcessPoolExecutor(max_workers=1)
    e = ExampleSync()
    result = await run_sync_method_in_async_pool(pool, e.mult, 3, 4)
    assert result == 12


@pytest.mark.asyncio
async def test_SyncToAsyncWrapper():
    foo = ExampleSync()
    wrapped = SyncToAsyncWrapper(foo)
    x = await wrapped.add(1, 2)
    assert x == 3
    bar = await wrapped.bar()
    assert bar == "bar"
    y = await wrapped.mult(3, 4)
    assert y == 12
    y = await wrapped.mult(3, 5)
    assert y == 15
    v = await wrapped.field
    assert v == 15
    v = await wrapped.div(10, 2)
    assert v == 5
    with pytest.raises(ValueError):
        await wrapped.exn()
