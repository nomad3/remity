# Remity.io MVP - Remittance Platform

This repository contains the Minimum Viable Product (MVP) for Remity.io, a platform designed to simplify international money transfers (remittances). It allows users to send money in their local fiat currency, which is then delivered to the recipient in their local fiat currency. Internally, the platform leverages cryptocurrencies (specifically stablecoins like USDC) to potentially optimize transfer speed and cost, although this aspect is simulated in the MVP.

**Core MVP Features:**

*   **Fiat-to-Fiat Interface:** Users interact only with familiar fiat currencies (e.g., USD -> MXN).
*   **User Registration & Login:** Secure authentication using JWT.
*   **KYC Verification (Placeholder):** Integration point for Know Your Customer checks (mandatory for real operation).
*   **Recipient Management:** Users can save and manage recipient details.
*   **Transaction Quoting:** Provides estimated exchange rates, fees, and delivery times before sending.
*   **Transaction Creation:** Initiates the remittance process, including payment intent creation (e.g., via Stripe).
*   **Transaction History:** Users can view their past transactions.
*   **Dockerized Environment:** Uses Docker Compose for easy local development setup.

## Tech Stack

*   **Backend:** Python 3.10+, FastAPI, SQLAlchemy (async with PostgreSQL), Pydantic, Alembic (migrations), Uvicorn.
*   **Frontend:** React (TypeScript), React Router, Axios (basic structure created).
*   **Database:** PostgreSQL
*   **Cache:** Redis (for potential future use like caching rates, sessions)
*   **Containerization:** Docker, Docker Compose
*   **(Planned) Infrastructure:** Terraform, Google Cloud Platform (GCP)

## Project Structure

```
remity-mvp/
├── backend/          # FastAPI application
│   ├── alembic/      # Database migration scripts
│   ├── app/          # Core application code
│   │   ├── api/      # API endpoints and routers
│   │   ├── core/     # Configuration, security
│   │   ├── crud/     # Database interaction logic
│   │   ├── db/       # Database session, base model
│   │   ├── models/   # SQLAlchemy ORM models
│   │   ├── schemas/  # Pydantic data validation schemas
│   │   └── services/ # External service integrations (TODO)
│   ├── tests/        # Unit and integration tests (TODO)
│   ├── .env          # Local environment variables (GITIGNORED)
│   ├── .env.example  # Example environment variables
│   ├── alembic.ini   # Alembic configuration
│   ├── Dockerfile    # Backend Docker image definition
│   ├── entrypoint.sh # Script to run migrations and start app
│   └── requirements.txt
├── frontend/         # React application
│   ├── public/       # Static assets, index.html
│   ├── src/          # React components, pages, services, etc.
│   ├── .env.example  # Example environment variables for React
│   ├── .gitignore
│   ├── Dockerfile    # Frontend Docker image definition
│   ├── package.json
│   └── tsconfig.json
├── infra/            # Terraform infrastructure code (TODO)
├── docs/             # Project documentation (TODO)
├── docker-compose.yml # Docker Compose configuration for local dev
└── README.md         # This file
```

## Setup and Running (Local Development)

**Prerequisites:**

*   Docker Desktop (or Docker Engine + Docker Compose) installed.
*   Git (for cloning)

**Steps:**

1.  **Clone the Repository:**
    ```bash
    git clone <repository-url>
    cd remity-mvp
    ```

2.  **Configure Environment Variables:**
    *   **Backend:** Copy `backend/.env.example` to `backend/.env`. Review the file and **replace placeholder values** (especially `JWT_SECRET_KEY`, Stripe keys, etc.) with your actual development/test credentials. Generate a strong `JWT_SECRET_KEY` using `openssl rand -hex 32`.
    *   **Frontend:** Copy `frontend/.env.example` to `frontend/.env.local`. Update `REACT_APP_STRIPE_PUBLISHABLE_KEY` if needed. (`.env.local` is gitignored).

3.  **Build and Run Services:**
    Use Docker Compose to build the images and start the containers:
    ```bash
    docker-compose up --build -d
    ```
    *   `--build`: Forces Docker to rebuild the images if Dockerfiles have changed.
    *   `-d`: Runs containers in detached mode (in the background).

    This command will:
    *   Build the `backend` and `frontend` Docker images.
    *   Start containers for `backend`, `frontend`, `db` (PostgreSQL), and `redis`.
    *   The `backend` container's entrypoint script will wait for the database, apply Alembic migrations automatically (`alembic upgrade head`), and then start the FastAPI server.
    *   The `frontend` container will install npm dependencies (if not already cached in the image) and start the React development server.

4.  **Accessing Services:**
    *   **Backend API:** `http://localhost:8000`
    *   **Backend API Docs (Swagger):** `http://localhost:8000/api/v1/docs`
    *   **Frontend App:** `http://localhost:3000`

5.  **Stopping Services:**
    ```bash
    docker-compose down
    ```
    To stop and remove volumes (like the database data):
    ```bash
    docker-compose down -v
    ```

## Database Migrations (Alembic)

Migrations are handled automatically on container startup by the `backend/entrypoint.sh` script (`alembic upgrade head`).

To manually generate a new migration after changing SQLAlchemy models (`backend/app/models/`):

1.  Ensure the containers are running (`docker-compose up -d`).
2.  Execute the Alembic revision command inside the running backend container:
    ```bash
    docker-compose exec backend alembic revision --autogenerate -m "Your migration message"
    ```
3.  Review the generated migration script in `backend/alembic/versions/`.
4.  Restart the backend container to apply the new migration:
    ```bash
    docker-compose restart backend
    ```
    (Alternatively, the migration will be applied the next time you run `docker-compose up`).

## Important Notes & Next Steps

*   **Security:** The current `.env` file contains example secrets. **Never commit real secrets.** Use secure methods for managing secrets in production (e.g., GCP Secret Manager, HashiCorp Vault). Webhook endpoints need robust signature validation.
*   **External Services:** The interactions with Binance, Stripe, KYC providers, and Off-Ramp providers are currently placeholders. These need to be implemented in `backend/app/services/` and called from the relevant API endpoints/tasks.
*   **Error Handling:** Implement more specific error handling and potentially a centralized exception handling mechanism.
*   **Testing:** Add comprehensive unit and integration tests for both backend and frontend.
*   **Frontend Development:** Build out the React components, routing, state management, and API integration based on the defined UX/UI.
*   **Infrastructure:** Implement the Terraform code in `infra/` to provision necessary GCP resources (VPC, Cloud SQL, MemoryStore, GCE/Cloud Run, Secret Manager, etc.).
*   **Production Dockerfiles:** Create optimized multi-stage Dockerfiles for production builds (smaller images, non-root users, etc.).
*   **CI/CD:** Set up a CI/CD pipeline (e.g., GitHub Actions, Cloud Build) for automated testing, building, and deployment.
