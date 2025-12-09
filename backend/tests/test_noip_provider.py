"""
No-IP Provider Tests.
Tests No-IP provider implementation with DDNS Key authentication.
"""
import pytest
import httpx
from unittest.mock import Mock, AsyncMock, patch
from app.providers.noip import NoIPProvider
from app.schemas.providers import DomainConfig
from app.core.exceptions import ProviderError


class TestNoIPProvider:
    """Test No-IP provider implementation."""

    @pytest.mark.asyncio
    async def test_noip_provider_success_good(self):
        """Test No-IP provider successful update (good response)."""
        with patch("httpx.AsyncClient") as MockClient:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.text = "good 1.2.3.4"
            
            mock_client = MockClient.return_value.__aenter__.return_value
            mock_client.get = AsyncMock(return_value=mock_response)

            provider = NoIPProvider(username="ddns_user", password="ddns_pass")
            config = DomainConfig(name="myhost.ddns.net")
            
            result = await provider.update_record("1.2.3.4", config)
            assert result is True

    @pytest.mark.asyncio
    async def test_noip_provider_success_nochg(self):
        """Test No-IP provider with no change needed (nochg response)."""
        with patch("httpx.AsyncClient") as MockClient:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.text = "nochg 1.2.3.4"
            
            mock_client = MockClient.return_value.__aenter__.return_value
            mock_client.get = AsyncMock(return_value=mock_response)

            provider = NoIPProvider(username="ddns_user", password="ddns_pass")
            config = DomainConfig(name="myhost.ddns.net")
            
            result = await provider.update_record("1.2.3.4", config)
            assert result is True

    @pytest.mark.asyncio
    async def test_noip_provider_badauth(self):
        """Test No-IP authentication failure (badauth)."""
        with patch("httpx.AsyncClient") as MockClient:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.text = "badauth"
            
            mock_client = MockClient.return_value.__aenter__.return_value
            mock_client.get = AsyncMock(return_value=mock_response)

            provider = NoIPProvider(username="wrong_user", password="wrong_pass")
            config = DomainConfig(name="myhost.ddns.net")
            
            with pytest.raises(ProviderError, match="badauth"):
                await provider.update_record("1.2.3.4", config)

    @pytest.mark.asyncio
    async def test_noip_provider_nohost(self):
        """Test No-IP hostname not found (nohost)."""
        with patch("httpx.AsyncClient") as MockClient:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.text = "nohost"
            
            mock_client = MockClient.return_value.__aenter__.return_value
            mock_client.get = AsyncMock(return_value=mock_response)

            provider = NoIPProvider(username="ddns_user", password="ddns_pass")
            config = DomainConfig(name="nonexistent.ddns.net")
            
            result = await provider.update_record("1.2.3.4", config)
            assert result is False

    @pytest.mark.asyncio
    async def test_noip_provider_badagent(self):
        """Test No-IP client banned (badagent)."""
        with patch("httpx.AsyncClient") as MockClient:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.text = "badagent"
            
            mock_client = MockClient.return_value.__aenter__.return_value
            mock_client.get = AsyncMock(return_value=mock_response)

            provider = NoIPProvider(username="ddns_user", password="ddns_pass")
            config = DomainConfig(name="myhost.ddns.net")
            
            with pytest.raises(ProviderError, match="badagent"):
                await provider.update_record("1.2.3.4", config)

    @pytest.mark.asyncio
    async def test_noip_provider_abuse(self):
        """Test No-IP account blocked (abuse)."""
        with patch("httpx.AsyncClient") as MockClient:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.text = "abuse"
            
            mock_client = MockClient.return_value.__aenter__.return_value
            mock_client.get = AsyncMock(return_value=mock_response)

            provider = NoIPProvider(username="ddns_user", password="ddns_pass")
            config = DomainConfig(name="myhost.ddns.net")
            
            with pytest.raises(ProviderError, match="abuse"):
                await provider.update_record("1.2.3.4", config)

    @pytest.mark.asyncio
    async def test_noip_provider_donator(self):
        """Test No-IP feature not available (!donator)."""
        with patch("httpx.AsyncClient") as MockClient:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.text = "!donator"
            
            mock_client = MockClient.return_value.__aenter__.return_value
            mock_client.get = AsyncMock(return_value=mock_response)

            provider = NoIPProvider(username="ddns_user", password="ddns_pass")
            config = DomainConfig(name="myhost.ddns.net")
            
            result = await provider.update_record("1.2.3.4", config)
            assert result is False

    @pytest.mark.asyncio
    async def test_noip_provider_missing_username(self):
        """Test No-IP with missing username."""
        provider = NoIPProvider(username="", password="ddns_pass")
        config = DomainConfig(name="myhost.ddns.net")
        
        with pytest.raises(ProviderError, match="credentials missing"):
            await provider.update_record("1.2.3.4", config)

    @pytest.mark.asyncio
    async def test_noip_provider_missing_password(self):
        """Test No-IP with missing password."""
        provider = NoIPProvider(username="ddns_user", password="")
        config = DomainConfig(name="myhost.ddns.net")
        
        with pytest.raises(ProviderError, match="credentials missing"):
            await provider.update_record("1.2.3.4", config)

    @pytest.mark.asyncio
    async def test_noip_provider_network_error(self):
        """Test No-IP network error handling."""
        with patch("httpx.AsyncClient") as MockClient:
            mock_client = MockClient.return_value.__aenter__.return_value
            mock_client.get = AsyncMock(side_effect=httpx.HTTPError("Network error"))

            provider = NoIPProvider(username="ddns_user", password="ddns_pass")
            config = DomainConfig(name="myhost.ddns.net")
            
            with pytest.raises(ProviderError, match="Network error"):
                await provider.update_record("1.2.3.4", config)

    @pytest.mark.asyncio
    async def test_noip_provider_unexpected_response(self):
        """Test No-IP with unexpected response."""
        with patch("httpx.AsyncClient") as MockClient:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.text = "UNEXPECTED"
            
            mock_client = MockClient.return_value.__aenter__.return_value
            mock_client.get = AsyncMock(return_value=mock_response)

            provider = NoIPProvider(username="ddns_user", password="ddns_pass")
            config = DomainConfig(name="myhost.ddns.net")
            
            result = await provider.update_record("1.2.3.4", config)
            assert result is False

    @pytest.mark.asyncio
    async def test_noip_provider_http_error(self):
        """Test No-IP with HTTP error status."""
        with patch("httpx.AsyncClient") as MockClient:
            mock_response = Mock()
            mock_response.status_code = 500
            mock_response.text = "Internal Server Error"
            
            mock_client = MockClient.return_value.__aenter__.return_value
            mock_client.get = AsyncMock(return_value=mock_response)

            provider = NoIPProvider(username="ddns_user", password="ddns_pass")
            config = DomainConfig(name="myhost.ddns.net")
            
            result = await provider.update_record("1.2.3.4", config)
            assert result is False

    @pytest.mark.asyncio
    async def test_noip_provider_name_property(self):
        """Test No-IP provider name property."""
        provider = NoIPProvider(username="ddns_user", password="ddns_pass")
        assert provider.name == "noip"

    @pytest.mark.asyncio
    async def test_noip_provider_empty_hostname(self):
        """Test No-IP with empty hostname."""
        provider = NoIPProvider(username="ddns_user", password="ddns_pass")
        config = DomainConfig(name="")
        
        result = await provider.update_record("1.2.3.4", config)
        assert result is False

    @pytest.mark.asyncio
    async def test_noip_provider_basic_auth_header(self):
        """Test No-IP sends correct Basic Auth header."""
        with patch("httpx.AsyncClient") as MockClient:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.text = "good 1.2.3.4"
            
            mock_client = MockClient.return_value.__aenter__.return_value
            mock_client.get = AsyncMock(return_value=mock_response)

            provider = NoIPProvider(username="testuser", password="testpass")
            config = DomainConfig(name="myhost.ddns.net")
            
            await provider.update_record("1.2.3.4", config)
            
            # Verify headers were sent correctly
            call_args = mock_client.get.call_args
            headers = call_args[1]['headers']
            
            # Check Basic Auth header exists
            assert 'Authorization' in headers
            assert headers['Authorization'].startswith('Basic ')
            
            # Check User-Agent header
            assert 'User-Agent' in headers
            assert 'IP-HOP' in headers['User-Agent']
