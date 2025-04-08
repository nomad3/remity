# Remity.io MVP - Remittance Platform

This repository contains the Minimum Viable Product (MVP) for Remity.io, a platform designed to simplify international money transfers (remittances). It allows users to send money in their local fiat currency, which is then delivered to the recipient in their local fiat currency. Internally, the platform leverages cryptocurrencies (specifically stablecoins like USDC) to potentially optimize transfer speed and cost, although this aspect is simulated in the MVP.

**Core MVP Features:**

*   **Fiat-to-Fiat Interface:** Users interact only with familiar fiat currencies (e.g., USD -> MXN).
*   **User Registration & Login:** Secure authentication using JWT.
*   **KYC Verification (Placeholder):** Integration point for Know Your Customer checks (mandatory for real operation).
*   **Recipient Management:** Users can save and manage recipient details.
*   **Transaction Quoting:** Provides estimated exchange rates, fees, and delivery times before sending.
*   **Transaction Creation:** Initiates the remittance process, including payment intent creation (e.g., via Stripe).
*   **Transaction History / Dashboard:** Users can view their past transactions on the dashboard. Admins see all transactions.
*   **Dockerized Environment:** Uses Docker Compose for easy local development setup with automatic database migrations and initial superuser creation.
*   **Manual Approval Workflow:** Includes an admin step to approve/reject transactions before processing.

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
│   │   └── services/ # External service integrations (PLACEHOLDERS)
│   ├── tests/        # Pytest unit/integration tests
│   │   ├── core/
│   │   ├── crud/
│   │   ├── api/
│   │   └── utils/
│   ├── .env          # Local environment variables (GITIGNORED)
│   ├── .env.example  # Example environment variables
│   ├── alembic.ini   # Alembic configuration
│   ├── Dockerfile    # Backend Docker image definition
│   ├── pytest.ini    # Pytest configuration
│   └── requirements.txt # NOTE: entrypoint.sh removed, logic moved to docker-compose
├── frontend/         # React application
│   ├── public/       # Static assets, index.html
│   ├── src/          # React components, pages, services, etc.
│   │   ├── components/ # Reusable UI parts
│   │   ├── contexts/   # React Context (e.g., AuthContext)
│   │   ├── pages/      # Top-level page components (Login, Register, Dashboard, Admin...)
│   │   ├── services/   # API interaction logic
│   │   └── App.tsx     # Main application component with routing
│   ├── .env.example  # Example environment variables for React
│   ├── .gitignore
│   ├── Dockerfile    # Frontend Docker image definition
│   ├── package.json
│   └── tsconfig.json
├── infra/            # Terraform infrastructure code (PLACEHOLDER)
├── docs/             # Project documentation (PLACEHOLDER)
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

2.  **Configure Environment Variables:**<>
    *   **Backend:** Copy `backend/.env.example` to `backend/.env`. Review the file and **replace placeholder values** (especially `JWT_SECRET_KEY`, Stripe keys, etc.) with your actual development/test credentials. Generate a strong `JWT_SECRET_KEY` using `openssl rand -hex 32`.
    *   **Frontend:** Copy `frontend/.env.example` to `frontend/.env.local`. Update `REACT_APP_STRIPE_PUBLISHABLE_KEY` if needed. (`.env.local` is gitignored).

3.  **Build and Run Services:**
    Use Docker Compose to build the images and start the containers (ensure you are in the `remity-mvp` directory):
    ```bash
    # Build images and start containers in detached mode
    docker-compose up --build -d
    ```
    *   `--build`: Rebuilds images if their source files (Dockerfile, code) have changed. Use `docker-compose build --no-cache` if you suspect caching issues.
    *   `-d`: Runs containers in detached mode (in the background).

    This command will:
    *   Build the `backend` and `frontend` Docker images.
    *   Start containers for `backend`, `frontend`, `db` (PostgreSQL), and `redis`.
    *   The `backend` container's `command` in `docker-compose.yml` will:
        *   Wait for the database to be ready.
        *   Apply Alembic migrations automatically (`alembic upgrade head`).
        *   Run the initial data script (`app.initial_data`) to create the default admin user (`admin@remity.io` / `simon144610`).
        *   Start the FastAPI server using Uvicorn.
    *   The `frontend` container will install npm dependencies (if not already cached in the image) and start the React development server.

4.  **Accessing Services:**
    *   **Backend API:** `http://localhost:8001` (Mapped from container port 8000)
    *   **Backend API Docs (Swagger):** `http://localhost:8001/docs` (FastAPI default) or `/api/v1/docs` if prefix applied correctly.
    *   **Frontend App:** `http://localhost:3000`
    *   **Redis (from host):** `localhost:6380` (Mapped from container port 6379)
    *   **PostgreSQL (from host):** `localhost:5432` (Use user/pass/db from `.env`)

5.  **Stopping Services:**
    ```bash
    docker-compose down
    ```
    To stop and remove volumes (like the database data), ensure you are in the `remity-mvp` directory:
    ```bash
    docker-compose down -v
    ```

## Environment Variables

*   **Root (`./.env`):** Contains variables needed by `docker-compose.yml` itself for variable substitution (primarily for the backend's startup command). Create this file and copy the `POSTGRES_*` variables from `backend/.env.example` into it. **NEVER** commit this file if it contains sensitive defaults (though in this case, they are development defaults).
*   **Backend (`backend/.env`):** Contains runtime secrets and configuration loaded directly by the backend container (via `env_file`). Critical for JWT secrets, external API keys, etc. **MUST** be created from `backend/.env.example` and populated. **NEVER** commit this file. Key variables include:
    *   `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`, `POSTGRES_HOST`, `POSTGRES_PORT`
    *   `REDIS_HOST`, `REDIS_PORT`
    *   `JWT_SECRET_KEY` (Generate securely!)
    *   `BACKEND_CORS_ORIGINS` (e.g., `["http://localhost:3000", "http://127.0.0.1:3000"]`)
    *   `STRIPE_SECRET_KEY`, `STRIPE_PUBLISHABLE_KEY`, `STRIPE_WEBHOOK_SECRET`
    *   `BINANCE_API_KEY`, `BINANCE_API_SECRET` (For exchange rates)
    *   `KYC_PROVIDER_API_KEY`, `KYC_PROVIDER_WEBHOOK_SECRET` (e.g., Onfido, Veriff)
    *   `OFFRAMP_PROVIDER_API_KEY`, `OFFRAMP_PROVIDER_WEBHOOK_SECRET` (e.g., Arcus, Xendit)
*   **Frontend (`frontend/.env.local`):** Used for frontend-specific variables. Create from `.env.example`. Key variables include:
    *   `REACT_APP_API_BASE_URL` (Should point to the backend's *host* port, e.g., `http://localhost:8001/api/v1`)
    *   `REACT_APP_STRIPE_PUBLISHABLE_KEY`

## Database Migrations (Alembic)

Migrations are handled automatically on container startup by the `command:` directive in `docker-compose.yml` (`alembic upgrade head`).

To manually generate a new migration after changing SQLAlchemy models (`backend/app/models/`):

1.  Ensure the containers are running (`docker-compose up -d`).
2.  Execute the Alembic revision command inside the running backend container, specifying the compose file if not in the `remity-mvp` directory:
    ```bash
    # From remity-mvp directory:
    docker-compose exec backend alembic -c /app/alembic.ini revision --autogenerate -m "Your migration message"

    # Or from parent directory:
    docker-compose -f remity-mvp/docker-compose.yml exec backend alembic -c /app/alembic.ini revision --autogenerate -m "Your migration message"
    ```
3.  Review the generated migration script in `backend/alembic/versions/`.
4.  The migration will be applied automatically the next time the backend container starts (e.g., via `docker-compose up --build -d`). You can also apply it manually if needed:
    ```bash
    docker-compose -f remity-mvp/docker-compose.yml exec backend alembic -c /app/alembic.ini upgrade head
    ```

## Running Tests

*   **Backend:**
    *   Ensure test dependencies (like `Faker`) are installed: `pip install Faker` (within the venv or add to `requirements.txt`).
    *   Make sure a separate test database URL is configured (e.g., via environment variables or a `.env.test` file loaded by `conftest.py`). The default in `conftest.py` appends `_test` to the main DB URL.
    *   Run tests using pytest from the `backend` directory (ensure venv is active or run via Docker):
        ```bash
        # Option 1: Using local venv
        cd backend
        # python -m venv .venv # If not already created
        # .\.venv\Scripts\Activate.ps1 # Or source .venv/bin/activate
        pip install Faker # If not in requirements
        pytest 
        
        # Option 2: Running inside the Docker container
        docker-compose exec backend pip install Faker # Install if needed
        docker-compose exec backend pytest
        ```
*   **Frontend:**
    *   Run tests using npm from the `frontend` directory:
        ```bash
        cd frontend
        npm test
        ```
    *   *(Note: Only a basic component rendering test exists currently).*

## API Authentication

*   Most API endpoints (except `/auth/register`, `/auth/login`, `/auth/refresh`, and webhooks) require authentication.
*   Authentication is handled via JWT (JSON Web Tokens).
*   After logging in via `/auth/login`, the client receives an `access_token` and a `refresh_token`.
*   The `access_token` must be included in the `Authorization` header of subsequent requests as a Bearer token:
    ```
    Authorization: Bearer <your_access_token>
    ```
*   Access tokens have a limited lifetime (default 30 minutes). Use the `refresh_token` with the `/auth/refresh` endpoint to obtain a new `access_token`.

## Creating an Admin User

The application includes admin-only endpoints (e.g., for transaction approval) protected by the `get_current_active_superuser` dependency.

**Automatic Creation:**
The default admin user (`admin@remity.io` / password `simon144610`) is created **automatically** when the backend container starts, as part of the `command:` in `docker-compose.yml`.

**Manual Creation/Update (Optional):**
If you need to create a different admin user or ensure an existing user is an admin:
1.  Ensure containers are running (`docker-compose up -d`).
2.  Execute the `initial_data.py` script inside the `backend` container, specifying the compose file if needed:
    ```bash
    # From remity-mvp directory:
    docker-compose exec backend python -m app.initial_data --email your_admin_email@example.com --password YourSecurePassword123

    # Or from parent directory:
    docker-compose -f remity-mvp/docker-compose.yml exec backend python -m app.initial_data --email your_admin_email@example.com --password YourSecurePassword123
    ```
    *   This script creates the user if they don't exist or updates an existing user to be a superuser.
    *   Choose a strong password (minimum 8 characters enforced by the script).
3.  **Log In:** You can log in via the frontend (`http://localhost:3000/login`) or API (`http://localhost:8001/api/v1/auth/login`) using the admin credentials.

## API Endpoints Overview

The backend exposes API endpoints under `/api/v1/`:

*   `/auth/register`: User registration.
*   `/auth/login`: User login (returns JWT).
*   `/auth/refresh`: Refresh access token.
*   `/users/me`: Get/Update current user profile.
*   `/recipients/`: List/Create recipients for the current user.
*   `/recipients/{id}`: Get/Update/Delete a specific recipient.
*   `/transactions/quote`: Get a transaction quote (rate, fees). Requires verified user.
*   `/transactions/`: Create a transaction (initiates payment). Requires verified user.
*   `/transactions/`: List transaction history (all for admin, own for regular user).
*   `/transactions/{id}`: Get details of a specific transaction (owner only).
*   `/admin/transactions/pending`: List transactions awaiting manual approval (Admin only).
*   `/admin/transactions/{id}/approve`: Approve a pending transaction (Admin only).
*   `/admin/transactions/{id}/reject`: Reject a pending transaction (Admin only).
*   *(Planned)* `/webhooks/...`: Endpoints to receive asynchronous updates from Stripe, KYC provider, Off-Ramp provider.

## Manual Approval Flow

1.  User creates a transaction via `/api/v1/transactions/`.
2.  User completes payment (e.g., via Stripe Elements using the `client_secret` returned).
3.  Stripe sends a webhook notification (`payment_intent.succeeded`) to the backend (TODO: Implement webhook endpoint).
4.  The webhook handler verifies the event and updates the transaction status to `PENDING_APPROVAL`.
5.  An administrator/operator uses an admin interface (TODO: Build frontend for this) to call `GET /api/v1/admin/transactions/pending` to see pending transactions.
6.  The operator reviews the transaction details.
7.  The operator calls either `POST /api/v1/admin/transactions/{id}/approve` or `POST /api/v1/admin/transactions/{id}/reject`.
8.  If approved, the status changes to `PROCESSING`, and the backend should trigger the next step (e.g., simulated crypto transfer, initiating off-ramp payout via external service).
9.  If rejected, the status changes to `MANUALLY_REJECTED`, and the backend should trigger appropriate actions (e.g., refund process, user notification).

## Important Notes & Next Steps

*   **Security:** The current `.env` file contains example secrets. **Never commit real secrets.** Use secure methods for managing secrets in production (e.g., GCP Secret Manager, HashiCorp Vault). Webhook endpoints need robust signature validation.
*   **External Services & Webhooks:**
    *   **Placeholders:** The core logic interacting with external services exists only as placeholder functions. Implementation is required using the respective service SDKs/APIs and API keys configured in `.env`. Planned services include:
        *   **On-Ramp Payment:** Stripe (Payment Intents API)
        *   **Exchange Rates:** Binance API
        *   **KYC Provider:** Onfido or Veriff (API + Webhooks)
        *   **Off-Ramp Payout (MXN):** SPEI provider (e.g., Arcus API - requires investigation)
        *   **Off-Ramp Payout (PHP):** GCash provider (e.g., Xendit API - requires investigation)
    *   **Webhooks:** Endpoints for receiving webhook notifications (e.g., payment success from Stripe, KYC status updates, payout status) are planned but **not yet implemented**. Secure webhook handling (signature validation) is crucial and must be added. The current manual approval flow depends on the payment webhook correctly updating the transaction status to `PENDING_APPROVAL`.
*   **Error Handling:** Basic error handling exists, but more specific exceptions and potentially a centralized handler should be implemented for robustness.
*   **Testing:** Initial backend unit tests for security and user CRUD, plus a basic frontend component test, are included. Coverage should be significantly expanded.
*   **Frontend Development:**
    *   **Homepage:** A basic structure with Header, Hero, Features, Calculator, and Footer components is implemented (`frontend/src/components/`).
    *   **Routing:** Routing using `react-router-dom` is set up in `App.tsx` for `/`, `/login`, `/register`, `/dashboard`, `/history`, and `/admin`.
    *   **Authentication:** `AuthContext` manages login state. `LoginPage`, `RegisterPage` provide forms. `ProtectedRoute` component secures routes.
    *   **Dashboard:** A basic `DashboardPage` exists, fetching and displaying transactions based on user role.
    *   **Admin Panel:** A placeholder layout (`AdminLayout`) and page (`PendingTransactions`) exist under `/admin`, but require UI implementation and API integration.
    *   **Needed:** Significant work remains on building the transaction creation flow, KYC integration UI, refining the dashboard, implementing the full admin panel UI/functionality, potentially adding state management (e.g., Zustand), and improving API service calls (`axios`).
*   **Infrastructure:** Implement the Terraform code in `infra/` to provision necessary GCP resources (VPC, Cloud SQL, MemoryStore, GCE/Cloud Run, Secret Manager, etc.).
*   **Production Dockerfiles:** Create optimized multi-stage Dockerfiles for production builds (smaller images, non-root users, etc.).
*   **CI/CD:** Set up a CI/CD pipeline (e.g., GitHub Actions, Cloud Build) for automated testing, building, and deployment.

## Security Considerations

*   **Environment Variables:** Sensitive data (API keys, JWT secret, DB credentials) MUST NOT be hardcoded. Use environment variables loaded via `.env` locally and a secure mechanism (like GCP Secret Manager or Vault) in production.
*   **Input Validation:** FastAPI uses Pydantic for robust input validation, protecting against many injection-style attacks at the edge. Ensure all incoming data is validated.
*   **Authentication/Authorization:** JWT is used for authentication. Ensure tokens have appropriate expiry times. Use FastAPI dependencies (`Depends`) to enforce authorization (e.g., `get_current_active_user`, `get_current_verified_user`, `get_current_active_superuser`).
*   **Password Hashing:** Passwords are hashed using `bcrypt` via `passlib`.
*   **HTTPS:** Ensure HTTPS is enforced in production (typically at the load balancer or ingress level) to protect data in transit.
*   **Rate Limiting:** Implement rate limiting on sensitive endpoints (login, registration, quote) to prevent brute-force attacks (e.g., using `slowapi`).
*   **Webhook Security:** Webhook endpoints MUST validate incoming request signatures using shared secrets to ensure they originate from the expected provider (e.g., Stripe, KYC provider).
*   **Dependency Scanning:** Regularly scan dependencies (both backend and frontend) for known vulnerabilities (e.g., using `pip-audit`, `npm audit`, Snyk, Dependabot).
*   **Docker Security:** Use minimal base images, run containers as non-root users in production, scan images for vulnerabilities.
*   **SQL Injection:** Using an ORM like SQLAlchemy with proper parameterization significantly reduces the risk of SQL injection compared to raw SQL queries. Avoid constructing queries manually with user input.
*   **Cross-Site Scripting (XSS):** Sanitize any user-generated content displayed in the frontend. React generally helps prevent XSS by default when rendering variables, but be cautious with `dangerouslySetInnerHTML`.
*   **Cross-Site Request Forgery (CSRF):** While less common for pure API backends consumed by SPAs using token auth, consider CSRF protection (e.g., double submit cookie) if session-based auth or traditional forms are ever introduced.
*   **Permissions:** Implement fine-grained permissions if needed beyond the basic user/superuser distinction.
