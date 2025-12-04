# Contributing

Thank you for considering contributing to IP-HOP! 🎉

## Ways to Contribute

- 🐛 Report bugs
- 💡 Suggest features
- 📝 Improve documentation
- 🔧 Submit code improvements
- 🌍 Add translations

## Development Setup

### Prerequisites

- Python 3.12+
- Node.js 20+
- Docker and Docker Compose

### Clone Repository

```bash
git clone https://github.com/Taoshan98/ip-hop.git
cd ip-hop
```

### Backend Development

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Run tests
pytest

# Run backend server
uvicorn app.main:app --reload
```

### Frontend Development

```bash
cd frontend
npm install

# Run tests
npm test

# Run dev server
npm run dev
```

## Pull Request Process

1. **Fork** the repository
2. **Create** a feature branch: `git checkout -b feature/amazing-feature`
3. **Make** your changes
4. **Run** tests: `pytest` and `npm test`
5. **Commit** with clear message: `git commit -m 'feat: add amazing feature'`
6. **Push** to branch: `git push origin feature/amazing-feature`
7. **Open** Pull Request

## Commit Convention

We use [Conventional Commits](https://www.conventionalcommits.org/):

- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation
- `style:` Formatting
- `refactor:` Code restructuring
- `test:` Adding tests
- `chore:` Maintenance

## Code Style

### Python

- Follow PEP 8
- Use type hints
- Run `black` for formatting
- Run `mypy` for type checking

### TypeScript/React

- Follow project ESLint config
- Use Prettier for formatting
- Write tests for new components

## Testing

All contributions should include tests:

- **Backend**: pytest tests in `backend/tests/`
- **Frontend**: Jest tests in `frontend/__tests__/`

Run all tests:

```bash
# Backend
cd backend && pytest

# Frontend
cd frontend && npm test
```

## Documentation

Update documentation when:

- Adding new features
- Changing configuration
- Modifying API endpoints

Documentation lives in `docs/` directory.

## Questions?

- 💬 Open a [Discussion](https://github.com/Taoshan98/ip-hop/discussions)
- 📧 Contact maintainers

Thank you for contributing! ❤️
