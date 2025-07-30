#!/usr/bin/env python3.9
# coding:utf-8
# Copyright (C) 2025 All rights reserved.
# FILENAME:    ~~/src/etiquette/core.py
# VERSION:     0.0.3
# CREATED:     2025-07-23 14:20
# AUTHOR:      Sitt Guruvanich <aekazitt+github@gmail.com>
# DESCRIPTION:
#
# HISTORY:
# *************************************************************

### Standard packages ###
from __future__ import annotations
from logging import Logger, getLogger
from typing import Any, Callable, Final
from uuid import UUID, uuid4 as uuid

### Local modules ###
from etiquette._types import TaskData
from etiquette.core import Etiquette

logger: Logger = getLogger(__name__)


class Decorum:
  def __init__(self) -> None:
    if not Etiquette.running:
      raise ValueError("Please initiate Etiquette at FastAPI / Litestar startup")

  async def add_task(self, callable: Callable[..., Any], *args: Any, **kwargs: Any) -> UUID:
    """Add a task to the queue"""
    task_id: UUID = uuid()
    task_data: TaskData = TaskData(
      args=args,
      callable=callable,
      kwargs=kwargs,
      task_id=task_id,
    )
    await Etiquette.task_queue.put(item=task_data)
    logger.debug(msg=f"Task {task_id} added to queue. Queue size: {Etiquette.task_queue.qsize()}")
    return task_id


__all__: Final[tuple[str, ...]] = ("Decorum",)
