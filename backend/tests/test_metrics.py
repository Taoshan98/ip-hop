import pytest
from fastapi.testclient import TestClient
from datetime import datetime, timedelta, UTC
from app.models import Provider, Domain, IPHistory


@pytest.fixture
def test_provider(client: TestClient, auth_headers: dict) -> int:
    """Create a test provider and return its ID."""
    response = client.post(
        "/api/v1/providers",
        headers=auth_headers,
        json={
            "name": "Test Provider",
            "type": "cloudflare",
            "credentials": {"api_key": "test"},
            "is_enabled": True
        }
    )
    return response.json()["id"]


@pytest.fixture
def test_domains_with_history(client: TestClient, auth_headers: dict, test_provider: int, db):
    """Create test domains with IP history."""
    # Create domains
    domain1_resp = client.post(
        "/api/v1/domains",
        headers=auth_headers,
        json={
            "provider_id": test_provider,
            "domain_name": "test1.example.com",
            "external_id": "ext1",
            "config": {}
        }
    )
    
    domain2_resp = client.post(
        "/api/v1/domains",
        headers=auth_headers,
        json={
            "provider_id": test_provider,
            "domain_name": "test2.example.com",
            "external_id": "ext2",
            "config": {}
        }
    )
    
    domain1_id = domain1_resp.json()["id"]
    domain2_id = domain2_resp.json()["id"]
    
    # Add IP history entries directly to DB
    now = datetime.now(UTC)
    history_entries = [
        IPHistory(
            domain_id=domain1_id,
            ip_address="192.168.1.1",
            status="SUCCESS",
            timestamp=now - timedelta(hours=2),
            message="Updated successfully"
        ),
        IPHistory(
            domain_id=domain1_id,
            ip_address="192.168.1.2",
            status="SUCCESS",
            timestamp=now - timedelta(hours=1),
            message="Updated successfully"
        ),
        IPHistory(
            domain_id=domain2_id,
            ip_address="192.168.2.1",
            status="FAILED",
            timestamp=now - timedelta(hours=3),
            message="Update failed"
        ),
        IPHistory(
            domain_id=domain2_id,
            ip_address="192.168.2.1",
            status="SUCCESS",
            timestamp=now - timedelta(minutes=30),
            message="Updated successfully"
        ),
    ]
    db.add_all(history_entries)
    db.commit()
    
    return {
        "domain1_id": domain1_id,
        "domain2_id": domain2_id
    }


class TestMetricsEndpoints:
    """Test all metrics endpoints"""
    
    def test_dashboard_metrics(self, client: TestClient, auth_headers: dict, test_domains_with_history):
        """Test GET /metrics/dashboard endpoint"""
        response = client.get("/api/v1/metrics/dashboard", headers=auth_headers)
        assert response.status_code == 200
        
        data = response.json()
        assert "total_domains" in data
        assert "active_domains" in data
        assert "success_rate_24h" in data
        assert "total_updates_24h" in data
        assert "failed_updates_24h" in data
        assert "unique_ips_24h" in data
        assert "providers_stats" in data
        
        assert data["total_domains"] == 2
        assert data["total_updates_24h"] == 4
        assert data["failed_updates_24h"] == 1
        assert isinstance(data["success_rate_24h"], (int, float))
    
    def test_dashboard_metrics_unauthenticated(self, client: TestClient):
        """Test dashboard metrics requires authentication"""
        response = client.get("/api/v1/metrics/dashboard")
        assert response.status_code == 401
    
    def test_response_time_metrics(self, client: TestClient, auth_headers: dict, test_domains_with_history):
        """Test GET /metrics/response-time endpoint"""
        response = client.get("/api/v1/metrics/response-time", headers=auth_headers)
        assert response.status_code == 200
        
        data = response.json()
        assert "1h" in data
        assert "6h" in data
        assert "24h" in data
        
        for period in ["1h", "6h", "24h"]:
            assert "count" in data[period]
            assert "avg_time" in data[period]
            assert "min_time" in data[period]
            assert "max_time" in data[period]
    
    def test_ip_changes_metrics(self, client: TestClient, auth_headers: dict, test_domains_with_history):
        """Test GET /metrics/ip-changes endpoint"""
        response = client.get("/api/v1/metrics/ip-changes", headers=auth_headers)
        assert response.status_code == 200
        
        data = response.json()
        assert "total_changes_last_week" in data
        assert "average_changes_per_day" in data
        assert "domains" in data
        
        assert isinstance(data["domains"], list)
        assert len(data["domains"]) == 2
        
        for domain_data in data["domains"]:
            assert "domain_id" in domain_data
            assert "domain_name" in domain_data
            assert "changes_last_week" in domain_data
            assert "changes_per_day" in domain_data
        
        # domain1 has 2 different IPs, so 1 change
        domain1_data = next(d for d in data["domains"] if d["domain_name"] == "test1.example.com")
        assert domain1_data["changes_last_week"] == 1
    
    def test_provider_stats_metrics(self, client: TestClient, auth_headers: dict, test_domains_with_history):
        """Test GET /metrics/provider-stats endpoint"""
        response = client.get("/api/v1/metrics/provider-stats", headers=auth_headers)
        assert response.status_code == 200
        
        data = response.json()
        assert "providers" in data
        assert "total_providers" in data
        
        assert data["total_providers"] == 1
        assert len(data["providers"]) == 1
        
        provider_data = data["providers"][0]
        assert "provider_id" in provider_data
        assert "provider_name" in provider_data
        assert "provider_type" in provider_data
        assert "is_enabled" in provider_data
        assert "total_domains" in provider_data
        assert "updates_24h" in provider_data
        assert "successful_updates_24h" in provider_data
        assert "success_rate_24h" in provider_data
        
        assert provider_data["provider_name"] == "Test Provider"
        assert provider_data["total_domains"] == 2
        assert provider_data["updates_24h"] == 4
        assert provider_data["successful_updates_24h"] == 3
        assert provider_data["success_rate_24h"] == 75.0
    
    def test_uptime_metrics(self, client: TestClient, auth_headers: dict, test_domains_with_history):
        """Test GET /metrics/uptime endpoint"""
        response = client.get("/api/v1/metrics/uptime", headers=auth_headers)
        assert response.status_code == 200
        
        data = response.json()
        assert "uptime_24h" in data
        assert "uptime_7d" in data
        assert "total_requests_24h" in data
        assert "successful_requests_24h" in data
        assert "total_requests_7d" in data
        assert "successful_requests_7d" in data
        assert "scheduler_status" in data
        
        assert data["total_requests_24h"] == 4
        assert data["successful_requests_24h"] == 3
        assert data["uptime_24h"] == 75.0
        
        assert data["scheduler_status"] in ["running", "stopped"]
    
    def test_activity_timeline(self, client: TestClient, auth_headers: dict, test_domains_with_history):
        """Test GET /metrics/activity endpoint"""
        response = client.get("/api/v1/metrics/activity", headers=auth_headers)
        assert response.status_code == 200
        
        data = response.json()
        assert "activity" in data
        assert "count" in data
        
        assert data["count"] == 4
        assert len(data["activity"]) == 4
        
        for item in data["activity"]:
            assert "id" in item
            assert "domain_id" in item
            assert "domain_name" in item
            assert "ip_address" in item
            assert "status" in item
            assert "timestamp" in item
            assert "message" in item
        
        # Verify ordering (most recent first)
        timestamps = [item["timestamp"] for item in data["activity"]]
        assert timestamps == sorted(timestamps, reverse=True)
    
    def test_activity_timeline_with_limit(self, client: TestClient, auth_headers: dict, test_domains_with_history):
        """Test GET /metrics/activity with custom limit"""
        response = client.get("/api/v1/metrics/activity?limit=2", headers=auth_headers)
        assert response.status_code == 200
        
        data = response.json()
        assert data["count"] == 2
        assert len(data["activity"]) == 2
    
    def test_metrics_with_no_data(self, client: TestClient, auth_headers: dict):
        """Test metrics endpoints with no data"""
        # Test dashboard with no history
        response = client.get("/api/v1/metrics/dashboard", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["total_updates_24h"] == 0
        assert data["success_rate_24h"] == 0.0
        
        # Test uptime with no data
        response = client.get("/api/v1/metrics/uptime", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["uptime_24h"] == 100.0
        
        # Test IP changes with no data
        response = client.get("/api/v1/metrics/ip-changes", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["total_changes_last_week"] == 0
