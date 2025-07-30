#!/usr/bin/env python3.9
# coding:utf-8
# Copyright (C) 2025 All rights reserved.
# FILENAME:    ~~/examples/litestar_counter.py
# VERSION:     0.0.3
# CREATED:     2025-07-24 11:22
# AUTHOR:      Sitt Guruvanich <aekazitt+github@gmail.com>
# DESCRIPTION:
#
# HISTORY:
# *************************************************************

### Standard packages ###
from asyncio import Lock, sleep
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from typing import AsyncGenerator, Final

### Third-party packages ###
from litestar import Litestar
from litestar.di import Provide
from litestar.handlers.http_handlers.decorators import get

### Local modules ###
from etiquette import Decorum, Etiquette


@asynccontextmanager
async def lifespan(_: Litestar) -> AsyncGenerator[None, None]:
  Etiquette.initiate(max_concurrent_tasks=16)
  yield
  await Etiquette.release()


@dataclass
class AtomicCounter:
  _lock: Lock = field(default_factory=Lock, init=False)
  count: int = 0

  async def increment(self) -> None:
    async with self._lock:
      self.count += 1
      current_count: int = self.count
    await sleep(delay=1)
    print(f"{current_count=}")


counter: AtomicCounter = AtomicCounter()


@get("/add-task")
async def add_new_task(decorum: Decorum) -> str:
  await decorum.add_task(counter.increment)
  return "OK"


app: Litestar = Litestar(
  dependencies={"decorum": Provide(Decorum, sync_to_thread=True)},
  lifespan=[lifespan],
  route_handlers=[add_new_task],
)

__all__: Final[tuple[str, ...]] = ("app",)
