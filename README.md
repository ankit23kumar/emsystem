
# EMSystem — Employee Management System

EMSystem is a full-stack employee management application built with a **Django REST-style JSON backend and a separate Vue 3 frontend**. It demonstrates user authentication, account management, profile updates, and user administration.

The project is organized into independent backend and frontend applications to keep the code maintainable and make each part easier to develop, test, and understand.

## Project Architecture

```text
emsystem/
├── README.md
├── emsystem-backend/
│   ├── manage.py
│   └── README.md
└── emsystem-frontend/
    ├── package.json
    └── README.md
```

- **Backend:** Django, Python, MySQL, JSON APIs, and JWT authentication.
- **Frontend:** Vue 3, Vite, Vue Router, Axios, JavaScript, and CSS.
- **Communication:** The frontend sends HTTP requests to the backend API.

Each application has its own dependencies, configuration, and documentation.

## Features

### Authentication and Account Management

- User registration and login
- JWT-based authentication
- Password reset
- Account validity and expiration checks
- Account renewal and reactivation
- Logout and protected frontend routes

### User Management

- View users with pagination
- Create users
- Update user information
- Delete users
- View and update profile information

### Backend

- JSON responses from Django views
- MySQL database integration
- Secure password hashing using Django's password-hashing utilities
- Input validation and error handling
- Automated backend tests

### Frontend

- Vue 3 single-page application
- Client-side routing
- Axios-based API communication
- Reusable components and service modules
- Form validation and user feedback
- Production builds using Vite

## Technology Stack

| Area               | Technologies            |
| ------------------ | ----------------------- |
| Backend language   | Python                  |
| Backend framework  | Django                  |
| Database           | MySQL                   |
| Authentication     | JWT with PyJWT          |
| Password security  | Django password hashing |
| Frontend framework | Vue 3                   |
| Build tool         | Vite                    |
| Routing            | Vue Router              |
| HTTP client        | Axios                   |
| Frontend language  | JavaScript              |
| Version control    | Git                     |

## Prerequisites

Install the following tools:

- Python 3.11 or a compatible project-configured version
- Node.js and npm compatible with the frontend's Vite version
- MySQL Server
- Git (optional, for version control)

## Getting Started

### 1. Set up the backend

Open a terminal and navigate to the backend directory:

```powershell
cd emsystem-backend
```

Activate the existing Python virtual environment:

```powershell
.\env\Scripts\Activate.ps1
```

Install the backend dependencies using the project's dependency file, if provided. Configure MySQL and the Django settings according to `emsystem-backend/README.md`.

Start the Django development server:

```powershell
python manage.py runserver
```

Keep this terminal running.

### 2. Set up the frontend

Open another terminal:

```powershell
cd emsystem-frontend
npm install
npm run dev
```

Open the local URL displayed by Vite.

Ensure the frontend's configured API base URL matches the backend address and API configuration.

## Testing

### Backend tests

From the backend directory, with the virtual environment activated:

```powershell
python manage.py check
python manage.py test userauth
```

### Frontend production build

From the frontend directory:

```powershell
npm run build
```

The production output is generated in `emsystem-frontend/dist/`.

For additional instructions, see the component-specific READMEs.

## API Overview

The backend exposes JSON endpoints for authentication, user management, and account operations.

| Endpoint                               | Purpose                             |
| -------------------------------------- | ----------------------------------- |
| `/api/`                              | API home/status                     |
| `/api/register`                      | Register a user                     |
| `/api/login`                         | Authenticate a user                 |
| `/api/user-list`                     | Retrieve paginated users            |
| `/api/user-create`                   | Create a user                       |
| `/api/update/<user_id>`              | Update a user                       |
| `/api/delete/<user_id>`              | Delete a user                       |
| ~~`/api/renew-account/<user_id>`~~ | ~~Renew an account~~              |
| ~~`/api/reactivate-account`~~      | ~~Reactivate an expired account~~ |
| `/api/me`                            | User's Profile                      |
| `/api/password-reset`                | Reset Password                      |

The endpoints shown above are a high-level overview. Refer to the backend URL configuration and backend README for supported HTTP methods, request formats, authorization requirements, and the exact password-reset endpoint.

## Security Notes

- Passwords are stored using Django's password-hashing utilities, not reversible encryption.
- Protected endpoints require valid authentication according to the backend's authorization rules.
- Never commit database passwords, signing keys, JWT secrets, tokens, or other credentials.
- Use environment variables or another secure configuration mechanism for secrets.
- Use appropriate production settings before deploying the application.

## Documentation

- **[Frontend README](emsystem-frontend/README.md)** — Vue setup, npm commands, frontend structure, and troubleshooting.
- **[Backend README](emsystem-backend/README.md)** — Django setup, MySQL configuration, API documentation, authentication, and backend testing.

## Development Status

This is a learning and development project for practicing full-stack application development, API integration, authentication, database operations, and testing.

## License

No license has been specified yet. Add a license before distributing the project if required.
