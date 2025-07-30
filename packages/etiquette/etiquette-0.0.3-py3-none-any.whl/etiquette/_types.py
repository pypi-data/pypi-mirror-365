#!/usr/bin/env python3.9
# coding:utf-8
# Copyright (C) 2025 All rights reserved.
# FILENAME:    ~~/src/etiquette/_types.py
# VERSION:     0.0.3
# CREATED:     2025-07-23 14:20
# AUTHOR:      Sitt Guruvanich <aekazitt+github@gmail.com>
# DESCRIPTION:
#
# HISTORY:
# *************************************************************

### Standard packages ###
from dataclasses import dataclass, field
from typing import Any, Callable, Mapping, Final
from uuid import UUID


@dataclass
class TaskData:
  callable: Callable[..., Any]
  task_id: UUID
  args: tuple[Any, ...] = field(default_factory=tuple)
  kwargs: Mapping[str, Any] = field(default_factory=dict)


__all__: Final[tuple[str, ...]] = ("TaskData",)
