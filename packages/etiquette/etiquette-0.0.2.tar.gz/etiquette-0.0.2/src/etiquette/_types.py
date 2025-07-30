#!/usr/bin/env python3.9
# coding:utf-8
# Copyright (C) 2025 All rights reserved.
# FILENAME:    ~~/src/etiquette/_types.py
# VERSION:     0.0.2
# CREATED:     2025-07-23 14:20
# AUTHOR:      Sitt Guruvanich <aekazitt+github@gmail.com>
# DESCRIPTION:
#
# HISTORY:
# *************************************************************

### Standard packages ###
from dataclasses import dataclass
from typing import Any, Callable, Final
from uuid import UUID


@dataclass
class TaskData:
  callable: Callable[..., Any]
  args: tuple[Any] | None
  kwargs: dict[str, Any] | None
  task_id: UUID


__all__: Final[tuple[str, ...]] = ("TaskData",)
