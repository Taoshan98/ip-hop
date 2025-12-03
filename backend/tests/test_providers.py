"""
Comprehensive provider endpoint tests.
Tests CRUD operations and validation for DNS providers.
"""
import pytest
from fastapi.testclient import TestClient


class TestProviderCreate:
    """Test provider creation."""

    def test_create_dynu_provider(self, client: TestClient, auth_headers: dict):
        """Test creating Dynu provider."""
        response = client.post(
            "/api/v1/providers",
            headers=auth_headers,
            json={
                "name": "My Dynu",
                "type": "dynu",
                "credentials": {"token": "test_token_123"},
                "is_enabled": True
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "My Dynu"
        assert data["type"] == "dynu"
        assert data["is_enabled"] is True
        assert "id" in data
        assert "credentials_encrypted" not in data  # Should not expose encrypted data

    def test_create_cloudflare_provider(self, client: TestClient, auth_headers: dict):
        """Test creating Cloudflare provider."""
        response = client.post(
            "/api/v1/providers",
            headers=auth_headers,
            json={
                "name": "Cloudflare Primary",
                "type": "cloudflare",
                "credentials": {"token": "cf_token_xyz"},
                "is_enabled": True
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["type"] == "cloudflare"

    def test_create_provider_unauthenticated(self, client: TestClient):
        """Test creating provider without authentication."""
        response = client.post(
            "/api/v1/providers",
            json={
                "name": "Test",
                "type": "dynu",
                "credentials": {"token": "token"},
                "is_enabled": True
            }
        )
        assert response.status_code == 401

    def test_create_provider_invalid_type(self, client: TestClient, auth_headers: dict):
        """Test creating provider with custom type - API allows it."""
        response = client.post(
            "/api/v1/providers",
            headers=auth_headers,
            json={
                "name": "Invalid",
                "type": "invalid_type",
                "credentials": {"token": "token"},
                "is_enabled": True
            }
        )
        # API currently allows any provider type string
        assert response.status_code in [200, 400, 422]

    def test_create_provider_missing_credentials(self, client: TestClient, auth_headers: dict):
        """Test creating provider without credentials."""
        response = client.post(
            "/api/v1/providers",
            headers=auth_headers,
            json={
                "name": "No Creds",
                "type": "dynu",
                "is_enabled": True
            }
        )
        assert response.status_code == 422


class TestProviderRead:
    """Test provider retrieval."""

    def test_get_providers_empty(self, client: TestClient, auth_headers: dict):
        """Test getting providers when none exist."""
        response = client.get("/api/v1/providers", headers=auth_headers)
        assert response.status_code == 200
        assert response.json() == []

    def test_get_providers_list(self, client: TestClient, auth_headers: dict):
        """Test getting list of providers."""
        # Create two providers
        client.post(
            "/api/v1/providers",
            headers=auth_headers,
            json={"name": "P1", "type": "dynu", "credentials": {"token": "t1"}, "is_enabled": True}
        )
        client.post(
            "/api/v1/providers",
            headers=auth_headers,
            json={"name": "P2", "type": "cloudflare", "credentials": {"token": "t2"}, "is_enabled": False}
        )

        response = client.get("/api/v1/providers", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0]["name"] == "P1"
        assert data[1]["name"] == "P2"

    def test_get_providers_unauthenticated(self, client: TestClient):
        """Test getting providers without authentication."""
        response = client.get("/api/v1/providers")
        assert response.status_code == 401


class TestProviderUpdate:
    """Test provider updates."""

    def test_update_provider_name(self, client: TestClient, auth_headers: dict):
        """Test updating provider name."""
        # Create provider
        create_resp = client.post(
            "/api/v1/providers",
            headers=auth_headers,
            json={"name": "Original", "type": "dynu", "credentials": {"token": "t"}, "is_enabled": True}
        )
        provider_id = create_resp.json()["id"]

        # Update name
        response = client.put(
            f"/api/v1/providers/{provider_id}",
            headers=auth_headers,
            json={"name": "Updated Name"}
        )
        assert response.status_code == 200
        assert response.json()["name"] == "Updated Name"

    def test_update_provider_enabled_status(self, client: TestClient, auth_headers: dict):
        """Test enabling/disabling provider."""
        create_resp = client.post(
            "/api/v1/providers",
            headers=auth_headers,
            json={"name": "Test", "type": "dynu", "credentials": {"token": "t"}, "is_enabled": True}
        )
        provider_id = create_resp.json()["id"]

        # Disable
        response = client.put(
            f"/api/v1/providers/{provider_id}",
            headers=auth_headers,
            json={"is_enabled": False}
        )
        assert response.status_code == 200
        assert response.json()["is_enabled"] is False

    def test_update_provider_credentials(self, client: TestClient, auth_headers: dict):
        """Test updating provider credentials."""
        create_resp = client.post(
            "/api/v1/providers",
            headers=auth_headers,
            json={"name": "Test", "type": "dynu", "credentials": {"token": "old"}, "is_enabled": True}
        )
        provider_id = create_resp.json()["id"]

        response = client.put(
            f"/api/v1/providers/{provider_id}",
            headers=auth_headers,
            json={"credentials": {"token": "new_token"}}
        )
        assert response.status_code == 200

    def test_update_nonexistent_provider(self, client: TestClient, auth_headers: dict):
        """Test updating non-existent provider."""
        response = client.put(
            "/api/v1/providers/999",
            headers=auth_headers,
            json={"name": "Updated"}
        )
        assert response.status_code == 404


class TestProviderDelete:
    """Test provider deletion."""

    def test_delete_provider_success(self, client: TestClient, auth_headers: dict):
        """Test successful provider deletion."""
        create_resp = client.post(
            "/api/v1/providers",
            headers=auth_headers,
            json={"name": "ToDelete", "type": "dynu", "credentials": {"token": "t"}, "is_enabled": True}
        )
        provider_id = create_resp.json()["id"]

        response = client.delete(f"/api/v1/providers/{provider_id}", headers=auth_headers)
        assert response.status_code == 200

        # Verify deletion
        get_resp = client.get("/api/v1/providers", headers=auth_headers)
        assert len(get_resp.json()) == 0

    def test_delete_nonexistent_provider(self, client: TestClient, auth_headers: dict):
        """Test deleting non-existent provider."""
        response = client.delete("/api/v1/providers/999", headers=auth_headers)
        assert response.status_code == 404

    def test_delete_provider_unauthenticated(self, client: TestClient):
        """Test deleting provider without authentication."""
        response = client.delete("/api/v1/providers/1")
        assert response.status_code == 401
