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
*   **Dockerized Environment:** Uses Docker Compose for easy local development setup with automatic database migrations.
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
│   ├── entrypoint.sh # Script to run migrations and start app
│   ├── pytest.ini    # Pytest configuration
│   └── requirements.txt
├── frontend/         # React application
│   ├── public/       # Static assets, index.html
│   ├── src/          # React components, pages, services, etc.
│   │   └── components/ # Homepage components added
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
    *   **Backend API:** `http://localhost:8001` (Note: Port changed from 8000 due to potential conflicts)
    *   **Backend API Docs (Swagger):** `http://localhost:8001/api/v1/docs`
    *   **Frontend App:** `http://localhost:3000`
    *   **Redis (from host):** `localhost:6380` (Note: Port changed from 6379)

5.  **Stopping Services:**
    ```bash
    docker-compose down
    ```
    To stop and remove volumes (like the database data):
    ```bash
    docker-compose down -v
    ```
    *(This removes containers, networks, and the database volume)*

## Environment Variables

*   **Backend (`backend/.env`):** Critical for database connection, JWT secrets, CORS origins, and external API keys. **MUST** be created from `.env.example` and populated with valid credentials (use test keys for development). **NEVER** commit the `.env` file. Key variables include:
    *   `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`, `POSTGRES_HOST`, `POSTGRES_PORT`
    *   `REDIS_HOST`, `REDIS_PORT`
    *   `JWT_SECRET_KEY` (Generate securely!)
    *   `BACKEND_CORS_ORIGINS` (e.g., `["http://localhost:3000"]`)
    *   `STRIPE_SECRET_KEY`, `STRIPE_PUBLISHABLE_KEY`, `STRIPE_WEBHOOK_SECRET`
    *   `BINANCE_API_KEY`, `BINANCE_API_SECRET` (For exchange rates)
    *   `KYC_PROVIDER_API_KEY`, `KYC_PROVIDER_WEBHOOK_SECRET` (e.g., Onfido, Veriff)
    *   `OFFRAMP_PROVIDER_API_KEY`, `OFFRAMP_PROVIDER_WEBHOOK_SECRET` (e.g., Arcus, Xendit)
*   **Frontend (`frontend/.env.local`):** Used for frontend-specific variables. Create from `.env.example`. Key variables include:
    *   `REACT_APP_API_BASE_URL` (Should point to the backend, e.g., `http://localhost:8001/api/v1`)
    *   `REACT_APP_STRIPE_PUBLISHABLE_KEY`

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
    (Alternatively, the migration will be applied automatically the next time you run `docker-compose up`).

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

The application includes admin-only endpoints (e.g., for transaction approval) protected by the `get_current_active_superuser` dependency. To create the first admin user:

1.  **Ensure Containers are Running:** Start the application stack if it's not already running:
    ```bash
    docker-compose up -d
    ```
2.  **Run the Creation Script:** Execute the `initial_data.py` script inside the running `backend` container using `docker-compose exec`. Replace the email and password with your desired admin credentials:
    ```bash
    docker-compose exec backend python app/initial_data.py --email your_admin_email@example.com --password YourSecurePassword123
    ```
    *   This script will either create a new user with the given credentials and mark them as a superuser, or update an existing user with that email to be a superuser.
    *   Choose a strong password (minimum 8 characters enforced by the script).
3.  **Log In:** You can now log in via the frontend (`http://localhost:3000/login`) or API (`http://localhost:8001/api/v1/auth/login`) using the admin credentials you just created. Requests made with this user's token will have superuser privileges.

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
*   `/transactions/`: List transaction history for the current user.
*   `/transactions/{id}`: Get details of a specific transaction.
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
    *   **Routing:** Basic routing using `react-router-dom` is set up in `App.tsx` for `/`, `/login`, `/register`, `/history`, and `/admin`.
    *   **Authentication:** A basic `AuthContext` manages login state, and `LoginPage`, `RegisterPage` provide forms. `ProtectedRoute` component exists for securing routes.
    *   **Admin Panel:** A placeholder layout (`AdminLayout`) and page (`PendingTransactions`) exist under `/admin`, but require UI implementation and API integration.
    *   **Needed:** Significant work remains on building functional user dashboard, transaction flow, KYC integration, admin panel UI components, state management (e.g., Zustand), and robust API service calls (`axios`).
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
