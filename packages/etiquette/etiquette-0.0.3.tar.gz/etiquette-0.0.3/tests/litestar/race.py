#!/usr/bin/env python3.9
# coding:utf-8
# Copyright (C) 2025 All rights reserved.
# FILENAME:    ~~/tests/litestar/race.py
# VERSION:     0.0.3
# CREATED:     2025-07-24 13:11
# AUTHOR:      Sitt Guruvanich <aekazitt+github@gmail.com>
# DESCRIPTION: Test script to demonstrate Litestar race condition prevention
#
# HISTORY:
# *************************************************************
"""
Tests for Etiquette plugin for Litestar race condition scenarios
"""

### Third-party packages ###
from fastapi.testclient import TestClient
from httpx import Response
from pytest import mark

### Local modules ###
from tests.litestar import test_client


@mark.asyncio
async def test_safe_counter(test_client: TestClient) -> None:
  """Test to demonstrate race condition prevention on SafeCounter"""
  for i in range(20):
    test_client.get("/safe-counter")
  response: Response = test_client.get("/safe-counter")
  assert int(response.text) == 20


@mark.asyncio
async def test_unsafe_counter(test_client: TestClient) -> None:
  """Test to demonstrate race condition on UnsafeCounter"""
  for i in range(20):
    test_client.get("/unsafe-counter")
  response: Response = test_client.get("/unsafe-counter")
  assert int(response.text) < 20
