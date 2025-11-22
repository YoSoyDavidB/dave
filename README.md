# 🤖 Dave

Your AI friend for productivity and English learning.

## Features

- 💬 Natural conversation with a friendly AI
- 📝 Obsidian vault integration (PARA method)
- 🇬🇧 English correction and learning
- 📊 Progress tracking dashboard

## Tech Stack

- **Backend**: Python 3.11, FastAPI, OpenRouter
- **Frontend**: React 18, Vite, TypeScript, Tailwind CSS
- **Database**: Qdrant (vectors), Neo4j (graph), Redis (cache)
- **Infrastructure**: Docker, GitHub Actions

## Getting Started

### Prerequisites

- Python 3.11+
- Node.js 20+
- Docker & Docker Compose
- Poetry (Python package manager)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/YOUR_USERNAME/dave.git
cd dave
```

2. Copy environment file:
```bash
cp .env.example .env
# Edit .env with your API keys
```

3. Install dependencies:
```bash
make install
```

### Development

Start the development environment:

```bash
# Start backend + Redis
make dev

# In another terminal, start frontend
cd frontend && npm run dev
```

- Backend: http://localhost:8000
- Frontend: http://localhost:5173
- API Docs: http://localhost:8000/docs

### Testing

```bash
make test
```

### Linting

```bash
make lint
```

## Project Structure

```
dave/
├── backend/           # FastAPI backend
│   ├── src/
│   │   ├── api/       # API routes
│   │   ├── core/      # Business logic
│   │   ├── tools/     # Agent tools
│   │   └── infrastructure/  # External services
│   └── tests/
├── frontend/          # React frontend
│   ├── src/
│   │   ├── pages/
│   │   ├── components/
│   │   ├── hooks/
│   │   └── stores/
└── docker-compose.yml
```

## License

MIT
