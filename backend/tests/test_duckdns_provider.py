"""
DuckDNS Provider Tests.
Tests DuckDNS provider implementation.
"""
import pytest
import httpx
from unittest.mock import Mock, AsyncMock, patch
from app.providers.duckdns import DuckDNSProvider
from app.schemas.providers import DomainConfig
from app.core.exceptions import ProviderError


class TestDuckDNSProvider:
    """Test DuckDNS provider implementation."""

    @pytest.mark.asyncio
    async def test_duckdns_provider_success(self):
        """Test DuckDNS provider successful update."""
        with patch("httpx.AsyncClient") as MockClient:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.text = "OK\n1.2.3.4\n\nUPDATED"
            
            mock_client = MockClient.return_value.__aenter__.return_value
            mock_client.get = AsyncMock(return_value=mock_response)

            provider = DuckDNSProvider(token="test_token_123")
            config = DomainConfig(name="testsubdomain")
            
            result = await provider.update_record("1.2.3.4", config)
            assert result is True

    @pytest.mark.asyncio
    async def test_duckdns_provider_success_simple_ok(self):
        """Test DuckDNS with simple OK response."""
        with patch("httpx.AsyncClient") as MockClient:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.text = "OK"
            
            mock_client = MockClient.return_value.__aenter__.return_value
            mock_client.get = AsyncMock(return_value=mock_response)

            provider = DuckDNSProvider(token="test_token")
            config = DomainConfig(name="mysubdomain")
            
            result = await provider.update_record("5.6.7.8", config)
            assert result is True

    @pytest.mark.asyncio
    async def test_duckdns_provider_with_full_domain(self):
        """Test DuckDNS with full domain name (subdomain.duckdns.org)."""
        with patch("httpx.AsyncClient") as MockClient:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.text = "OK"
            
            mock_client = MockClient.return_value.__aenter__.return_value
            mock_client.get = AsyncMock(return_value=mock_response)

            provider = DuckDNSProvider(token="test_token")
            config = DomainConfig(name="testsubdomain.duckdns.org")
            
            result = await provider.update_record("1.2.3.4", config)
            assert result is True
            
            # Verify subdomain was extracted correctly
            call_args = mock_client.get.call_args
            assert call_args[1]['params']['domains'] == 'testsubdomain'

    @pytest.mark.asyncio
    async def test_duckdns_provider_failure_ko(self):
        """Test DuckDNS provider failure (KO response)."""
        with patch("httpx.AsyncClient") as MockClient:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.text = "KO"
            
            mock_client = MockClient.return_value.__aenter__.return_value
            mock_client.get = AsyncMock(return_value=mock_response)

            provider = DuckDNSProvider(token="invalid_token")
            config = DomainConfig(name="testdomain")
            
            result = await provider.update_record("1.2.3.4", config)
            assert result is False

    @pytest.mark.asyncio
    async def test_duckdns_provider_missing_token(self):
        """Test DuckDNS with missing token."""
        provider = DuckDNSProvider(token="")
        config = DomainConfig(name="testdomain")
        
        with pytest.raises(ProviderError, match="token missing"):
            await provider.update_record("1.2.3.4", config)

    @pytest.mark.asyncio
    async def test_duckdns_provider_network_error(self):
        """Test DuckDNS network error handling."""
        with patch("httpx.AsyncClient") as MockClient:
            mock_client = MockClient.return_value.__aenter__.return_value
            mock_client.get = AsyncMock(side_effect=httpx.HTTPError("Network error"))

            provider = DuckDNSProvider(token="test_token")
            config = DomainConfig(name="testdomain")
            
            with pytest.raises(ProviderError, match="Network error"):
                await provider.update_record("1.2.3.4", config)

    @pytest.mark.asyncio
    async def test_duckdns_provider_unexpected_response(self):
        """Test DuckDNS with unexpected response."""
        with patch("httpx.AsyncClient") as MockClient:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.text = "UNEXPECTED"
            
            mock_client = MockClient.return_value.__aenter__.return_value
            mock_client.get = AsyncMock(return_value=mock_response)

            provider = DuckDNSProvider(token="test_token")
            config = DomainConfig(name="testdomain")
            
            result = await provider.update_record("1.2.3.4", config)
            assert result is False

    @pytest.mark.asyncio
    async def test_duckdns_provider_http_error(self):
        """Test DuckDNS with HTTP error status."""
        with patch("httpx.AsyncClient") as MockClient:
            mock_response = Mock()
            mock_response.status_code = 500
            mock_response.text = "Internal Server Error"
            
            mock_client = MockClient.return_value.__aenter__.return_value
            mock_client.get = AsyncMock(return_value=mock_response)

            provider = DuckDNSProvider(token="test_token")
            config = DomainConfig(name="testdomain")
            
            result = await provider.update_record("1.2.3.4", config)
            assert result is False

    @pytest.mark.asyncio
    async def test_duckdns_provider_name_property(self):
        """Test DuckDNS provider name property."""
        provider = DuckDNSProvider(token="test_token")
        assert provider.name == "duckdns"

    @pytest.mark.asyncio
    async def test_duckdns_provider_empty_subdomain(self):
        """Test DuckDNS with empty subdomain after extraction."""
        provider = DuckDNSProvider(token="test_token")
        config = DomainConfig(name=".duckdns.org")  # Edge case
        
        result = await provider.update_record("1.2.3.4", config)
        assert result is False
