
# EMSystem Backend

The **EMSystem (Employee Management System) Backend** is a Django-based JSON API. It handles user registration, authentication, profile operations, user administration, account renewal/reactivation, and password-reset functionality. The API is designed to be consumed by the separate Vue 3 frontend.

## Technology Stack

| Technology              | Purpose                                  |
| ----------------------- | ---------------------------------------- |
| Python 3.11.5           | Backend language                         |
| Django 5.2.18           | Web framework                            |
| MySQL                   | Relational database                      |
| PyJWT                   | JWT-based authentication                 |
| Django `JsonResponse` | JSON API responses                       |
| Django password hashing | Secure password storage and verification |
| Django test framework   | Automated backend tests                  |

> This project currently uses Django function-based views and Django JSON responses. It does not assume Django REST Framework or SimpleJWT.

## Project Location

```text
F:\Projects\Django_Project\emsystem\
└── emsystem-backend\
```

## Prerequisites

- Python 3.11.x
- MySQL Server
- Configured MySQL database and database user
- Existing Python virtual environment (`env`)
- Git (optional)

## Setup and Installation

Run the following commands in PowerShell.

### 1. Open the backend directory

```powershell
cd F:\Projects\Django_Project\emsystem\emsystem-backend
```

### 2. Activate the virtual environment

```powershell
.\env\Scripts\Activate.ps1
```

Check the Python version:

```powershell
python --version
```

### 3. Install dependencies

If the project contains `requirements.txt`:

```powershell
python -m pip install -r requirements.txt
```

### 4. Configure MySQL

Configure your database settings using the existing project configuration.

You will need:

- Database name
- Database username
- Database password
- Database host
- Database port

**Important:** Never commit database credentials, JWT secrets, or passwords to GitHub.

### 5. Run Django checks and migrations

```powershell
python manage.py check
python manage.py migrate
```

### 6. Start the development server

```powershell
python manage.py runserver
```

Default development server:

```text
http://127.0.0.1:8000/
```

API root:

```text
http://127.0.0.1:8000/api/
```

## API Endpoints

All API routes use the `/api/` prefix.

| Endpoint                         | Purpose                               | Access                         |
| -------------------------------- | ------------------------------------- | ------------------------------ |
| `GET /api/`                    | API status/home                       | Public                         |
| `/api/register`                | Register a new user                   | Public                         |
| `/api/login`                   | Authenticate and receive JWT          | Public                         |
| `/api/user-list`               | Retrieve paginated users              | JWT required                   |
| `/api/user-create`             | Create a user                         | JWT required                   |
| `/api/update/<user_id>`        | Update user information               | JWT required                   |
| `/api/delete/<user_id>`        | Delete a user                         | JWT required                   |
| `/api/renew-account/<user_id>` | Renew an account                      | JWT required; own account only |
| `/api/reactivate-account`      | Reactivate an expired account         | Credentials required           |
| `/api/me`                      | Retrieve authenticated user's profile | JWT required                   |
| `/api/password-reset`          | Reset a user's password               | Public route                   |

For routes where the HTTP method is not shown, check the current URL configuration and view before constructing a request.

The exact request fields and response formats for `/api/me` and `/api/password-reset` should be verified against their current implementations.

## Authentication

After successful login, the API returns a JWT access token.

Send the token with protected requests using the Bearer authentication scheme:

```http
Authorization: Bearer <access_token>
```

Keep access tokens private. Never commit real tokens to source control.

## User List and Pagination

The user-list endpoint supports pagination through query parameters:

```text
/api/user-list?page=1&page_size=10
```

- Default page: `1`
- Default page size: `10`
- Page-size range: `1` to `100`
- Password fields are excluded from user-list responses.

The response includes pagination information such as the current page and total user count.

## User Registration and Login

Registration validates required user information:

- First name
- Last name
- Email
- Password

Additional validation includes:

- Name length validation
- Email validation
- Password length validation
- Duplicate email prevention

Passwords are stored using Django's password-hashing utilities.

Login verifies the supplied credentials. An expired account is handled separately from invalid credentials.

Successful login returns an access token and user information.

Refer to the current backend views for exact JSON request and response structures.

## User Updates and Account Operations

### Update User

The update endpoint supports:

- `PUT` – Requires all supported editable fields.
- `PATCH` – Allows partial updates.

Editable fields include:

- `first_name`
- `last_name`
- `email`

Password changes are not part of this profile-update operation.

### Renew Account

Account renewal requires a valid JWT and is restricted to the authenticated account owner.

### Reactivate Account

Account reactivation verifies the user's credentials before reactivating an expired account.

The current implementation issues a fresh token after successful reactivation.

### Profile and Password Reset

The following endpoints are included:

- `/api/me`
- `/api/password-reset`

Check their corresponding `my_profile` and `reset_password` views for exact HTTP methods, required JSON fields, validation rules, authentication behavior, and response codes.

## Password Security

- Passwords are hashed using Django's password-hashing utilities.
- Password verification uses Django's password-checking utilities.
- Plaintext passwords are never stored.
- Reversible encryption should not be used as a substitute for password hashing.
- Passwords and JWT tokens should never be logged.

## Automated Testing

Run the backend test suite:

```powershell
python manage.py test userauth
```

Run Django system checks:

```powershell
python manage.py check
```

The test suite covers backend behavior such as authentication, validation, account operations, and password-reset functionality.

Django may create a separate test database. Ensure your MySQL user has the required permissions.

**Important:** Always verify which database is affected before removing or recreating any database.

## Troubleshooting

### No module named 'django'

Activate the project's virtual environment:

```powershell
.\env\Scripts\Activate.ps1
```

Check whether Django is installed:

```powershell
python -m pip show django
```

### MySQL connection errors

Check:

- MySQL Server is running.
- Database exists.
- Database credentials are correct.
- Django database settings match your local configuration.

### Authentication errors

Check:

- Authorization header is included.
- Bearer token is valid.
- Token has not expired.
- Correct API endpoint is being accessed.

### Test database errors

Read the Django error carefully and verify which database is affected before making changes.

Do not delete the development database to resolve a test-database issue.

## Related Documentation

- [Project Overview](../README.md)
- [EMSystem Frontend](../emsystem-frontend/README.md)
