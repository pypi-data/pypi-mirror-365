#!/usr/bin/env python3.9
# coding:utf-8
# Copyright (C) 2025 All rights reserved.
# FILENAME:    ~~/examples/starlette_counter.py
# VERSION:     0.0.3
# CREATED:     2025-07-29 15:23
# AUTHOR:      Sitt Guruvanich <aekazitt+github@gmail.com>
# DESCRIPTION:
#
# HISTORY:
# *************************************************************

### Standard packages ###
from asyncio import Lock, sleep
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from typing import AsyncIterator, Final, TypedDict

### Third-party packages ###
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import PlainTextResponse
from starlette.routing import Route

### Local modules ###
from etiquette import Decorum, Etiquette


class State(TypedDict):
  decorum: Decorum


@asynccontextmanager
async def lifespan(_: Starlette) -> AsyncIterator[State]:
  Etiquette.initiate(max_concurrent_tasks=16)
  decorum: Decorum = Decorum()
  yield {"decorum": decorum}
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


async def add_new_task(request: Request) -> PlainTextResponse:
  await request.state.decorum.add_task(counter.increment)
  return PlainTextResponse("OK")


app: Starlette = Starlette(lifespan=lifespan, routes=[Route("/add-task", add_new_task)])

__all__: Final[tuple[str, ...]] = ("app",)
