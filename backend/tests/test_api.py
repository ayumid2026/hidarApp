"""
Integration tests for API endpoints.
Run with: pytest backend/tests/
"""

import pytest
import asyncio
from httpx import AsyncClient, ASGITransport
from app.main import app

@pytest.mark.asyncio
async def test_root_endpoint():
    """Test the root endpoint."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/")
        assert response.status_code == 200
        assert response.json() == {"message": "Welcome to the Hidar API", "docs": "/docs"}

@pytest.mark.asyncio
async def test_register_user():
    """Test user registration API."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Try to register
        response = await client.post(
            "/auth/register",
            json={
                "phone_number": "0922222222",
                "name": "API Test User",
                "email": "apitest@example.com",
                "password": "testpass123"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["phone_number"] == "0922222222"
        assert data["name"] == "API Test User"

@pytest.mark.asyncio
async def test_duplicate_registration():
    """Test that duplicate registration is rejected."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # First registration
        await client.post(
            "/auth/register",
            json={
                "phone_number": "0933333333",
                "name": "Duplicate Test",
                "password": "testpass123"
            }
        )
        # Second registration with same phone
        response = await client.post(
            "/auth/register",
            json={
                "phone_number": "0933333333",
                "name": "Duplicate Test",
                "password": "testpass123"
            }
        )
        assert response.status_code == 400
        assert "already registered" in response.json()["detail"]

@pytest.mark.asyncio
async def test_login():
    """Test login API."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Register user
        await client.post(
            "/auth/register",
            json={
                "phone_number": "0944444444",
                "name": "Login Test",
                "password": "loginpass123"
            }
        )
        # Login
        response = await client.post(
            "/auth/login",
            data={
                "username": "0944444444",
                "password": "loginpass123"
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

@pytest.mark.asyncio
async def test_protected_endpoint():
    """Test accessing protected endpoint with valid token."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Register and login
        await client.post(
            "/auth/register",
            json={
                "phone_number": "0955555555",
                "name": "Protected Test",
                "password": "securepass123"
            }
        )
        login_response = await client.post(
            "/auth/login",
            data={
                "username": "0955555555",
                "password": "securepass123"
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        token = login_response.json()["access_token"]
        
        # Access protected endpoint (alerts list)
        response = await client.get(
            "/alerts",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        # Should return empty list (no alerts yet)
        assert response.json() == []
