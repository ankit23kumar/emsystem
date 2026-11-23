# EMSystem Backend

The **EMSystem (Employee Management System) Backend** is a Django-based REST-style JSON API that provides authentication, user management, account operations, password reset, and role-based access control (RBAC).

It is developed using Django function-based views and Django `JsonResponse`. The backend communicates with a separate Vue 3 frontend through HTTP API requests.

## Features

- User registration and login
- Custom JWT authentication using PyJWT
- Password hashing and verification
- User listing with pagination
- Create, update, and delete users
- User profile retrieval and updates
- Account renewal and reactivation
- Password reset
- Role management
- Permission management
- Assign and update user roles
- Permission-based endpoint protection
- Role-based access control
- Automated backend tests

## Technology Stack

| Technology              | Purpose                      |
| ----------------------- | ---------------------------- |
| Python 3.11.5           | Backend programming language |
| Django 5.2.18           | Backend framework            |
| MySQL                   | Relational database          |
| PyJWT                   | JWT authentication           |
| Django `JsonResponse` | JSON API responses           |
| Django password hashing | Secure password storage      |
| Django ORM              | Database operations          |
| Django Test Framework   | Automated testing            |

> **Architecture note:** This project currently uses Django function-based views and custom JWT authentication. It does not depend on Django REST Framework or SimpleJWT for its current API implementation.

## Project Location

```text
F:\Projects\Django_Project\emsystem\
└── emsystem-backend\
```

## Prerequisites

Install or configure the following:

- Python 3.11.x
- Django 5.2.x
- MySQL Server
- MySQL database and database user
- Python virtual environment
- Git (optional)

## Installation and Setup

### 1. Navigate to the backend directory

```powershell
cd F:\Projects\Django_Project\emsystem\emsystem-backend
```

### 2. Activate the virtual environment

```powershell
.\env\Scripts\Activate.ps1
```

Verify Python:

```powershell
python --version
```

### 3. Install dependencies

If `requirements.txt` is available:

```powershell
python -m pip install -r requirements.txt
```

### 4. Configure MySQL

Configure the database connection in the Django project settings.

You will need:

- Database name
- Database username
- Database password
- Database host
- Database port

Keep database credentials and JWT signing secrets in environment variables or another secure configuration mechanism.

**Never commit passwords, database credentials, or JWT secrets to GitHub.**

### 5. Run system checks and migrations

```powershell
python manage.py check
python manage.py migrate
```

### 6. Start the development server

```powershell
python manage.py runserver
```

Backend development URL:

```text
http://127.0.0.1:8000/
```

API root:

```text
http://127.0.0.1:8000/api/
```

## API Endpoints

All API endpoints use the `/api/` prefix.

### Authentication and User Management

| HTTP Method | Endpoint                  | Purpose                               | Access                 |
| ----------- | ------------------------- | ------------------------------------- | ---------------------- |
| GET         | `/api/`                 | API status                            | Public                 |
| POST        | `/api/register`         | Register a new user                   | Public                 |
| POST        | `/api/login`            | Authenticate and receive JWT          | Public                 |
| GET         | `/api/user-list`        | Retrieve paginated users              | JWT + `users.read`   |
| POST        | `/api/user-create`      | Create a user                         | JWT + `users.create` |
| PUT         | `/api/update/<user_id>` | Replace editable user information     | JWT + `users.update` |
| PATCH       | `/api/update/<user_id>` | Partially update user information     | JWT + `users.update` |
| DELETE      | `/api/delete/<user_id>` | Delete a user                         | JWT + `users.delete` |
| GET         | `/api/me`               | Retrieve authenticated user's profile | JWT                    |
| PATCH       | `/api/me`               | Update authenticated user's profile   | JWT                    |

### Account Management and Password Reset

| HTTP Method | Endpoint                         | Purpose                       |
| ----------- | -------------------------------- | ----------------------------- |
| POST        | `/api/renew-account/<user_id>` | Renew an account              |
| POST        | `/api/reactivate-account`      | Reactivate an expired account |
| POST        | `/api/password-reset`          | Reset a user's password       |

The exact methods and required request fields should be checked against the current URL configuration and view implementations.

### Roles and Permissions

The roles application provides role and permission management.

| HTTP Method | Endpoint                        | Purpose                                 |
| ----------- | ------------------------------- | --------------------------------------- |
| GET         | `/api/permissions`            | Retrieve available permissions          |
| GET         | `/api/roles`                  | List available roles                    |
| POST        | `/api/roles`                  | Create a role                           |
| GET         | `/api/roles/<role_id>`        | Retrieve role details                   |
| DELETE      | `/api/roles/<role_id>`        | Delete a role                           |
| PUT/PATCH   | `/api/roles/<role_id>/update` | Update role information                 |
| PATCH       | `/api/user/<user_id>/role`    | Assign, change, or remove a user's role |

The roles API supports listing and creating roles through `roles_api`, retrieving and deleting roles through `role_detail_api`, and updating roles through `role_update`.

> Confirm the exact HTTP methods and permission requirements in the corresponding Django views before integrating additional clients.

## Authentication

EMSystem uses custom JWT authentication with PyJWT.

After successful login, the backend returns an access token and user information.

Include the token in protected requests:

```http
Authorization: Bearer <access_token>
```

Protected endpoints validate the token before processing the request.

Keep tokens private. Never commit real tokens to source control or expose them in application logs.

## User Management

### User Registration

Registration accepts the required user information:

- First name
- Last name
- Email
- Password

The backend validates input, checks duplicate email addresses, hashes the password, and creates the user account.

### User Login

Login verifies the supplied email and password.

The API handles invalid credentials and expired accounts separately. Successful authentication returns a JWT access token.

### User Listing and Pagination

The user-list API supports pagination:

```text
/api/user-list?page=1&page_size=10
```

Pagination defaults:

- Page: `1`
- Page size: `10`
- Allowed page-size range: `1–100`

The response includes pagination information, such as the current page and total number of users.

Password fields are excluded from user-list responses.

### Create User

Authenticated users with the required `users.create` permission can create new users.

The create-user operation supports an optional `role_id` so that a role can be assigned during user creation.

Example request:

```json
{
  "first_name": "Haris",
  "last_name": "Sharma",
  "email": "haris@example.com",
  "password": "SecurePassword123",
  "role_id": 2
}
```

If no role is selected, the user can be created without an assigned role.

### Update User

The user-update API supports:

- `PUT` — Requires all supported editable fields.
- `PATCH` — Supports partial updates.

Editable profile fields:

- `first_name`
- `last_name`
- `email`

Role assignment is handled separately through the user-role endpoint.

### Delete User

User deletion requires the appropriate `users.delete` permission.

## Account Operations

### Account Renewal

Account renewal requires a valid JWT.

A user can renew their own account. The backend checks that the authenticated user's ID matches the requested account ID.

### Account Reactivation

Account reactivation verifies the user's email and password before reactivating an expired account.

A fresh JWT is issued after successful reactivation.

## Role-Based Access Control (RBAC)

EMSystem includes a role and permission management system.

### Roles

A role represents a collection of permissions that can be assigned to a user.

Examples include:

- Admin
- Manager
- Employee

These are illustrative examples; actual roles depend on the roles configured in the database.

### Permissions

Permissions define which operations an authenticated user can perform.

Examples of permission names include:

- `users.read`
- `users.create`
- `users.update`
- `users.delete`
- `roles.read`

### Role Assignment

The backend supports assigning, changing, and removing a user's role through:

```http
PATCH /api/user/<user_id>/role
```

Example request to assign a role:

```json
{
  "role_id": 2
}
```

To remove a role:

```json
{
  "role_id": null
}
```

The role-assignment operation checks the authenticated user's permissions. It also prevents a user from assigning a role containing permissions they do not possess.

### Security Considerations

- Protected endpoints require JWT authentication.
- Permission checks are performed on the backend.
- Role assignment is handled separately from profile updates.
- Unauthorized privilege escalation is rejected.
- Frontend permission checks are for user-interface behavior; backend authorization remains authoritative.

## Password Security

- Passwords are stored using Django password-hashing utilities.
- Password verification uses Django's password-checking utilities.
- Plaintext passwords are never stored.
- Passwords and JWT tokens should never be logged.
- JWT signing secrets and database credentials must remain private.

## Automated Testing

Run the backend test suite:

```powershell
python manage.py test userauth
```

Run Django system checks:

```powershell
python manage.py check
```

The automated tests cover backend functionality such as:

- Registration and login
- JWT authentication
- User creation and updates
- User deletion
- Account renewal and reactivation
- Password reset
- Role management
- Permission validation
- Role assignment and privilege escalation protection

Django may create a separate test database. Ensure that your MySQL user has the necessary permissions.

**Important:** Verify the database name before deleting or recreating any database. Never delete your development database to resolve a test-database problem.

## Troubleshooting

### `No module named 'django'`

Activate the backend virtual environment:

```powershell
.\env\Scripts\Activate.ps1
```

Verify Django installation:

```powershell
python -m pip show django
```

### MySQL connection errors

Check:

- MySQL Server is running.
- The database exists.
- Database credentials are correct.
- Django database settings match your configuration.

### JWT authentication errors

Check:

- The Authorization header is included.
- The token uses the Bearer scheme.
- The token is valid and has not expired.
- The JWT configuration matches the backend settings.

### Permission denied errors

Check:

- The user has a valid JWT.
- The user's assigned role contains the required permission.
- The endpoint's permission requirements are correct.

### Test database errors

Review the Django error carefully. Confirm which database is affected before making any changes.

## Related Documentation

- [EMSystem Project Overview](../README.md)
- [EMSystem Fronte](../emsystem-frontend/README.md)

# EMSystem Backend

The **EMSystem (Employee Management System) Backend** is a Django-based REST-style JSON API that manages authentication, users, accounts, roles, and permissions.

It provides backend services to the separate Vue 3 frontend application. The backend uses Django function-based views, `JsonResponse`, MySQL, and custom JWT authentication.

## Features

- User registration and login
- JWT-based authentication
- User profile management
- User listing with pagination
- Create, update, and delete users
- Account renewal and reactivation
- Password reset
- Role management
- Permission management
- Role assignment and removal
- Permission-based access control
- Automated backend testing

## Technology Stack

| Technology              | Purpose                      |
| ----------------------- | ---------------------------- |
| Python 3.11.5           | Backend programming language |
| Django 5.2.18           | Backend framework            |
| MySQL                   | Relational database          |
| PyJWT                   | JWT authentication           |
| Django `JsonResponse` | JSON API responses           |
| Django password hashing | Secure password storage      |
| Django Test Framework   | Automated testing            |

> The current backend uses Django function-based views and custom JWT authentication. It does not depend on Django REST Framework or SimpleJWT for its current API implementation.

## Project Location

```text
F:\Projects\Django_Project\emsystem\
└── emsystem-backend\
```

## Project Structure

The following is a simplified representation. Refer to the actual repository for the complete structure.

```text
emsystem-backend/
│
├── userauth/
│   ├── migrations/
│   ├── tests/
│   ├── urls.py
│   └── views.py
│
├── roles/
│   ├── migrations/
│   ├── urls.py
│   └── views.py
│
├── emsystem/
│   ├── settings.py
│   ├── urls.py
│   └── ...
│
├── manage.py
├── requirements.txt
└── README.md
```

## Prerequisites

Install or configure:

- Python 3.11.x
- MySQL Server
- MySQL database and database user
- Python virtual environment
- Git (optional)

## Installation and Setup

Run the following commands using PowerShell.

### 1. Open the backend directory

```powershell
cd F:\Projects\Django_Project\emsystem\emsystem-backend
```

### 2. Activate the virtual environment

```powershell
.\env\Scripts\Activate.ps1
```

Verify Python:

```powershell
python --version
```

### 3. Install dependencies

```powershell
python -m pip install -r requirements.txt
```

### 4. Configure MySQL

Configure the database connection in the existing Django settings.

You will need:

- Database name
- Database username
- Database password
- Database host
- Database port

**Security:** Never commit database credentials, JWT secrets, access tokens, or passwords to GitHub.

### 5. Run system checks and migrations

```powershell
python manage.py check
python manage.py migrate
```

### 6. Start the development server

```powershell
python manage.py runserver
```

Backend development URL:

```text
http://127.0.0.1:8000/
```

API root:

```text
http://127.0.0.1:8000/api/
```

## API Documentation

All API endpoints are accessed through the `/api/` prefix.

### 1. User Authentication and Management

| Endpoint                               | Purpose                             | Access                        |
| -------------------------------------- | ----------------------------------- | ----------------------------- |
| `GET /api/`                          | API status                          | Public                        |
| `/api/register`                      | Register a new user                 | Public                        |
| `/api/login`                         | Authenticate and receive JWT        | Public                        |
| `/api/user-list`                     | Retrieve paginated users            | JWT + permission              |
| `/api/user-create`                   | Create a user                       | JWT + permission              |
| `/api/update/<user_id>`              | Update user information             | JWT + permission              |
| `/api/delete/<user_id>`              | Delete a user                       | JWT + permission              |
| `/api/me`                            | Retrieve current user's profile     | JWT                           |
| ~~`/api/renew-account/<user_id>`~~ | ~~Renew an account~~              | ~~JWT; own account only~~   |
| ~~`/api/reactivate-account`~~      | ~~Reactivate an expired account~~ | ~~Credentials required~~    |
| `/api/password-reset`                | Reset a user's password             | Verify current implementation |

The HTTP methods and exact request formats should be checked against the corresponding `userauth/urls.py` and views.

### 2. Roles and Permissions

The `roles` application manages application roles and their associated permissions.

The URL configuration includes:

| Endpoint                        | View                | Purpose                                |
| ------------------------------- | ------------------- | -------------------------------------- |
| `GET /api/permissions`        | `permission_list` | Retrieve available permissions         |
| `/api/roles`                  | `roles_api`       | List roles and create roles            |
| `/api/roles/<role_id>`        | `role_detail_api` | Retrieve role details or delete a role |
| `/api/roles/<role_id>/update` | `role_update`     | Update a role                          |

The expected operations for the combined role endpoints are:

- `GET /api/roles` – List roles
- `POST /api/roles` – Create a role
- `GET /api/roles/<role_id>` – Retrieve role details
- `DELETE /api/roles/<role_id>` – Delete a role
- `PUT` or `PATCH /api/roles/<role_id>/update` – Update a role, depending on the view implementation
- `GET /api/permissions` – Retrieve available permissions

### 3. User Role Assignment

The backend also provides a dedicated endpoint for assigning or removing a user's role.

| Method    | Endpoint                     | Purpose                                 |
| --------- | ---------------------------- | --------------------------------------- |
| `PATCH` | `/api/user/<user_id>/role` | Assign, change, or remove a user's role |

Example request:

```json
{
  "role_id": 2
}
```

To remove the assigned role:

```json
{
  "role_id": null
}
```

The role assignment endpoint checks the requesting user's permissions before allowing a role change. It prevents assigning a role containing permissions that the requesting user does not possess.

> Role assignment is handled separately from the regular user profile update endpoint.

## Authentication and Authorization

### JWT Authentication

After successful login, the backend returns an access token.

Include the token in protected API requests:

```http
Authorization: Bearer <access_token>
```

### Permission-Based Authorization

EMSystem uses role-based access control (RBAC).

The general relationship is:

```text
User
  |
  v
Role
  |
  v
Permissions
  |
  v
Authorized API Operations
```

Examples of application permissions include:

- `users.read`
- `users.create`
- `users.update`
- `users.delete`
- `roles.read`
- Role and permission management permissions defined in the application

Access is determined by the permissions assigned to the authenticated user.

## User List and Pagination

The user-list endpoint supports pagination.

Example:

```text
/api/user-list?page=1&page_size=10
```

Default values:

| Parameter     | Default | Allowed range    |
| ------------- | ------: | ---------------- |
| `page`      |       1 | Positive integer |
| `page_size` |      10 | 1–100           |

Password fields are excluded from user-list responses.

The response includes pagination information such as the current page and total user count.

## User Operations

### Registration and Login

Registration validates:

- First name
- Last name
- Email
- Password
- Name and email formats
- Password length
- Duplicate email addresses

Passwords are stored using Django's password-hashing utilities.

Login verifies user credentials and checks account validity.

### User Update

The user update endpoint supports:

- `PUT` – Complete update of supported editable fields.
- `PATCH` – Partial update of supported editable fields.

Editable fields:

- `first_name`
- `last_name`
- `email`

Role changes are handled through the separate user-role assignment endpoint.

### Account Renewal and Reactivation

Account renewal requires a valid JWT and is restricted to the authenticated account owner.

Account reactivation verifies the user's credentials before restoring an expired account. A fresh token is issued after successful reactivation.

### Profile and Password Reset

The backend also provides profile and password-reset functionality.

Check the corresponding views for exact HTTP methods, request fields, authentication requirements, and validation rules.

## Automated Testing

Run the application tests:

```powershell
python manage.py test userauth
```

Run Django system checks:

```powershell
python manage.py check
```

The automated tests cover functionality such as:

- Authentication
- Registration and validation
- User operations
- Account renewal and reactivation
- Password reset
- Roles and permissions
- Role assignment and authorization

Django may create a separate test database. Ensure your MySQL user has the required permissions.

**Important:** Verify which database is affected before deleting or recreating any database.

## Security Guidelines

- Store passwords using Django password hashing.
- Never store plaintext passwords.
- Keep JWT signing secrets private.
- Never commit database credentials.
- Validate incoming API data.
- Protect sensitive endpoints with JWT authentication.
- Enforce permissions on protected operations.
- Prevent unauthorized privilege escalation.
- Avoid logging passwords and access tokens.

## Troubleshooting

### Django module not found

Activate the virtual environment:

```powershell
.\env\Scripts\Activate.ps1
```

Check Django installation:

```powershell
python -m pip show django
```

### MySQL connection errors

Verify:

- MySQL Server is running.
- Database exists.
- Credentials are correct.
- Django database settings are configured properly.

### Authentication or permission errors

Verify:

- Authorization header is present.
- JWT token is valid and not expired.
- User has the required permission.
- The endpoint and HTTP method are correct.

### Test database errors

Review the Django error and verify the database name before making changes. Do not delete the development database to resolve a test database issue.

## Related Documentation

- [Main Project README](../README.md)
- [EMSystem Fronte](../emsystem-frontend/README.md)

# EMSystem Backend

The **EMSystem (Employee Management System) Backend** is a Django-based REST-style JSON API. It manages user registration, authentication, profile operations, user administration, account renewal and reactivation, password reset, and role-based access control.

The backend is designed to work independently from the Vue 3 frontend and communicates through JSON over HTTP.

## Technology Stack

| Technology              | Purpose                                  |
| ----------------------- | ---------------------------------------- |
| Python 3.11.5           | Backend programming language             |
| Django 5.2.18           | Web framework                            |
| MySQL                   | Relational database                      |
| PyJWT                   | JWT-based authentication                 |
| Django `JsonResponse` | JSON API responses                       |
| Django password hashing | Secure password storage and verification |
| Django ORM              | Database operations                      |
| Django Test Framework   | Automated testing                        |

> **Architecture note:** This project currently uses Django function-based views and Django JSON responses. It uses custom PyJWT authentication and does not depend on Django REST Framework or SimpleJWT.

## Project Location

```text
F:\Projects\Django_Project\emsystem\
└── emsystem-backend\
```

## Features

- User registration and login
- JWT-based authentication
- Authenticated user profile retrieval and updates
- User listing with pagination
- Create, update, and delete users
- Account renewal and reactivation
- Password-reset functionality
- Role-based access control (RBAC)
- Role assignment and removal
- Permission-based API authorization
- Input validation and error handling
- Automated backend tests

## Project Structure

The following is a representative structure. Adjust it to match the actual repository.

```text
emsystem-backend/
│
├── userauth/
│   ├── migrations/
│   ├── tests/
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   └── ...
│
├── emsystem/
│   ├── settings.py
│   ├── urls.py
│   └── ...
│
├── env/
├── manage.py
├── requirements.txt
└── README.md
```

## Prerequisites

Before running the backend, install or configure:

- Python 3.11.x
- MySQL Server
- A configured MySQL database and database user
- Python virtual environment (`env`)
- Git (optional)

## Setup and Installation

Run the following commands in PowerShell.

### 1. Navigate to the backend directory

```powershell
cd F:\Projects\Django_Project\emsystem\emsystem-backend
```

### 2. Activate the virtual environment

```powershell
.\env\Scripts\Activate.ps1
```

Verify Python:

```powershell
python --version
```

### 3. Install dependencies

```powershell
python -m pip install -r requirements.txt
```

### 4. Configure MySQL

Configure the database connection using the existing Django settings.

You will need:

- Database name
- Database username
- Database password
- Database host
- Database port

**Security:** Never commit database credentials, JWT signing secrets, passwords, or other sensitive configuration to GitHub.

### 5. Run system checks and migrations

```powershell
python manage.py check
python manage.py migrate
```

### 6. Start the development server

```powershell
python manage.py runserver
```

Default development URL:

```text
http://127.0.0.1:8000/
```

API root:

```text
http://127.0.0.1:8000/api/
```

## API Endpoints

All API endpoints use the `/api/` prefix.

### Authentication and Account Operations

| Endpoint                         | Purpose                       | Access                           |
| -------------------------------- | ----------------------------- | -------------------------------- |
| `GET /api/`                    | API status                    | Public                           |
| `/api/register`                | Register a new user           | Public                           |
| `/api/login`                   | Authenticate and receive JWT  | Public                           |
| `/api/reactivate-account`      | Reactivate an expired account | Credentials required             |
| `/api/renew-account/<user_id>` | Renew an account              | JWT; own account only            |
| `/api/password-reset`          | Reset a user's password       | Public route; see implementation |

### User Management

| Endpoint                  | Purpose                               | Access                      |
| ------------------------- | ------------------------------------- | --------------------------- |
| `/api/user-list`        | Retrieve paginated users              | JWT + permission            |
| `/api/user-create`      | Create a user                         | JWT + `users.create`      |
| `/api/update/<user_id>` | Update user information               | JWT + `users.update`      |
| `/api/delete/<user_id>` | Delete a user                         | JWT + applicable permission |
| `/api/me`               | Retrieve authenticated user's profile | JWT                         |
| `/api/me`               | Update authenticated user's profile   | JWT                         |

### Role and Permission Operations

| Endpoint                           | Purpose                                 | Access                      |
| ---------------------------------- | --------------------------------------- | --------------------------- |
| `/api/roles`                     | Retrieve available roles                | JWT + applicable permission |
| `PATCH /api/user/<user_id>/role` | Assign, change, or remove a user's role | JWT + `users.update`      |

> Other role and permission management endpoints depend on the current URL configuration. Refer to `userauth/urls.py` for their exact paths and supported HTTP methods.

For endpoints where the HTTP method is not shown, check the current URL configuration and view before constructing a request.

## Authentication

The backend uses JSON Web Tokens (JWT) for authentication.

After successful login, the API returns an access token.

Include the token in protected API requests using the Bearer authentication scheme:

```http
Authorization: Bearer <access_token>
```

Protected endpoints validate the JWT before allowing access.

Keep access tokens private. Never commit real tokens to source control.

## User Registration and Login

Registration validates:

- First name
- Last name
- Email
- Password

Additional validation includes:

- Required-field validation
- Name-length validation
- Email validation
- Password-length validation
- Duplicate email prevention

Passwords are stored using Django's password-hashing utilities.

Login verifies the supplied credentials. Expired accounts are handled separately from invalid credentials.

Successful login returns an access token and user information.

## User Management

### User List and Pagination

The user-list endpoint supports pagination:

```text
/api/user-list?page=1&page_size=10
```

Default pagination settings:

| Setting           | Value   |
| ----------------- | ------- |
| Default page      | `1`   |
| Default page size | `10`  |
| Minimum page size | `1`   |
| Maximum page size | `100` |

Password fields are excluded from user-list responses.

The response includes pagination information such as the current page and total user count.

### Create User

The user-create endpoint supports creating users through authenticated requests.

When permitted, the request can include an optional `role_id` to assign a role during user creation.

If no role is selected, the user can be created without a role.

### Update User

The user-update endpoint supports:

- `PUT` — Full update; all supported editable fields are required.
- `PATCH` — Partial update; only supplied fields are updated.

Supported profile fields:

- `first_name`
- `last_name`
- `email`

Role changes are handled separately through the role-assignment endpoint.

### Delete User

The delete endpoint removes a user according to the permissions and validation rules implemented by the backend.

## Role-Based Access Control (RBAC)

EMSystem includes a role-based access control system.

RBAC connects users with roles, and roles contain permissions that determine which operations an authenticated user can perform.

### Main Concepts

| Concept         | Description                                     |
| --------------- | ----------------------------------------------- |
| User            | An account registered in the system             |
| Role            | A collection of permissions                     |
| Permission      | Authorization to perform a particular operation |
| Role Assignment | Connecting a role to a user                     |

### Examples of Permissions

- `users.create`
- `users.update`
- `users.read`
- `users.delete`
- `roles.read`

The actual permission set is determined by the backend database and implementation.

### Assigning or Changing a Role

The backend provides:

```http
PATCH /api/user/<user_id>/role
```

Example request body:

```json
{
  "role_id": 2
}
```

To remove the assigned role:

```json
{
  "role_id": null
}
```

The endpoint validates the requested role and applies the backend's permission and privilege-escalation checks.

### Role Assignment During User Creation

The user-create endpoint can accept an optional role:

```json
{
  "first_name": "Haris",
  "last_name": "Sharma",
  "email": "haris@example.com",
  "password": "example-password",
  "role_id": 2
}
```

Use the actual request fields and validation rules defined in the current backend implementation.

## Account Operations

### Renew Account

Account renewal requires a valid JWT.

Users can renew only their own accounts through the renewal endpoint.

### Reactivate Account

Account reactivation verifies the user's credentials before reactivating an expired account.

The current implementation issues a fresh token after successful reactivation.

## Profile and Password Reset

The backend provides profile operations through `/api/me` and password-reset functionality through `/api/password-reset`.

Refer to the corresponding views for exact HTTP methods, required JSON fields, validation rules, authentication behavior, and response codes.

## Password Security

- Passwords are hashed using Django's password-hashing utilities.
- Password verification uses Django's password-checking utilities.
- Plaintext passwords are never stored.
- Reversible encryption should not be used as a substitute for password hashing.
- Passwords and JWT tokens should never be logged.
- Sensitive configuration should remain outside source control.

## Automated Testing

Run the backend test suite:

```powershell
python manage.py test userauth
```

Run Django system checks:

```powershell
python manage.py check
```

The test suite covers implemented backend functionality, including authentication, validation, user operations, account management, password reset, and role/permission behavior.

Django may create a separate test database. Ensure your MySQL user has the required permissions.

**Important:** Always verify which database is affected before removing or recreating any database. Do not delete your development database to resolve a test-database issue.

## Troubleshooting

### No module named 'django'

Activate the project's virtual environment:

```powershell
.\env\Scripts\Activate.ps1
```

Check Django installation:

```powershell
python -m pip show django
```

### MySQL connection errors

Check:

- MySQL Server is running.
- The database exists.
- Database credentials are correct.
- Django database settings match your local configuration.

### Authentication errors

Check:

- Authorization header is included.
- Bearer token is valid.
- Token has not expired.
- The correct API endpoint is being accessed.

### Permission errors

Check:

- The authenticated user has a valid role, where required.
- The role contains the required permission.
- The backend endpoint permission check matches the intended operation.

### Test database errors

Read the Django error carefully and verify which database is affected before making changes.

## Development Guidelines

- Keep backend and frontend code separate.
- Use Django ORM for database operations.
- Keep API responses consistent.
- Validate incoming request data.
- Protect private endpoints using JWT authentication.
- Enforce permissions on the backend.
- Never expose password fields in API responses.
- Write automated tests for new functionality.
- Avoid committing secrets and credentials.

## Related Documentation

- [Main Project README](../README.md)
- [EMSystem Frontend READ](../emsystem-frontend/README.md)

# EMSystem Backend

The **EMSystem (Employee Management System) Backend** is a Django-based REST-style JSON API. It manages user registration, authentication, profile operations, user administration, account renewal and reactivation, password reset, and role-based access control.

The backend is designed to work independently from the Vue 3 frontend and communicates through JSON over HTTP.

## Technology Stack

| Technology              | Purpose                                  |
| ----------------------- | ---------------------------------------- |
| Python 3.11.5           | Backend programming language             |
| Django 5.2.18           | Web framework                            |
| MySQL                   | Relational database                      |
| PyJWT                   | JWT-based authentication                 |
| Django `JsonResponse` | JSON API responses                       |
| Django password hashing | Secure password storage and verification |
| Django ORM              | Database operations                      |
| Django Test Framework   | Automated testing                        |

> **Architecture note:** This project currently uses Django function-based views and Django JSON responses. It uses custom PyJWT authentication and does not depend on Django REST Framework or SimpleJWT.

## Project Location

```text
F:\Projects\Django_Project\emsystem\
└── emsystem-backend\
```

## Features

- User registration and login
- JWT-based authentication
- Authenticated user profile retrieval and updates
- User listing with pagination
- Create, update, and delete users
- Account renewal and reactivation
- Password-reset functionality
- Role-based access control (RBAC)
- Role assignment and removal
- Permission-based API authorization
- Input validation and error handling
- Automated backend tests

## Project Structure

The following is a representative structure. Adjust it to match the actual repository.

```text
emsystem-backend/
│
├── userauth/
│   ├── migrations/
│   ├── tests/
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   └── ...
│
├── emsystem/
│   ├── settings.py
│   ├── urls.py
│   └── ...
│
├── env/
├── manage.py
├── requirements.txt
└── README.md
```

## Prerequisites

Before running the backend, install or configure:

- Python 3.11.x
- MySQL Server
- A configured MySQL database and database user
- Python virtual environment (`env`)
- Git (optional)

## Setup and Installation

Run the following commands in PowerShell.

### 1. Navigate to the backend directory

```powershell
cd F:\Projects\Django_Project\emsystem\emsystem-backend
```

### 2. Activate the virtual environment

```powershell
.\env\Scripts\Activate.ps1
```

Verify Python:

```powershell
python --version
```

### 3. Install dependencies

```powershell
python -m pip install -r requirements.txt
```

### 4. Configure MySQL

Configure the database connection using the existing Django settings.

You will need:

- Database name
- Database username
- Database password
- Database host
- Database port

**Security:** Never commit database credentials, JWT signing secrets, passwords, or other sensitive configuration to GitHub.

### 5. Run system checks and migrations

```powershell
python manage.py check
python manage.py migrate
```

### 6. Start the development server

```powershell
python manage.py runserver
```

Default development URL:

```text
http://127.0.0.1:8000/
```

API root:

```text
http://127.0.0.1:8000/api/
```

## API Endpoints

All API endpoints use the `/api/` prefix.

### Authentication and Account Operations

| Endpoint                         | Purpose                       | Access                           |
| -------------------------------- | ----------------------------- | -------------------------------- |
| `GET /api/`                    | API status                    | Public                           |
| `/api/register`                | Register a new user           | Public                           |
| `/api/login`                   | Authenticate and receive JWT  | Public                           |
| `/api/reactivate-account`      | Reactivate an expired account | Credentials required             |
| `/api/renew-account/<user_id>` | Renew an account              | JWT; own account only            |
| `/api/password-reset`          | Reset a user's password       | Public route; see implementation |

### User Management

| Endpoint                  | Purpose                               | Access                      |
| ------------------------- | ------------------------------------- | --------------------------- |
| `/api/user-list`        | Retrieve paginated users              | JWT + permission            |
| `/api/user-create`      | Create a user                         | JWT + `users.create`      |
| `/api/update/<user_id>` | Update user information               | JWT + `users.update`      |
| `/api/delete/<user_id>` | Delete a user                         | JWT + applicable permission |
| `/api/me`               | Retrieve authenticated user's profile | JWT                         |
| `/api/me`               | Update authenticated user's profile   | JWT                         |

### Role and Permission Operations

| Endpoint                           | Purpose                                 | Access                      |
| ---------------------------------- | --------------------------------------- | --------------------------- |
| `/api/roles`                     | Retrieve available roles                | JWT + applicable permission |
| `PATCH /api/user/<user_id>/role` | Assign, change, or remove a user's role | JWT + `users.update`      |

> Other role and permission management endpoints depend on the current URL configuration. Refer to `userauth/urls.py` for their exact paths and supported HTTP methods.

For endpoints where the HTTP method is not shown, check the current URL configuration and view before constructing a request.

## Authentication

The backend uses JSON Web Tokens (JWT) for authentication.

After successful login, the API returns an access token.

Include the token in protected API requests using the Bearer authentication scheme:

```http
Authorization: Bearer <access_token>
```

Protected endpoints validate the JWT before allowing access.

Keep access tokens private. Never commit real tokens to source control.

## User Registration and Login

Registration validates:

- First name
- Last name
- Email
- Password

Additional validation includes:

- Required-field validation
- Name-length validation
- Email validation
- Password-length validation
- Duplicate email prevention

Passwords are stored using Django's password-hashing utilities.

Login verifies the supplied credentials. Expired accounts are handled separately from invalid credentials.

Successful login returns an access token and user information.

## User Management

### User List and Pagination

The user-list endpoint supports pagination:

```text
/api/user-list?page=1&page_size=10
```

Default pagination settings:

| Setting           | Value   |
| ----------------- | ------- |
| Default page      | `1`   |
| Default page size | `10`  |
| Minimum page size | `1`   |
| Maximum page size | `100` |

Password fields are excluded from user-list responses.

The response includes pagination information such as the current page and total user count.

### Create User

The user-create endpoint supports creating users through authenticated requests.

When permitted, the request can include an optional `role_id` to assign a role during user creation.

If no role is selected, the user can be created without a role.

### Update User

The user-update endpoint supports:

- `PUT` — Full update; all supported editable fields are required.
- `PATCH` — Partial update; only supplied fields are updated.

Supported profile fields:

- `first_name`
- `last_name`
- `email`

Role changes are handled separately through the role-assignment endpoint.

### Delete User

The delete endpoint removes a user according to the permissions and validation rules implemented by the backend.

## Role-Based Access Control (RBAC)

EMSystem includes a role-based access control system.

RBAC connects users with roles, and roles contain permissions that determine which operations an authenticated user can perform.

### Main Concepts

| Concept         | Description                                     |
| --------------- | ----------------------------------------------- |
| User            | An account registered in the system             |
| Role            | A collection of permissions                     |
| Permission      | Authorization to perform a particular operation |
| Role Assignment | Connecting a role to a user                     |

### Examples of Permissions

- `users.create`
- `users.update`
- `users.read`
- `users.delete`
- `roles.read`

The actual permission set is determined by the backend database and implementation.

### Assigning or Changing a Role

The backend provides:

```http
PATCH /api/user/<user_id>/role
```

Example request body:

```json
{
  "role_id": 2
}
```

To remove the assigned role:

```json
{
  "role_id": null
}
```

The endpoint validates the requested role and applies the backend's permission and privilege-escalation checks.

### Role Assignment During User Creation

The user-create endpoint can accept an optional role:

```json
{
  "first_name": "Haris",
  "last_name": "Sharma",
  "email": "haris@example.com",
  "password": "example-password",
  "role_id": 2
}
```

Use the actual request fields and validation rules defined in the current backend implementation.

## Account Operations

### Renew Account

Account renewal requires a valid JWT.

Users can renew only their own accounts through the renewal endpoint.

### Reactivate Account

Account reactivation verifies the user's credentials before reactivating an expired account.

The current implementation issues a fresh token after successful reactivation.

## Profile and Password Reset

The backend provides profile operations through `/api/me` and password-reset functionality through `/api/password-reset`.

Refer to the corresponding views for exact HTTP methods, required JSON fields, validation rules, authentication behavior, and response codes.

## Password Security

- Passwords are hashed using Django's password-hashing utilities.
- Password verification uses Django's password-checking utilities.
- Plaintext passwords are never stored.
- Reversible encryption should not be used as a substitute for password hashing.
- Passwords and JWT tokens should never be logged.
- Sensitive configuration should remain outside source control.

## Automated Testing

Run the backend test suite:

```powershell
python manage.py test userauth
```

Run Django system checks:

```powershell
python manage.py check
```

The test suite covers implemented backend functionality, including authentication, validation, user operations, account management, password reset, and role/permission behavior.

Django may create a separate test database. Ensure your MySQL user has the required permissions.

**Important:** Always verify which database is affected before removing or recreating any database. Do not delete your development database to resolve a test-database issue.

## Troubleshooting

### No module named 'django'

Activate the project's virtual environment:

```powershell
.\env\Scripts\Activate.ps1
```

Check Django installation:

```powershell
python -m pip show django
```

### MySQL connection errors

Check:

- MySQL Server is running.
- The database exists.
- Database credentials are correct.
- Django database settings match your local configuration.

### Authentication errors

Check:

- Authorization header is included.
- Bearer token is valid.
- Token has not expired.
- The correct API endpoint is being accessed.

### Permission errors

Check:

- The authenticated user has a valid role, where required.
- The role contains the required permission.
- The backend endpoint permission check matches the intended operation.

### Test database errors

Read the Django error carefully and verify which database is affected before making changes.

## Development Guidelines

- Keep backend and frontend code separate.
- Use Django ORM for database operations.
- Keep API responses consistent.
- Validate incoming request data.
- Protect private endpoints using JWT authentication.
- Enforce permissions on the backend.
- Never expose password fields in API responses.
- Write automated tests for new functionality.
- Avoid committing secrets and credentials.

## Related Documentation

- [Main Project README](../README.md)
- [EMSystem Frontend README](../emsystem-frontend/README.md)

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
