# Chef Prompt: Remity - Next-Generation Remittance Platform

## Project Overview
Create a complete, production-ready remittance platform called "Remity" that allows users to send money internationally with competitive rates and transparent fees. The platform should be inspired by Wise.com's design and functionality.

## Tech Stack Requirements
- **Backend**: FastAPI with Python 3.9+
- **Frontend**: React with TypeScript
- **Database**: PostgreSQL with SQLAlchemy ORM and Alembic migrations
- **Authentication**: JWT tokens with bcrypt password hashing
- **Containerization**: Docker and Docker Compose for local development
- **Deployment**: Kubernetes (GKE) with Helm charts
- **API Documentation**: OpenAPI/Swagger
- **Testing**: pytest for backend, Jest for frontend

## Core Features

### 1. User Authentication & Management
- User registration with email verification
- Secure login with JWT tokens
- Password reset functionality
- User profile management
- Role-based access (regular users, admins)

### 2. Landing Page (Wise.com inspired)
- Modern, clean design with hero section
- Real-time currency calculator
- Features showcase (transparency, security, regulation)
- Customer testimonials
- How it works section
- Security and compliance information
- Call-to-action buttons for registration

### 3. Currency Calculator
- Real-time exchange rate display
- Fee transparency (show exact fees)
- Support for major currency pairs (USD→EUR, USD→MXN, USD→PHP, etc.)
- Historical rate charts
- Comparison with traditional banks

### 4. User Dashboard
- Transaction history
- Saved recipients
- Account balance
- Transfer status tracking
- Profile settings
- Security settings

### 5. Admin Dashboard
- Pending transaction approvals
- User management
- System statistics
- Transaction monitoring
- Compliance tools

### 6. Transaction System
- Create new transfers
- Recipient management
- Payment method selection
- Transfer status tracking
- Email notifications
- Receipt generation

### 7. API Endpoints
- Authentication: `/api/v1/auth/login`, `/api/v1/auth/register`
- Users: `/api/v1/users/me`, `/api/v1/users/{id}`
- Transactions: `/api/v1/transactions/`, `/api/v1/transactions/{id}`
- Recipients: `/api/v1/recipients/`, `/api/v1/recipients/{id}`
- Admin: `/api/v1/admin/transactions`, `/api/v1/admin/users`

## Database Schema

### Users Table
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR UNIQUE NOT NULL,
    full_name VARCHAR NOT NULL,
    hashed_password VARCHAR NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    is_superuser BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

### Transactions Table
```sql
CREATE TABLE transactions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    recipient_id INTEGER REFERENCES recipients(id),
    amount DECIMAL(10,2) NOT NULL,
    currency_from VARCHAR(3) NOT NULL,
    currency_to VARCHAR(3) NOT NULL,
    exchange_rate DECIMAL(10,6) NOT NULL,
    fee_amount DECIMAL(10,2) NOT NULL,
    total_amount DECIMAL(10,2) NOT NULL,
    status VARCHAR(20) DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

### Recipients Table
```sql
CREATE TABLE recipients (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    full_name VARCHAR NOT NULL,
    email VARCHAR,
    phone VARCHAR,
    bank_name VARCHAR,
    account_number VARCHAR,
    routing_number VARCHAR,
    swift_code VARCHAR,
    country VARCHAR NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);
```

## Frontend Requirements

### Landing Page Components
- Header with navigation and CTA buttons
- Hero section with compelling copy
- Currency calculator with real-time rates
- Features section with icons
- Testimonials carousel
- Security section
- Footer with links

### Authentication Pages
- Login page with email/password
- Registration page with form validation
- Password reset page
- Clean, modern design inspired by Wise.com

### Dashboard Components
- Sidebar navigation
- Transaction cards
- Status indicators
- Action buttons
- Responsive design

### Admin Components
- Data tables for transactions/users
- Approval workflows
- Statistics cards
- Search and filter functionality

## Styling Requirements
- Modern, clean design inspired by Wise.com
- Blue primary color (#00b9ff)
- Responsive design for mobile/tablet/desktop
- Smooth animations and transitions
- Professional typography
- Consistent spacing and layout

## Security Requirements
- JWT token authentication
- Password hashing with bcrypt
- CORS configuration for frontend-backend communication
- Input validation and sanitization
- Rate limiting
- HTTPS enforcement

## Docker Configuration
- Multi-stage builds for optimization
- Nginx for frontend serving
- PostgreSQL database
- Environment variable management
- Health checks

## Kubernetes Deployment
- Separate Helm charts for frontend and backend
- Ingress configuration for routing
- Database persistence
- Secret management
- Horizontal pod autoscaling

## Testing Requirements
- Unit tests for all API endpoints
- Integration tests for database operations
- Frontend component testing
- E2E testing for critical user flows

## Performance Requirements
- API response times under 200ms
- Frontend load times under 3 seconds
- Database query optimization
- Caching strategies
- CDN for static assets

## Monitoring & Logging
- Structured logging
- Error tracking
- Performance monitoring
- Health check endpoints

## Documentation
- API documentation with OpenAPI
- README with setup instructions
- Deployment guides
- Architecture diagrams

## Additional Features
- Email notifications for transactions
- PDF receipt generation
- Multi-language support (English/Spanish)
- Mobile-responsive design
- Progressive Web App capabilities
- Real-time notifications
- Dark mode support

## File Structure
```
remity/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── core/
│   │   ├── crud/
│   │   ├── db/
│   │   ├── models/
│   │   └── schemas/
│   ├── alembic/
│   ├── tests/
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── services/
│   │   └── contexts/
│   ├── public/
│   ├── Dockerfile
│   └── package.json
├── k8s/
│   ├── remity-backend-chart/
│   └── remity-frontend-chart/
└── docker-compose.yml
```

## Implementation Notes
- Use FastAPI's automatic OpenAPI generation
- Implement proper error handling and status codes
- Follow RESTful API conventions
- Use TypeScript for type safety
- Implement proper form validation
- Use React hooks for state management
- Implement proper loading states
- Add comprehensive error boundaries
- Use environment variables for configuration
- Implement proper logging throughout

## Success Criteria
- Application runs locally with Docker Compose
- All API endpoints return proper responses
- Frontend displays correctly with responsive design
- Authentication flow works end-to-end
- Database migrations run successfully
- Tests pass with good coverage
- Application can be deployed to Kubernetes
- Performance meets requirements
- Security best practices are followed

Please create this application with production-ready code quality, comprehensive error handling, and a focus on user experience. The application should be immediately deployable and maintainable.
