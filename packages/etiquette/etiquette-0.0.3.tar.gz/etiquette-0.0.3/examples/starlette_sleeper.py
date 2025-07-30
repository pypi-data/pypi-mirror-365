#!/usr/bin/env python3.9
# coding:utf-8
# Copyright (C) 2025 All rights reserved.
# FILENAME:    ~~/examples/starlette_sleeper.py
# VERSION:     0.0.3
# CREATED:     2025-07-29 15:23
# AUTHOR:      Sitt Guruvanich <aekazitt+github@gmail.com>
# DESCRIPTION:
#
# HISTORY:
# *************************************************************

### Standard packages ###
from asyncio import sleep
from contextlib import asynccontextmanager
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


async def add_sleep_task_to_decorum(request: Request) -> PlainTextResponse:
  async def sleep_3() -> None:
    await sleep(3)
    print("task done")

  await request.state.decorum.add_task(sleep_3)
  return PlainTextResponse("OK")


app: Starlette = Starlette(
  lifespan=lifespan,
  routes=[Route("/add-task", add_sleep_task_to_decorum)],
)

__all__: Final[tuple[str, ...]] = ("app",)
