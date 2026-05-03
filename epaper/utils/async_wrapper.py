import asyncio
import inspect
from concurrent.futures import Executor, ProcessPoolExecutor, ThreadPoolExecutor
from dataclasses import dataclass
from functools import partial
from typing import Literal


def run_async_method_sync(m, *args, **kwargs):
    return asyncio.run(m(*args, **kwargs))


async def run_sync_method_in_async_pool(pool, method, *args, **kwargs):
    loop = asyncio.get_running_loop()
    ret = await loop.run_in_executor(pool, method, *args, **kwargs)
    return ret


async def lift_value_async[T](v: T) -> T:
    return v


type PoolMode = Literal["thread", "process"]


@dataclass
class PoolConfig:
    pool_mode: PoolMode
    max_workers: int

    @staticmethod
    def default():
        return PoolConfig(pool_mode="process", max_workers=1)

    def make_pool(self) -> Executor:
        match self.pool_mode:
            case "process":
                return ProcessPoolExecutor(max_workers=self.max_workers)
            case "thread":
                return ThreadPoolExecutor(max_workers=self.max_workers)


class SyncToAsyncWrapper[T]:
    """
    Wraps an object with synchronous methods and runs them in another thread or process while returning Futures to be awaited on in the main event loop
    """

    _pool: Executor
    _owns_pool: bool

    def __init__(
        self,
        obj: T,
        pool: Executor | PoolConfig | None = None,
    ):
        self._obj = obj
        p = pool or PoolConfig.default()
        match p:
            case Executor():
                self._pool = p
                self._owns_pool = False
            case PoolConfig():
                self._pool = p.make_pool()
                self._owns_pool = True

    def __del__(self):
        if self._owns_pool:
            self._pool.shutdown(wait=False, cancel_futures=True)

    def __getattr__(self, name):
        method = getattr(self._obj, name)
        if not method:
            raise AttributeError(
                f"Could not find {name} on object {self._obj} of type {type(self._obj)}"
            )
        if not callable(method):
            return lift_value_async(method)
        if inspect.iscoroutinefunction(method):
            return method

        return partial(run_sync_method_in_async_pool, self._pool, method)


class AsyncToSyncWrapper[T]:
    """
    Wraps an object with async methods and runs them in a synchronous manner.
    """

    def __init__(self, obj: T) -> None:
        self._inner = obj

    def __getattr__(self, name):
        method = getattr(self._inner, name)
        if not method:
            raise AttributeError(
                f"Could not find {name} on object {self._inner} of type {type(self._inner)}"
            )
        if not callable(method):
            return method
        if not inspect.iscoroutinefunction(method):
            return method
        else:
            return partial(run_async_method_sync, method)
