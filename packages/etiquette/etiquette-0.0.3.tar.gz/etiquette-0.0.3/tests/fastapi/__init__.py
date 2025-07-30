#!/usr/bin/env python3.9
# coding:utf-8
# Copyright (C) 2025 All rights reserved.
# FILENAME:    ~~/tests/fastapi/__init__.py
# VERSION:     0.0.3
# CREATED:     2025-07-24 16:48
# AUTHOR:      Sitt Guruvanich <aekazitt+github@gmail.com>
# DESCRIPTION: https://www.w3docs.com/snippets/python/what-is-init-py-for.html
#
# HISTORY:
# *************************************************************
"""
Tests for Etiquette plugin for FastAPI TestClient fixture
"""

### Standard packages ###
from asyncio import Lock, sleep
from asyncio.exceptions import CancelledError
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from typing import Annotated, AsyncGenerator, Final

### Third-party packages ###
from fastapi import FastAPI
from fastapi.param_functions import Depends
from fastapi.testclient import TestClient
from pytest import fixture
from starlette.requests import Request
from starlette.responses import JSONResponse

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
  async def lifespan(_: FastAPI) -> AsyncGenerator[None, None]:
    Etiquette.initiate(max_concurrent_tasks=8)
    yield
    await Etiquette.release()

  app = FastAPI(lifespan=lifespan)

  @dataclass
  class UnsafeCounter:
    """Counter without thread safety - demonstrates race condition"""

    count: int = 0

    async def add(self, amount: int) -> None:
      await sleep(0.01)
      self.count += amount

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
        await sleep(0.001)
        self.count += 1

  safe_counter: SafeCounter = SafeCounter()

  @app.get("/safe-counter")
  async def increment_safe_counter(
    decorum: Annotated[Decorum, Depends(Decorum)],
    amount: None | int = None,
  ) -> int:
    if amount is not None:
      await decorum.add_task(safe_counter.add, amount)
    else:
      await decorum.add_task(safe_counter.increment)
    return await safe_counter.current

  @app.get("/safe-counter/{amount}")
  async def add_amount_to_safe_counter(
    amount: int, decorum: Annotated[Decorum, Depends(Decorum)]
  ) -> int:
    await decorum.add_task(safe_counter.add, amount=amount)
    return await safe_counter.current

  @dataclass
  class SureFailCounter:
    """Counter that does not count, just fails"""

    async def increment(self) -> int:
      raise CancelledError

  sure_fail_counter: SureFailCounter = SureFailCounter()

  @app.get("/sure-fail-counter")
  async def increment_sure_fail_counter(decorum: Annotated[Decorum, Depends(Decorum)]) -> int:
    await decorum.add_task(sure_fail_counter.increment)
    return 0

  unsafe_counter: UnsafeCounter = UnsafeCounter()

  @app.get("/unsafe-counter")
  async def increment_unsafe_counter(
    decorum: Annotated[Decorum, Depends(Decorum)],
    amount: None | int = None,
  ) -> int:
    if amount is not None:
      await decorum.add_task(unsafe_counter.add, amount)
    else:
      await decorum.add_task(unsafe_counter.increment)
    return await unsafe_counter.current

  @app.get("/unsafe-counter/{amount}")
  async def add_amount_to_unsafe_counter(
    amount: int, decorum: Annotated[Decorum, Depends(Decorum)]
  ) -> int:
    await decorum.add_task(unsafe_counter.add, amount=amount)
    return await unsafe_counter.current

  @app.exception_handler(ValueError)
  def value_error_handler(request: Request, exc: ValueError) -> JSONResponse:
    return JSONResponse(status_code=520, content={"detail": str(exc)})

  with TestClient(app) as client:
    yield client


__all__: Final[tuple[str, ...]] = ("test_client",)
