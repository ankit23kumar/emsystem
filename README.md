# EMSystem — Employee Management System

EMSystem is a full-stack Employee Management System built using a **Django-based JSON API backend and a separate Vue 3 frontend**.

The application demonstrates user authentication, account management, profile operations, and employee administration.

The project is organized into independent backend and frontend applications to maintain clean separation of concerns and make development, testing, and maintenance easier.

## Project Architecture

```text
emsystem/
│
├── README.md
│
├── emsystem-backend/
│   ├── manage.py
│   └── README.md
│
└── emsystem-frontend/
    ├── package.json
    └── README.md
```

### Application Overview

- **Backend:** Django, Python, MySQL, JSON APIs, and JWT authentication.
- **Frontend:** Vue 3, Vite, Vue Router, Axios, JavaScript, and CSS.
- **Communication:** The frontend communicates with the backend through HTTP requests.

Each application maintains its own dependencies, configuration, and documentation.

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

### Backend Features

- JSON responses using Django views
- MySQL database integration
- Secure password hashing using Django's password-hashing utilities
- Input validation and error handling
- JWT-based authentication
- Automated backend tests

### Frontend Features

- Vue 3 single-page application
- Client-side routing using Vue Router
- Axios-based API communication
- Reusable components and service modules
- Form validation and user feedback
- Production builds using Vite

## Technology Stack

| Area               | Technologies            |
| ------------------ | ----------------------- |
| Backend Language   | Python                  |
| Backend Framework  | Django                  |
| Database           | MySQL                   |
| Authentication     | JWT with PyJWT          |
| Password Security  | Django Password Hashing |
| Frontend Framework | Vue 3                   |
| Build Tool         | Vite                    |
| Routing            | Vue Router              |
| HTTP Client        | Axios                   |
| Frontend Language  | JavaScript              |
| Styling            | CSS                     |
| Version Control    | Git                     |

## Prerequisites

Install the following tools before setting up the project:

- Python 3.11 or a compatible project-configured version
- Node.js and npm compatible with the installed Vite version
- MySQL Server
- Git (optional, for version control)

## Getting Started

Follow these steps to run the backend and frontend applications locally.

### 1. Set Up the Backend

Open a terminal and navigate to the backend directory:

```powershell
cd emsystem-backend
```

Activate the existing Python virtual environment:

```powershell
.\env\Scripts\Activate.ps1
```

Install the backend dependencies using the project's dependency file, if provided:

```powershell
python -m pip install -r requirements.txt
```

Configure MySQL and the Django database settings according to the backend documentation.

Run Django system checks and migrations:

```powershell
python manage.py check
python manage.py migrate
```

Start the Django development server:

```powershell
python manage.py runserver
```

The backend API will be available at:

```text
http://127.0.0.1:8000/api/
```

Keep this terminal running.

For additional backend setup instructions, refer to:

`emsystem-backend/README.md`

### 2. Set Up the Frontend

Open another terminal and navigate to the frontend directory:

```powershell
cd emsystem-frontend
```

Install frontend dependencies:

```powershell
npm install
```

Start the Vue development server:

```powershell
npm run dev
```

Open the local URL displayed by Vite in your browser.

Ensure that the frontend's configured API base URL matches the running backend address and API configuration.

For additional frontend setup instructions, refer to:

`emsystem-frontend/README.md`

## Testing

### Backend Tests

From the backend directory, activate the virtual environment and execute:

```powershell
python manage.py check
python manage.py test userauth
```

### Frontend Production Build

From the frontend directory, execute:

```powershell
npm run build
```

The production build output is generated inside:

```text
emsystem-frontend/dist/
```

For more detailed testing and troubleshooting instructions, refer to the component-specific README files.

## API Overview

The backend exposes JSON endpoints for authentication, user management, profile operations, and account management.

| Endpoint                         | Purpose                                   |
| -------------------------------- | ----------------------------------------- |
| `/api/`                        | API home/status                           |
| `/api/register`                | Register a user                           |
| `/api/login`                   | Authenticate a user                       |
| `/api/user-list`               | Retrieve paginated users                  |
| `/api/user-create`             | Create a user                             |
| `/api/update/<user_id>`        | Update a user                             |
| `/api/delete/<user_id>`        | Delete a user                             |
| `/api/renew-account/<user_id>` | Renew an account                          |
| `/api/reactivate-account`      | Reactivate an expired account             |
| `/api/me`                      | Retrieve the authenticated user's profile |
| `/api/password-reset`          | Reset a password                          |

**Note:** This is a high-level endpoint overview. Refer to the backend URL configuration and backend README for supported HTTP methods, request formats, authorization requirements, and exact password-reset behavior.

## Security Notes

- Passwords are stored using Django's password-hashing utilities, not reversible encryption.
- Protected endpoints require valid authentication according to the backend's authorization rules.
- Never commit database passwords, signing keys, JWT secrets, access tokens, or other credentials.
- Use environment variables or another secure configuration mechanism for sensitive settings.
- Never expose private credentials in frontend source code.
- Use appropriate production settings before deploying the application.

## Documentation

Detailed setup and implementation instructions are available in the individual application documentation:

- **[Frontend README](emsystem-frontend/README.md)** — Vue setup, npm commands, frontend structure, API integration, and troubleshooting.
- **[Backend README](emsystem-backend/README.md)** — Django setup, MySQL configuration, API documentation, authentication, and backend testing.

## Development Status

EMSystem is a learning and development project focused on practicing full-stack application development.

It demonstrates practical concepts including:

- Backend API development
- Frontend and backend integration
- JWT authentication
- Database operations
- User and account management
- Automated testing

## License

No license has been specified yet.

Add an appropriate license before distributing or publishing the project if require

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

| Endpoint                              | Purpose                            |
| ------------------------------------- | ---------------------------------- |
| `/api/`                             | API home/status                    |
| `/api/register`                     | Register a user                    |
| `/api/login`                        | Authenticate a user                |
| `/api/user-list`                    | Retrieve paginated users           |
| `/api/user-create`                  | Create a user                      |
| `/api/update/<user_id>`             | Update a user                      |
| `/api/delete/<user_id>`             | Delete a user                      |
| ~~`/api/renew-account/<user_id>`~~ | ~~Renew an account~~              |
| ~~`/api/reactivate-account`~~      | ~~Reactivate an expired account~~ |
| `/api/me`                           | User's Profile                     |
| `/api/password-reset`               | Reset Password                     |

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
