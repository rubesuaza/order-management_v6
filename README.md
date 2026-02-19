# Order Management System

A Python-based order management system following Hexagonal Architecture principles.

## Project Structure

```
src/order_management/
├── application/          # Application Layer (Use Cases)
│   ├── ports/          # Ports (Abstract Base Classes)
│   │   ├── input/      # Input Ports (Use Case interfaces)
│   │   └── output/     # Output Ports (Repository interfaces)
│   └── services/       # Use Case Implementations
├── domain/             # Domain Layer (Pure Business Logic)
│   ├── models/        # Domain Entities and Value Objects
│   └── exceptions/    # Domain-specific Exceptions
├── infrastructure/     # Infrastructure Layer (Adapters)
│   ├── adapters/
│   │   ├── input/     # Input Adapters (FastAPI Routers)
│   │   └── output/    # Output Adapters (SQLAlchemy Repositories)
│   └── config/        # Framework setup
└── main.py            # Application Entry Point
```

## Setup

### Prerequisites

- Python 3.11+
- Poetry

### Installation

1. Install dependencies:
```bash
poetry install
```

2. Activate the virtual environment:
```bash
poetry shell
```

3. Configure environment variables:
```bash
cp .env.example .env
# Edit .env with your database configuration
```

4. Run database migrations:
```bash
alembic upgrade head
```

5. Start the application:
```bash
uvicorn src.order_management.main:app --reload
```

## Testing

Run tests with:
```bash
pytest
```

## Development

- Format code: `black .`
- Type checking: `mypy src/order_management`
- Linting: `ruff check .`
