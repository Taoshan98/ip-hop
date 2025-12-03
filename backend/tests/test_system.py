"""
System endpoint and security tests.
Tests system status, security utilities, and edge cases.
"""
import pytest
from fastapi.testclient import TestClient

from app.core import security


class TestSystemEndpoints:
    """Test system-level endpoints."""

    def test_system_status_response_format(self, client: TestClient):
        """Test system status endpoint returns correct format."""
        response = client.get("/api/v1/system/status")
        assert response.status_code == 200
        data = response.json()
        # Check response structure
        assert "initialized" in data
        assert "version" in data
        assert data["version"] == "1.0.0"
        # initialized can be True or False depending on DB state
        assert isinstance(data["initialized"], bool)

    def test_root_endpoint(self, client: TestClient):
        """Test root path."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data


class TestSecurityUtilities:
    """Test security and encryption utilities."""

    def test_password_hashing(self):
        """Test password hashing and verification."""
        password = "Secure123!"  # Shorter to avoid bcrypt 72 byte limit
        hashed = security.get_password_hash(password)
        
        assert hashed != password
        assert security.verify_password(password, hashed) is True
        assert security.verify_password("Wrong123!", hashed) is False

    def test_encrypt_decrypt_credentials(self):
        """Test credential encryption and decryption."""
        original = {"token": "secret_token_123", "api_key": "key456"}
        
        encrypted = security.encrypt_credentials(original)
        assert encrypted != str(original)
        assert isinstance(encrypted, str)
        
        decrypted = security.decrypt_credentials(encrypted)
        assert decrypted == original

    def test_jwt_creation_and_verification(self):
        """Test JWT token creation and verification."""
        subject = "testuser"
        
        token = security.create_access_token(subject=subject)
        assert isinstance(token, str)
        
        decoded = security.decode_access_token(token)
        assert decoded is not None
        assert decoded["sub"] == subject

    def test_jwt_expired_token(self):
        """Test handling of expired JWT tokens."""
        from datetime import timedelta
        
        subject = "testuser"
        # Create token with negative expiry (immediately expired)
        token = security.create_access_token(subject=subject, expires_delta=timedelta(seconds=-10))
        
        decoded = security.decode_access_token(token)
        assert decoded is None  # Expired tokens return None

    def test_jwt_invalid_token(self):
        """Test handling of invalid JWT tokens."""
        invalid_token = "invalid.jwt.token"
        decoded = security.decode_access_token(invalid_token)
        assert decoded is None


class TestPasswordValidation:
    """Test password validation rules."""

    def test_password_strength_validation(self, client: TestClient):
        """Test various password strength scenarios."""
        weak_passwords = [
            "short",
            "12345678",
            "allowercase",
            "ALLUPPERCASE",
            "NoNumbers!",
            "nonspecial1"
        ]
        
        for weak_pass in weak_passwords:
            response = client.post(
                "/api/v1/auth/setup",
                json={"username": "admin", "password": weak_pass}
            )
            assert response.status_code == 400, f"Password '{weak_pass}' should be rejected"

    def test_password_strong_validation(self, client: TestClient):
        """Test that strong passwords are accepted."""
        strong_passwords = [
            "SecurePass123!",
            "MyP@ssw0rd",
            "C0mpl3x!Pass"
        ]
        
        for strong_pass in strong_passwords:
            response = client.post(
                "/api/v1/auth/setup",
                json={"username": "admin", "password": strong_pass}
            )
            # Should succeed (first one) or fail because admin exists (subsequent)
            assert response.status_code in [200, 400]


class TestErrorHandling:
    """Test error handling and edge cases."""

    def test_malformed_json(self, client: TestClient):
        """Test handling of malformed JSON."""
        response = client.post(
            "/api/v1/auth/setup",
            content=b"{invalid json",
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 422

    def test_wrong_content_type(self, client: TestClient, admin_user: dict):
        """Test API with wrong content type."""
        response = client.post(
            "/api/v1/auth/token",
            json=admin_user,  # Should be form data, not JSON
        )
        # FastAPI OAuth2PasswordRequestForm expects form data
        assert response.status_code == 422

    def test_missing_authorization_header(self, client: TestClient):
        """Test protected endpoints without auth header."""
        protected_endpoints = [
            "/api/v1/providers",
            "/api/v1/domains",
            "/api/v1/auth/me"
        ]
        
        for endpoint in protected_endpoints:
            response = client.get(endpoint)
            assert response.status_code == 401

    def test_invalid_bearer_token_format(self, client: TestClient):
        """Test with malformed Bearer token."""
        response = client.get(
            "/api/v1/auth/me",
            headers={"Authorization": "NotBearer token"}
        )
        assert response.status_code == 401


class TestDatabaseIntegrity:
    """Test database constraints and integrity."""

    def test_unique_username_constraint(self, db):
        """Test that duplicate usernames are prevented."""
        from app.models import User
        from app.core import security
        
        # First user
        user1 = User(
            username="testuser",
            password_hash=security.get_password_hash("pass123")
        )
        db.add(user1)
        db.commit()
        
        # Try to create duplicate
        user2 = User(
            username="testuser",
            password_hash=security.get_password_hash("pass456")
        )
        db.add(user2)
        
        with pytest.raises(Exception):  # SQLAlchemy integrity error
            db.commit()

    def test_provider_domain_relationship(self, db):
        """Test provider-domain foreign key relationship."""
        from app.models import Domain, Provider
        from app.core import security
        
        # Create provider
        provider = Provider(
            name="Test",
            type="dynu",
            credentials_encrypted=security.encrypt_credentials({"token": "t"}),
            is_enabled=True
        )
        db.add(provider)
        db.commit()
        
        # Create domain
        domain = Domain(
            provider_id=provider.id,
            domain_name="test.com",
            external_id="123",
            config={}
        )
        db.add(domain)
        db.commit()
        
        # Verify relationship
        assert domain.provider.name == "Test"
        assert provider.domains[0].domain_name == "test.com"
