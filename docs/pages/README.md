# IP-HOP Documentation

This directory contains the full documentation for IP-HOP built with MkDocs Material.

## Structure

```
docs/
├── mkdocs.yml          # MkDocs configuration
├── requirements.txt    # Python dependencies  
├── pages/             # Documentation pages
│   ├── index.md       # Home page
│   ├── getting-started.md
│   ├── installation/  # Installation guides
│   ├── configuration/ # Configuration reference
│   ├── api/          # API documentation
│   ├── troubleshooting.md
│   └── contributing.md
└── site/             # Generated site (gitignored)
```

## Local Development

### Setup

```bash
# Navigate to docs directory
cd docs

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Serve Locally

```bash
cd docs
source venv/bin/activate
mkdocs serve
```

Visit: `http://127.0.0.1:8000/ip-hop/`

### Build Static Site

```bash
source venv-docs/bin/activate
cd docs
mkdocs build
```

Output in `docs/site/` directory.

## Deployment

Documentation is automatically deployed to GitHub Pages via GitHub Actions when changes are pushed to `main` branch.

**Live URL**: https://taoshan98.github.io/ip-hop/

## Contributing to Docs

1. Edit markdown files in `pages/` directory
2. Test locally with `mkdocs serve`
3. Commit and push changes
4. GitHub Actions will automatically deploy

## MkDocs Commands

- `mkdocs serve` - Start development server
- `mkdocs build` - Build static site
- `mkdocs --help` - Show all commands
