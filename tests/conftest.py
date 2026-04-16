"""
Pytest configuration and fixtures for the FastAPI application tests.
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app


@pytest.fixture
def fastapi_app():
    """
    Fixture that provides the FastAPI application instance.
    
    Arrange: Set up the app for testing.
    """
    return app


@pytest.fixture
def client(fastapi_app):
    """
    Fixture that provides a TestClient instance for making HTTP requests to the app.
    
    Depends on the fastapi_app fixture. Automatically handles request/response
    serialization and allows testing endpoints without running the server.
    
    Arrange: Set up the test client with the app.
    """
    return TestClient(fastapi_app)
