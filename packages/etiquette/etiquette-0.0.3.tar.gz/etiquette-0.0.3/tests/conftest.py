#!/usr/bin/env python3.9
# coding:utf-8
# Copyright (C) 2025 All rights reserved.
# FILENAME:    ~~/tests/conftest.py
# VERSION:     0.0.3
# CREATED:     2025-07-29 17:52
# AUTHOR:      Sitt Guruvanich <aekazitt+github@gmail.com>
# DESCRIPTION:
#
# HISTORY:
# *************************************************************

### Standard packages ###
from typing import Final

### Third-party packages ###
from pytest import fixture
from uvloop import EventLoopPolicy


@fixture(scope="session")
def event_loop_policy() -> EventLoopPolicy:
  return EventLoopPolicy()


__all__: Final[tuple[str, ...]] = ("event_loop_policy",)
