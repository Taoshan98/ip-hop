"""
Comprehensive service layer tests.
Tests DDNS service, IP fetching, and business logic.
"""
import pytest
from unittest.mock import AsyncMock, Mock, patch
from sqlalchemy.orm import Session

from app.services.ddns_service import DDNSService
from app.models import Domain, Provider
from app.core.exceptions import IPFetchError


class TestDDNSService:
    """Test DDNS service functionality."""

    @pytest.fixture
    def test_provider_db(self, db: Session) -> Provider:
        """Create a test provider in database."""
        from app.core import security
        
        provider = Provider(
            name="Test Provider",
            type="dynu",
            credentials_encrypted=security.encrypt_credentials({"token": "test_token"}),
            is_enabled=True
        )
        db.add(provider)
        db.commit()
        db.refresh(provider)
        return provider

    @pytest.fixture
    def test_domain_db(self, db: Session, test_provider_db: Provider) -> Domain:
        """Create a test domain in database."""
        domain = Domain(
            provider_id=test_provider_db.id,
            domain_name="test.example.com",
            external_id="123456",
            config={}
        )
        db.add(domain)
        db.commit()
        db.refresh(domain)
        return domain

    @pytest.mark.asyncio
    async def test_update_domain_ip_success(self, db: Session, test_domain_db: Domain):
        """Test successful domain IP update."""
        service = DDNSService(db)

        # Mock IP fetcher
        with patch("app.services.ddns_service.IPFetcher") as MockFetcher:
            mock_fetcher = MockFetcher.return_value
            mock_fetcher.get_current_ip = AsyncMock(return_value="1.2.3.4")

            # Mock provider
            with patch("app.services.ddns_service.DynuProvider") as MockProvider:
                mock_provider = MockProvider.return_value
                mock_provider.update_record = AsyncMock(return_value=True)

                result = await service.update_domain_ip(test_domain_db.id)
                
                assert result is True
                # Verify domain was updated
                db.refresh(test_domain_db)
                assert test_domain_db.last_known_ip == "1.2.3.4"
                assert test_domain_db.last_update_status == "SUCCESS"

    @pytest.mark.asyncio
    async def test_update_domain_ip_fetch_failure(self, db: Session, test_domain_db: Domain):
        """Test domain update when IP fetch fails."""
        service = DDNSService(db)

        with patch("app.services.ddns_service.IPFetcher") as MockFetcher:
            mock_fetcher = MockFetcher.return_value
            mock_fetcher.get_current_ip = AsyncMock(side_effect=IPFetchError("All services failed"))

            with pytest.raises(IPFetchError):
                await service.update_domain_ip(test_domain_db.id)

    @pytest.mark.asyncio
    async def test_update_domain_ip_provider_failure(self, db: Session, test_domain_db: Domain):
        """Test domain update when provider update fails."""
        service = DDNSService(db)

        with patch("app.services.ddns_service.IPFetcher") as MockFetcher:
            mock_fetcher = MockFetcher.return_value
            mock_fetcher.get_current_ip = AsyncMock(return_value="1.2.3.4")

            with patch("app.services.ddns_service.DynuProvider") as MockProvider:
                mock_provider = MockProvider.return_value
                mock_provider.update_record = AsyncMock(return_value=False)

                result = await service.update_domain_ip(test_domain_db.id)
                
                assert result is False
                db.refresh(test_domain_db)
                assert test_domain_db.last_update_status == "FAILED"

    @pytest.mark.asyncio
    async def test_update_domain_ip_invalid_domain(self, db: Session):
        """Test update with non-existent domain."""
        service = DDNSService(db)

        with pytest.raises(ValueError, match="Domain not found"):
            await service.update_domain_ip(999)

    @pytest.mark.asyncio
    async def test_update_domain_ip_disabled_provider(self, db: Session, test_domain_db: Domain, test_provider_db: Provider):
        """Test update when provider is disabled."""
        # Disable provider
        test_provider_db.is_enabled = False
        db.commit()

        service = DDNSService(db)

        with pytest.raises(ValueError, match="Provider is disabled"):
            await service.update_domain_ip(test_domain_db.id)


class TestIPFetcher:
    """Test IP fetcher functionality."""

    @pytest.mark.asyncio
    async def test_ip_fetcher_success(self):
        """Test successful IP fetching."""
        from app.core.ip_fetcher import IPFetcher

        with patch("httpx.AsyncClient") as MockClient:
            mock_response = Mock()
            mock_response.text = "  8.8.8.8  "
            mock_response.raise_for_status = Mock()
            
            mock_client = MockClient.return_value.__aenter__.return_value
            mock_client.get = AsyncMock(return_value=mock_response)

            fetcher = IPFetcher()
            ip = await fetcher.get_current_ip()
            
            assert ip == "8.8.8.8"

    @pytest.mark.asyncio
    async def test_ip_fetcher_all_services_fail(self):
        """Test when all IP services fail."""
        from app.core.ip_fetcher import IPFetcher

        with patch("httpx.AsyncClient") as MockClient:
            mock_client = MockClient.return_value.__aenter__.return_value
            mock_client.get = AsyncMock(side_effect=Exception("Network error"))

            fetcher = IPFetcher()
            
            with pytest.raises(IPFetchError, match="All IP fetch attempts failed"):
                await fetcher.get_current_ip()

    @pytest.mark.asyncio
    async def test_ip_fetcher_invalid_ip(self):
        """Test when service returns invalid IP."""
        from app.core.ip_fetcher import IPFetcher

        with patch("httpx.AsyncClient") as MockClient:
            mock_response = Mock()
            mock_response.text = "not_an_ip"
            mock_response.raise_for_status = Mock()
            
            mock_client = MockClient.return_value.__aenter__.return_value
            mock_client.get = AsyncMock(return_value=mock_response)

            fetcher = IPFetcher()
            
            with pytest.raises(IPFetchError):
                await fetcher.get_current_ip()

    @pytest.mark.asyncio
    async def test_ip_fetcher_retry_success(self):
        """Test IP fetcher retry mechanism."""
        from app.core.ip_fetcher import IPFetcher

        with patch("httpx.AsyncClient") as MockClient:
            # First call fails, second succeeds
            mock_response_success = Mock()
            mock_response_success.text = "1.1.1.1"
            mock_response_success.raise_for_status = Mock()
            
            mock_client = MockClient.return_value.__aenter__.return_value
            mock_client.get = AsyncMock(
                side_effect=[Exception("First fail"), mock_response_success]
            )

            fetcher = IPFetcher()
            ip = await fetcher.get_current_ip()
            
            assert ip == "1.1.1.1"


class TestProviders:
    """Test provider implementations."""

    @pytest.mark.asyncio
    async def test_cloudflare_provider_success(self):
        """Test Cloudflare provider successful update."""
        from app.providers.cloudflare import CloudflareProvider
        from app.schemas.providers import DomainConfig

        with patch("httpx.AsyncClient") as MockClient:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json = Mock(return_value={"success": True})
            
            mock_client = MockClient.return_value.__aenter__.return_value
            mock_client.put = AsyncMock(return_value=mock_response)

            provider = CloudflareProvider(auth_token="test_token")
            config = DomainConfig(
                name="test.com",
                zone_id="zone123",
                record_id="rec456",
                proxied=False
            )
            
            result = await provider.update_record("1.2.3.4", config)
            assert result is True

    @pytest.mark.asyncio
    async def test_dynu_provider_success(self):
        """Test Dynu provider successful update."""
        from app.providers.dynu import DynuProvider
        from app.schemas.providers import DomainConfig

        with patch("httpx.AsyncClient") as MockClient:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json = Mock(return_value={"statusCode": 200})
            
            mock_client = MockClient.return_value.__aenter__.return_value
            mock_client.post = AsyncMock(return_value=mock_response)

            provider = DynuProvider(auth_token="test_token")
            config = DomainConfig(
                name="test.com",
                id="123456"
            )
            
            result = await provider.update_record("1.2.3.4", config)
            assert result is True
