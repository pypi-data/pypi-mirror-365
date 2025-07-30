#!/usr/bin/env python3.9
# coding:utf-8
# Copyright (C) 2025 All rights reserved.
# FILENAME:    ~~/tests/litestar/cancelled.py
# VERSION:     0.0.3
# CREATED:     2025-07-24 13:11
# AUTHOR:      Sitt Guruvanich <aekazitt+github@gmail.com>
# DESCRIPTION: Test script to demonstrate Decorum retries on Litestar
#
# HISTORY:
# *************************************************************
"""
Tests for Etiquette plugin for Litestar race condition scenarios
"""

### Standard packages ###
from asyncio import sleep

### Third-party packages ###
from litestar.testing import TestClient
from httpx import Response
from pytest import mark

### Local modules ###
from tests.litestar import test_client


@mark.asyncio
async def test_sure_fail_counter(test_client: TestClient) -> None:
  """Test to demonstrate retries when using a SureFailCounter"""
  response: Response = test_client.get("/sure-fail-counter")
  assert int(response.text) == 0
