# EMSystem Backend

The backend for **EMSystem (Employee Management System)** is built with Python and Django. It exposes JSON API endpoints consumed by the separate Vue 3 frontend.

The application uses MySQL for data storage, PyJWT for token-based authentication, and Django's password-hashing utilities for password security.

## Technology Stack

- Python 3.11.5
- Django 5.2.18
- MySQL
- PyJWT
- Django password hashing
- Django `JsonResponse` for JSON API responses
- Django's test framework

## Prerequisites

- Python installed and available in the terminal
- MySQL Server running
- A configured MySQL database and database user
- The project's Python virtual environment
- Git (optional)

## Project Setup

### 1. Open the backend directory

```powershell
cd F:\Projects\Django_Project\emsystem\emsystem-backend
```

### 2. Activate the virtual environment

The existing project environment is named `env`.

```powershell
.\env\Scripts\Activate.ps1
```

If PowerShell cannot activate the environment, verify that the `env` directory exists and review your local PowerShell execution-policy settings.

Confirm Python is available:

```powershell
python --version
```

### 3. Install dependencies

If the repository contains a `requirements.txt` file, install the declared dependencies:

```powershell
python -m pip install -r requirements.txt
```

If no dependency file exists, use the project's existing environment and dependency list. Do not replace working dependencies without checking compatibility.

### 4. Configure MySQL

Create or identify the MySQL database and database user required by the project.

Review the database configuration in Django's settings. Supply the correct database name, username, password, host, and port using the configuration method already adopted by the project.

**Security:** Do not put real database credentials in this README or commit them to source control.

### 5. Run Django checks

```powershell
python manage.py check
```

If database migrations are pending, review them and apply the appropriate migrations:

```powershell
python manage.py migrate
```

### 6. Start the development server

```powershell
python manage.py runserver
```

The default local development address is `http://127.0.0.1:8000/`.

The API home endpoint is:

```text
http://127.0.0.1:8000/api/
```

## API Endpoints

All endpoints use the `/api/` URL prefix. The following table summarizes the known endpoint behavior. Check the project's URL configuration and views for the exact HTTP methods and request formats.

| Endpoint                         | Purpose                       | Authentication               |
| -------------------------------- | ----------------------------- | ---------------------------- |
| `/api/`                        | API status/home               | Public                       |
| `/api/register`                | Register a new user           | Public                       |
| `/api/login`                   | Log in and receive a JWT      | Public                       |
| `/api/user-list`               | Retrieve paginated users      | Required                     |
| `/api/user-create`             | Create a user                 | Required                     |
| `/api/update/<user_id>`        | Update user information       | Required                     |
| `/api/delete/<user_id>`        | Delete a user                 | Required                     |
| `/api/renew-account/<user_id>` | Renew an account              | Required; owner-only renewal |
| `/api/reactivate-account`      | Reactivate an expired account | Credentials required         |
| `/api/me`                      | Load a user's own profile     | Required                     |
| `/api/password-reset`          | Reset a user's password      | Public                       |

Password-reset functionality is also implemented. Add its exact route, HTTP method, request body, and response details after verifying the relevant URL configuration and view.

### User Registration

Registration validates required fields, names, email, and password. Duplicate email addresses are rejected. Passwords are stored using Django's password-hashing utilities.

### Login and JWT Authentication

Successful login returns a JWT access token and user information. Protected requests must supply the token in the authorization header:

```http
Authorization: Bearer <access_token>
```

The backend uses its configured JWT expiration settings. Do not hardcode real tokens or signing secrets in the source code or documentation.

### User List and Pagination

The user-list endpoint supports pagination through query parameters:

```text
/api/user-list?page=1&page_size=10
```

The default page is `1` and the default page size is `10`. The configured page-size range is 1–100.

The user-list response excludes password fields.

### User Updates

The update endpoint supports `PUT` and `PATCH`:

- `PUT` requires all supported editable fields.
- `PATCH` allows partial updates.
- Editable profile fields include `first_name`, `last_name`, and `email`.

Refer to the current view implementation for the exact response format and validation rules.

### Account Renewal and Reactivation

Account renewal requires authentication and is restricted to the account owner.

Account reactivation verifies the user's credentials before reactivating an expired account. Successful reactivation issues a fresh token according to the current implementation.

### Current User Profile

**Endpoint:** `/api/me`

This endpoint is connected to the `my_profile` view. It is intended for retrieving the authenticated user's profile.

Authentication requirements and supported HTTP methods should be confirmed from the view implementation.

### Password Reset

**Endpoint:** `/api/password-reset`

This endpoint is connected to the `reset_password` view. It provides the password-reset functionality implemented in the backend.

Refer to the view's validation logic for the required request fields, password rules, response codes, and authentication requirements. Never include actual passwords, JWT tokens, or other secrets in documentation or logs.

## Password Security

- Use Django's password-hashing utilities when storing passwords.
- Verify passwords using Django's password-checking utilities.
- Never store plaintext passwords.
- Do not use reversible encryption as a replacement for password hashing.
- Do not log passwords, access tokens, or sensitive authentication details.

## Automated Testing

Run the backend tests from this directory:

```powershell
python manage.py test userauth
```

Run the Django system checks separately:

```powershell
python manage.py check
```

The test suite covers backend behavior, including authentication, validation, account operations, and password-reset functionality.

Tests may create a separate test database. Ensure the MySQL account has the necessary test-database permissions and follow Django's prompts carefully if a test database already exists.

## Troubleshooting

### `No module named 'django'`

Activate the correct virtual environment:

```powershell
.\env\Scripts\Activate.ps1
```

Then check the installation:

```powershell
python -m pip show django
```

### MySQL connection errors

Verify that:

- MySQL Server is running.
- The configured database exists.
- The database credentials are correct.
- The database user has the required permissions.
- Django's database settings match the local configuration.

### Authentication errors

Check that:

- The authorization header uses the `Bearer` scheme.
- The token is valid and has not expired.
- The request targets the correct endpoint.
- The request body uses the expected JSON fields.

### Test database errors

Review the error carefully before deleting or recreating a test database. Confirm that it is the test database and not your development database.

## Related Documentation

- **[Universal README](../README.md)** — full project overview and setup sequence.
- **[Frontend README](../emsystem-frontend/README.md)** — Vue installation, API integration, and frontend commands.
