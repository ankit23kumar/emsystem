
# EMSystem — Employee Management System

EMSystem is a full-stack Employee Management System built using a **Django-based JSON API backend and a separate Vue 3 frontend**.

The application demonstrates full-stack development concepts, including user authentication, account management, profile operations, employee administration, and Role-Based Access Control (RBAC).

The project is organized into independent backend and frontend applications to maintain separation of concerns and make development, testing, and maintenance easier.

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

- **Backend:** Python, Django, MySQL, JSON APIs, and custom JWT authentication.
- **Frontend:** Vue 3, Vite, Vue Router, Axios, JavaScript, and CSS.
- **Communication:** The frontend communicates with the backend through HTTP requests.
- **Authorization:** Backend permission checks and role-based access control.

Each application maintains its own dependencies, configuration, and documentation.

## Features

### 1. Authentication and Account Management

- User registration and login
- Custom JWT-based authentication
- Password reset
- Secure password hashing
- Account validity and expiration checks
- Account renewal
- Account reactivation
- Logout and protected frontend routes

### 2. User Management

- View users with pagination
- Create users
- Update user information
- Delete users
- View and update profile information
- Assign roles during user creation
- Change or remove assigned roles

### 3. Role-Based Access Control (RBAC)

- Create and manage roles
- Retrieve available roles
- Update role information
- Delete roles
- Retrieve available permissions
- Assign permissions to roles
- Assign roles to users
- Change or remove user roles
- Permission-based access control
- Protection against unauthorized privilege escalation

### 4. Backend Features

- Django function-based JSON API views
- MySQL database integration
- Django ORM
- Custom JWT authentication using PyJWT
- Secure password hashing using Django utilities
- Input validation and error handling
- Permission-based endpoint protection
- Automated backend tests

### 5. Frontend Features

- Vue 3 single-page application
- Client-side routing using Vue Router
- Axios-based API communication
- Reusable Vue components
- Centralized API service modules
- Authentication state management
- Permission-aware user interface
- User and role management dashboard
- Form validation and toast notifications
- Production builds using Vite

## Technology Stack

| Area               | Technologies            |
| ------------------ | ----------------------- |
| Backend Language   | Python 3.11.5           |
| Backend Framework  | Django 5.2.18           |
| Database           | MySQL                   |
| Authentication     | JWT with PyJWT          |
| Password Security  | Django Password Hashing |
| API Responses      | Django JsonResponse     |
| Frontend Framework | Vue 3                   |
| Build Tool         | Vite                    |
| Routing            | Vue Router              |
| HTTP Client        | Axios                   |
| Frontend Language  | JavaScript              |
| Styling            | CSS                     |
| Version Control    | Git                     |

> **Architecture note:** The current backend uses Django function-based views and custom PyJWT authentication. Django REST Framework and SimpleJWT are not required by the current implementation.

## Prerequisites

Install the following tools before setting up the project:

- Python 3.11.x
- Node.js compatible with the installed Vite version
- npm
- MySQL Server
- Git (optional)

## Getting Started

Follow these steps to run both applications locally.

### 1. Clone or open the project

Navigate to the project directory:

```powershell
cd F:\Projects\Django_Project\emsystem
```

### 2. Set Up the Backend

Open a terminal in the backend directory:

```powershell
cd emsystem-backend
```

Activate the existing Python virtual environment:

```powershell
.\env\Scripts\Activate.ps1
```

Install backend dependencies:

```powershell
python -m pip install -r requirements.txt
```

Configure MySQL and Django database settings according to the backend README.

Run Django system checks and migrations:

```powershell
python manage.py check
python manage.py migrate
```

Start the Django development server:

```powershell
python manage.py runserver
```

Backend API root:

```text
http://127.0.0.1:8000/api/
```

Keep the backend terminal running.

Detailed instructions:

[Backend README](emsystem-backend/README.md)

### 3. Set Up the Frontend

Open another terminal and navigate to the frontend directory:

```powershell
cd F:\Projects\Django_Project\emsystem\emsystem-frontend
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

Ensure that the frontend API configuration matches the running Django backend.

Detailed instructions:

[Frontend README](emsystem-frontend/README.md)

## API Overview

The Django backend exposes JSON endpoints for authentication, user management, account operations, and role-based access control.

### Authentication and User Management

| HTTP Method | Endpoint                  | Purpose                               |
| ----------- | ------------------------- | ------------------------------------- |
| GET         | `/api/`                 | API home/status                       |
| POST        | `/api/register`         | Register a user                       |
| POST        | `/api/login`            | Authenticate a user                   |
| GET         | `/api/user-list`        | Retrieve paginated users              |
| POST        | `/api/user-create`      | Create a user                         |
| PUT         | `/api/update/<user_id>` | Replace user information              |
| PATCH       | `/api/update/<user_id>` | Partially update user information     |
| DELETE      | `/api/delete/<user_id>` | Delete a user                         |
| GET         | `/api/me`               | Retrieve authenticated user's profile |
| PATCH       | `/api/me`               | Update authenticated user's profile   |

### Account and Password Management

| Endpoint                         | Purpose                       |
| -------------------------------- | ----------------------------- |
| `/api/renew-account/<user_id>` | Renew an account              |
| `/api/reactivate-account`      | Reactivate an expired account |
| `/api/password-reset`          | Reset a user's password       |

### Roles and Permissions

| HTTP Method | Endpoint                        | Purpose                                 |
| ----------- | ------------------------------- | --------------------------------------- |
| GET         | `/api/permissions`            | Retrieve available permissions          |
| GET         | `/api/roles`                  | Retrieve roles                          |
| POST        | `/api/roles`                  | Create a role                           |
| GET         | `/api/roles/<role_id>`        | Retrieve role details                   |
| DELETE      | `/api/roles/<role_id>`        | Delete a role                           |
| PUT/PATCH   | `/api/roles/<role_id>/update` | Update role information                 |
| PATCH       | `/api/user/<user_id>/role`    | Assign, update, or remove a user's role |

**Note:** The API overview summarizes the current endpoint design. Refer to the backend URL configuration and individual views for exact supported methods, request formats, response structures, and permission requirements.

## Authentication and Authorization

EMSystem uses custom JWT authentication with PyJWT.

After successful login, the backend returns an access token.

Protected API requests must include the token:

```http
Authorization: Bearer <access_token>
```

The backend validates authentication and checks the permissions required for protected operations.

### Role-Based Access Control

Roles group permissions together. Users receive permissions through their assigned roles.

For example:

```text
User
  │
  └── Assigned Role
          │
          ├── Permission 1
          ├── Permission 2
          └── Permission 3
```

The frontend uses permission information to control the visibility of dashboard features and management actions.

**Important:** Frontend permission checks are not a security boundary. The backend independently validates authorization for protected API operations.

## Testing

### Backend Tests

Navigate to the backend directory and activate the virtual environment.

Run Django system checks:

```powershell
python manage.py check
```

Run the backend test suite:

```powershell
python manage.py test userauth
```

### Frontend Production Build

Navigate to the frontend directory:

```powershell
npm run build
```

The production build is generated inside:

```text
emsystem-frontend/dist/
```

Preview the production build locally:

```powershell
npm run preview
```

Refer to the individual README files for more detailed testing and troubleshooting instructions.

## Security Notes

- Passwords are stored using Django's password-hashing utilities, not reversible encryption.
- Protected endpoints require valid authentication.
- Backend permission checks enforce access control.
- Role assignment includes protection against unauthorized privilege escalation.
- Never commit database passwords, JWT signing keys, access tokens, or other credentials.
- Use environment variables or another secure configuration mechanism for sensitive settings.
- Never expose private backend credentials in frontend source code.
- Use appropriate production settings before deploying the application.

## Documentation

Detailed setup and implementation instructions are available in the individual application documentation.

- **[Backend README](emsystem-backend/README.md)** — Django setup, MySQL configuration, API documentation, authentication, roles, permissions, and backend testing.
- **[Frontend README](emsystem-frontend/README.md)** — Vue setup, npm commands, frontend structure, components, services, API integration, and troubleshooting.

## Development Status

EMSystem is a learning and development project focused on practicing full-stack application development.

It demonstrates practical concepts including:

- Django JSON API development
- Vue 3 frontend development
- Frontend and backend integration
- JWT authentication
- MySQL database operations
- User and account management
- Role-Based Access Control
- Permission management
- Automated backend testing
- Component-based frontend architecture

## License

No license has been specified yet.

Add an appropriate open-source license before distributing or publishing the project if required.

```

**Final recommendation:** Use this as the single parent README, and keep the two application-specific README files for detailed setup and implementation documentation. This gives your GitHub repository a clean, professional documentation structure.
```
