#!/usr/bin/env python3.9
# coding:utf-8
# Copyright (C) 2025 All rights reserved.
# FILENAME:    ~~/tests/litestar/__init__.py
# VERSION:     0.0.3
# CREATED:     2025-07-24 16:48
# AUTHOR:      Sitt Guruvanich <aekazitt+github@gmail.com>
# DESCRIPTION: https://www.w3docs.com/snippets/python/what-is-init-py-for.html
#
# HISTORY:
# *************************************************************
"""
Tests for Etiquette plugin for Litestar TestClient fixture
"""

### Standard packages ###
from asyncio import Lock, sleep
from asyncio.exceptions import CancelledError
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from typing import AsyncGenerator, Final

### Third-party packages ###
from litestar import Litestar
from litestar.di import Provide
from litestar.handlers.http_handlers import get
from litestar.testing import TestClient
from pytest import fixture

### Local modules ###
from etiquette import Decorum, Etiquette


@fixture
def test_client() -> AsyncGenerator[TestClient, None]:
  """
  Sets up a FastAPI TestClient wrapped around an application implementing both
  SafeCounter and UnsafeCounter increment call by Decorum

  ---
  :return: test client fixture used for local testing
  :rtype: fastapi.testclient.TestClient
  """

  @asynccontextmanager
  async def lifespan(_: Litestar) -> AsyncGenerator[None, None]:
    Etiquette.initiate(max_concurrent_tasks=8)
    yield
    await Etiquette.release()

  @dataclass
  class UnsafeCounter:
    """Counter without thread safety - demonstrates race condition"""

    count: int = 0

    async def add(self, amount: int) -> None:
      await sleep(0.01)
      self.count += 1

    @property
    async def current(self) -> int:
      return self.count

    async def increment(self) -> None:
      await sleep(0.01)
      self.count += 1

  @dataclass
  class SafeCounter:
    """Counter with thread safety - fixes race condition"""

    count: int = 0
    _lock: Lock = field(default_factory=Lock, init=False)

    async def add(self, amount: int) -> None:
      async with self._lock:
        await sleep(0.001)
        self.count += amount

    @property
    async def current(self) -> int:
      async with self._lock:
        return self.count

    async def increment(self) -> None:
      async with self._lock:
        current = self.count
        await sleep(0.001)
        self.count = current + 1

  safe_counter: SafeCounter = SafeCounter()

  @get("/safe-counter")
  async def increment_safe_counter(decorum: Decorum, amount: None | int = None) -> int:
    if amount is not None:
      await decorum.add_task(safe_counter.add, amount)
    else:
      await decorum.add_task(safe_counter.increment)
    return await safe_counter.current

  @get("/safe-counter/{amount:int}")
  async def add_amount_to_safe_counter(amount: int, decorum: Decorum) -> int:
    await decorum.add_task(safe_counter.add, amount=amount)
    return await safe_counter.current

  @dataclass
  class SureFailCounter:
    """Counter that does not count, just fails"""

    async def increment(self) -> int:
      raise CancelledError

  sure_fail_counter: SureFailCounter = SureFailCounter()

  @get("/sure-fail-counter")
  async def increment_sure_fail_counter(decorum: Decorum) -> int:
    await decorum.add_task(sure_fail_counter.increment)
    return 0

  unsafe_counter: UnsafeCounter = UnsafeCounter()

  @get("/unsafe-counter")
  async def increment_unsafe_counter(decorum: Decorum, amount: None | int = None) -> int:
    if amount is not None:
      await decorum.add_task(unsafe_counter.add, amount)
    else:
      await decorum.add_task(unsafe_counter.increment)
    return await unsafe_counter.current

  @get("/unsafe-counter/{amount:int}")
  async def add_amount_to_unsafe_counter(amount: int, decorum: Decorum) -> int:
    await decorum.add_task(unsafe_counter.add, amount=amount)
    return await safe_counter.current

  app: Litestar = Litestar(
    lifespan=[lifespan],
    dependencies={"decorum": Provide(Decorum, sync_to_thread=True)},
    route_handlers=[
      add_amount_to_safe_counter,
      add_amount_to_unsafe_counter,
      increment_safe_counter,
      increment_sure_fail_counter,
      increment_unsafe_counter,
    ],
  )

  with TestClient(app) as client:
    yield client


__all__: Final[tuple[str, ...]] = ("test_client",)
