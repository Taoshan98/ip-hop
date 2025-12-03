# Changelog

All notable changes to IP-HOP will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Future features will be listed here

## [1.0.0] - 2025-11-30

### Added
- Initial stable release of IP-HOP
- FastAPI backend with async architecture
- Next.js frontend with TypeScript
- Multi-provider DDNS support (Cloudflare, Dynu)
- Cron-based domain update scheduling
- Encrypted credential storage
- JWT authentication with HttpOnly cookies
- Comprehensive test suite (73 tests)
- Docker deployment with multi-stage builds
- GitHub Actions CI/CD pipeline
- Security scanning with Trivy
- Health check endpoints

### Security
- Mandatory ENCRYPTION_KEY for credential storage
- Non-root user in Docker containers
- HttpOnly cookie implementation
- Environment-based secrets management

### Infrastructure
- Alpine-based Docker images (~200MB)
- Multi-architecture support (amd64, arm64)
- GitHub Container Registry publishing
- Automated testing on PRs and main branch

---

## Version History

- **v1.0.0** (2025-11-30): Initial stable release
