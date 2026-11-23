# EMSystem Frontend

The **EMSystem (Employee Management System) Frontend** is a Vue 3 single-page application built with Vite.

It provides the user interface for authentication, profile management, user administration, and role-based access control. The frontend communicates with the separate Django backend through HTTP API requests using Axios.

## Features

### Authentication

- User registration
- User login
- JWT-based authentication
- Authentication-aware navigation
- Protected routes
- Logout functionality

### User Management

- View users
- Paginated user listing
- Create users
- Update user information
- Delete users
- User profile management
- Account renewal and reactivation

### Password Management

- Password reset interface
- Password input component
- Form validation and error handling

### Role and Permission Management

- View available roles
- Create roles
- Update role information
- Delete roles
- View available permissions
- Manage role permissions
- Assign roles during user creation
- View and change assigned roles while editing users
- Remove an assigned role
- Display role badges in the user list
- Permission-aware user interface

### Reusable UI Components

- Confirmation modal
- User form modal
- Password input
- Password reset modal
- Toast notifications
- Dashboard topbar
- User grid
- Role badge
- Status badge
- User action renderer

## Technology Stack

| Technology | Purpose                           |
| ---------- | --------------------------------- |
| Vue 3      | Frontend framework                |
| Vite       | Development server and build tool |
| Vue Router | Client-side routing               |
| Axios      | Backend HTTP communication        |
| JavaScript | Application logic                 |
| CSS        | Styling and responsive layouts    |

## Project Location

```text
F:\Projects\Django_Project\emsystem\
└── emsystem-frontend\
```

## Project Structure

Current application structure based on the project directory:

```text
emsystem-frontend/
│
├── public/
│
├── src/
│   │
│   ├── assets/
│   │
│   ├── components/
│   │   ├── ConfirmationModal.vue
│   │   ├── DashboardTopbar.vue
│   │   ├── FirstNameHeader.vue
│   │   ├── PasswordInput.vue
│   │   ├── PasswordResetModal.vue
│   │   ├── RoleBadge.vue
│   │   ├── RoleBadgeCellRenderer.vue
│   │   ├── StatusBadgeRenderer.vue
│   │   ├── ToastNotification.vue
│   │   ├── UserActionsRenderer.vue
│   │   ├── UserFormModal.vue
│   │   ├── UserGrid.vue
│   │   │
│   │   └── dashboard/
│   │       ├── DashboardTabs.vue
│   │       ├── RoleFormModal.vue
│   │       ├── RoleManagementPanel.vue
│   │       └── UserManagementPanel.vue
│   │
│   ├── composables/
│   │   ├── useToast.js
│   │   └── useUsers.js
│   │
│   ├── layouts/
│   │   └── DashboardLayout.vue
│   │
│   ├── router/
│   │   └── index.js
│   │
│   ├── services/
│   │   ├── api.js
│   │   └── userService.js
│   │
│   ├── stores/
│   │   └── authStore.js
│   │
│   ├── views/
│   │   ├── DashboardView.vue
│   │   ├── LoginView.vue
│   │   ├── RegisterView.vue
│   │   └── UserListView.vue
│   │
│   ├── App.vue
│   ├── main.js
│   └── style.css
│
├── index.html
├── package.json
├── package-lock.json
├── vite.config.js
└── README.md
```

> **Note:** The structure above reflects the supplied `src/` directory. Add any additional files that exist in your local repository.

## Folder Responsibilities

| Folder/File               | Responsibility                            |
| ------------------------- | ----------------------------------------- |
| `assets/`               | Static images, icons, and other assets    |
| `components/`           | Reusable Vue components                   |
| `components/dashboard/` | Dashboard-specific management components  |
| `composables/`          | Reusable Composition API logic            |
| `layouts/`              | Shared page layouts                       |
| `router/`               | Vue Router configuration and route guards |
| `services/`             | API communication and service functions   |
| `stores/`               | Shared authentication state               |
| `views/`                | Page-level components                     |
| `App.vue`               | Root Vue component                        |
| `main.js`               | Application entry point                   |
| `style.css`             | Global application styles                 |

## Architecture and Code Organization

The frontend follows a component-based structure.

### Components

Components are responsible for reusable user-interface elements, such as modals, forms, badges, notifications, and data-grid renderers.

### Views

Views represent application pages, such as login, registration, dashboard, and user listing.

### Composables

Composables contain reusable application logic.

Examples:

- `useToast.js` — Toast notification functionality.
- `useUsers.js` — User-related reusable logic.

### Services

The service layer handles communication with the Django backend.

Examples:

- `api.js` — Shared Axios instance and API configuration.
- `userService.js` — User-related API operations.

Keep HTTP requests inside service modules rather than writing Axios requests directly inside reusable UI components.

**Role-service note:** The role-management components and role dropdown functionality also require a role service module. If it is part of your current implementation, include `src/services/roleService.js` alongside `api.js` and `userService.js`.

### Authentication Store

`authStore.js` maintains shared authentication information and permission checks.

It supports authentication-aware navigation and permission-based interface behavior.

### Router

`router/index.js` defines application routes and route protection.

Protected pages should be accessible only when the user has the required authentication state.

## Prerequisites

Install the following:

- Node.js compatible with the installed Vite version
- npm
- EMSystem Django backend
- MySQL configured for the backend

Check installed versions:

```powershell
node --version
npm --version
```

## Installation

Navigate to the frontend directory:

```powershell
cd F:\Projects\Django_Project\emsystem\emsystem-frontend
```

Install dependencies:

```powershell
npm install
```

## Running the Application

Start the Vite development server:

```powershell
npm run dev
```

Open the local URL displayed in the terminal.

## Production Build

Generate the production build:

```powershell
npm run build
```

Vite generates optimized production files inside:

```text
dist/
```

Preview the production build locally:

```powershell
npm run preview
```

## Backend Integration

The frontend communicates with the Django backend through Axios.

Local backend API root:

```text
http://127.0.0.1:8000/api/
```

The shared API configuration is maintained in:

```text
src/services/api.js
```

Before testing the frontend:

1. Start the Django backend.
2. Confirm the API is accessible.
3. Verify the API base URL in the Axios configuration.
4. Confirm that endpoint paths match the backend URL configuration.
5. Ensure protected requests include the JWT Bearer token.
6. Check that the backend allows requests from the frontend origin through its CORS configuration, if applicable.

Example authorization header:

```http
Authorization: Bearer <access_token>
```

Never store database passwords, JWT signing secrets, or other private backend credentials in frontend source code.

## User Management Workflow

The user-management interface supports:

- Loading and displaying users.
- Paginated user listing.
- Creating users.
- Editing user information.
- Deleting users.
- Displaying account status.
- Showing assigned roles.

The user form supports creating and editing user information.

When creating a user, an available role can be selected if the authenticated user has the appropriate permission.

When editing a user, the existing assigned role can be displayed and changed or removed. Profile updates and role assignment use their respective backend API operations.

## Role and Permission Management

The dashboard includes role-management functionality.

Users with the appropriate permissions can access role-management operations.

The interface supports:

- Loading available roles.
- Creating a role.
- Updating role details.
- Deleting a role.
- Viewing available permissions.
- Managing permissions associated with roles.
- Displaying user roles through reusable role badges.
- Assigning or changing a user's role.

Frontend permission checks improve the user experience by hiding or disabling unavailable actions.

However, frontend permission checks are not a replacement for backend authorization. The Django API must validate every protected operation.

## Manual Testing Checklist

### Authentication

- [ ] Register a new account.
- [ ] Log in with valid credentials.
- [ ] Verify invalid login error handling.
- [ ] Test logout.
- [ ] Verify protected routes.
- [ ] Test expired-session handling.

### Password and Account Operations

- [ ] Test password reset.
- [ ] View the user profile.
- [ ] Update supported profile fields.
- [ ] Test account renewal.
- [ ] Test account reactivation.

### User Management

- [ ] Load the user list.
- [ ] Test pagination.
- [ ] Create a user without a role.
- [ ] Create a user with a role.
- [ ] Edit user information.
- [ ] Verify the existing role appears in the edit form.
- [ ] Change an assigned role.
- [ ] Remove an assigned role.
- [ ] Delete a user.
- [ ] Verify permission-based UI behavior.

### Role Management

- [ ] Load available roles.
- [ ] Create a role.
- [ ] Update a role.
- [ ] Delete a role.
- [ ] Load available permissions.
- [ ] Assign permissions to a role.
- [ ] Verify role badges in the user list.
- [ ] Test unauthorized role-management operations.

### Build Verification

- [ ] Run `npm run build`.
- [ ] Resolve build errors.
- [ ] Preview the production build.

## Troubleshooting

### API Requests Fail

Check:

- Django backend is running.
- Axios base URL is correct.
- Endpoint paths match the backend.
- JWT token is included for protected requests.
- Browser Network and Console panels show no unresolved errors.
- Backend terminal does not report server-side errors.

### Permission Errors

Check:

- The user is authenticated.
- The user has the required permission.
- The assigned role contains the required permission.
- The backend permission checks allow the requested operation.

### Roles Are Not Loading

Check:

- The roles API endpoint is available.
- The user has permission to access the roles API.
- The Axios authorization header is included.
- The role service uses the correct endpoint.
- The backend response structure matches the frontend implementation.

### Dependencies or Development Server Fail

Run:

```powershell
npm install
npm run dev
```

Review the terminal output before changing package versions.

### Production Build Fails

Run:

```powershell
npm run build
```

Review the first relevant error and resolve the underlying issue before adding dependency overrides or changing package versions.

## Development Guidelines

- Keep frontend and backend code separate.
- Use reusable Vue components.
- Keep page-level components inside `views/`.
- Keep dashboard-specific components organized inside `components/dashboard/`.
- Keep API requests in the service layer.
- Use composables for reusable application logic.
- Use Vue Router for client-side navigation.
- Keep authentication and permission state centralized.
- Handle API errors clearly.
- Do not expose backend secrets in frontend code.
- Test the production build before considering a change complete.

## Related Documentation

- [EMSystem Project Overview](../README.md)
- [EMSystem Backe](../emsystem-backend/README.md)

# EMSystem Frontend

The **EMSystem (Employee Management System) Frontend** is a Vue 3 single-page application built with Vite.

It provides the user interface for authentication, profile management, and user administration through the separate Django JSON API.

## Features

- User registration and login
- Password-reset interface
- User profile management
- Paginated user listing
- Create, update, and delete users
- Account renewal and reactivation
- Authentication-aware navigation
- Protected routes
- Form validation
- API error handling

> Feature availability and exact behavior depend on the current application implementation and backend API.

## Technology Stack

| Technology | Purpose                           |
| ---------- | --------------------------------- |
| Vue 3      | Frontend framework                |
| Vite       | Development server and build tool |
| Vue Router | Client-side routing               |
| Axios      | HTTP communication                |
| JavaScript | Application logic                 |
| CSS        | Styling and responsive layouts    |

## Project Location

```text
F:\Projects\Django_Project\emsystem\
└── emsystem-frontend\
```

## Project Structure

The following is a representative project structure. Keep it aligned with your actual repository.

```text
emsystem-frontend/
│
├── public/
│
├── src/
│   ├── assets/
│   │
│   ├── components/
│   │
│   ├── router/
│   │
│   ├── services/
│   │
│   ├── views/
│   │
│   ├── App.vue
│   └── main.js
│
├── index.html
├── package.json
├── vite.config.js
└── README.md
```

### Folder Responsibilities

| Folder/File     | Responsibility                   |
| --------------- | -------------------------------- |
| `assets/`     | Images, icons, and static assets |
| `components/` | Reusable Vue components          |
| `router/`     | Vue Router configuration         |
| `services/`   | Axios and API-related modules    |
| `views/`      | Page-level Vue components        |
| `App.vue`     | Root Vue component               |
| `main.js`     | Application entry point          |

## Prerequisites

Before running the project, install:

- Node.js compatible with the installed Vite version
- npm
- EMSystem Django backend

Check installed versions:

```powershell
node --version
npm --version
```

## Installation

Open PowerShell in the frontend directory:

```powershell
cd F:\Projects\Django_Project\emsystem\emsystem-frontend
```

Install dependencies:

```powershell
npm install
```

## Run Development Server

Start the Vite development server:

```powershell
npm run dev
```

Vite will display a local development URL in the terminal.

Open that URL in your browser.

## Production Build

Generate the production build:

```powershell
npm run build
```

Vite generates production files inside:

```text
dist/
```

To preview the production build locally:

```powershell
npm run preview
```

## Backend Integration

The Vue application communicates with the Django backend through HTTP requests using Axios.

Local backend API root:

```text
http://127.0.0.1:8000/api/
```

Before testing frontend functionality:

1. Start the Django backend.
2. Confirm that the backend API is running.
3. Verify that the frontend API base URL is correct.
4. Check that endpoint paths match the backend URL configuration.
5. Include the JWT Bearer token for protected API requests.

Example authorization header:

```http
Authorization: Bearer <access_token>
```

Keep the API base URL in the existing frontend service/configuration location.

Never store database passwords, JWT signing secrets, or private credentials in frontend source code.

## Manual Testing Checklist

Use the following checklist to validate the application:

- [ ] Register a new account.
- [ ] Log in with valid credentials.
- [ ] Verify invalid login error handling.
- [ ] Test password-reset functionality.
- [ ] View the current user's profile.
- [ ] Update supported profile fields.
- [ ] Load the user list.
- [ ] Test pagination.
- [ ] Create a user.
- [ ] Update a user.
- [ ] Delete a user.
- [ ] Test account renewal.
- [ ] Test account reactivation.
- [ ] Log out successfully.
- [ ] Verify that protected routes require authentication.

Some account operations may require specific account states, such as an expired account, to test successfully.

## Troubleshooting

### API Requests Fail

Check the following:

- Django backend is running.
- API base URL is correct.
- Endpoint paths are correct.
- Protected requests include a valid JWT.
- Browser Network and Console panels show no unresolved errors.
- Django terminal does not report server-side errors.

### Dependencies or Development Server Fail

Run:

```powershell
npm install
npm run dev
```

If the problem continues, review the terminal error before changing package versions.

### Production Build Fails

Run:

```powershell
npm run build
```

Review the first relevant error in the output.

Check dependency compatibility and resolve the reported issue before changing package versions or adding overrides.

## Development Guidelines

- Keep frontend code separate from the Django backend.
- Store reusable UI elements in `src/components/`.
- Store page-level components in `src/views/`.
- Keep API communication in the existing service layer.
- Use Vue Router for client-side navigation.
- Handle API errors clearly.
- Avoid putting credentials or secrets in frontend source code.
- Test the production build before considering a change complete.

## Related Documentation

- [Project Overview](../README.md)
- [EMSystem Backe](../emsystem-backend/README.md)

# EMSystem Frontend

The frontend application for **EMSystem (Employee Management System)**, built with Vue 3 and Vite. It provides a web interface for authentication, profile management, and user administration through the Django backend API.

## Features

- User registration and login
- Password reset
- User profile management
- User listing with pagination
- Create, update, and delete users
- Account renewal and reactivation
- Authentication-aware navigation and protected routes
- Form validation and API error handling

## Technology Stack

- **Vue 3** — frontend framework
- **Vite** — development server and production build tool
- **Vue Router** — client-side routing
- **Axios** — HTTP requests to the backend API
- **JavaScript** — application logic
- **CSS** — styling and responsive layouts

## Project Structure

```text
emsystem-frontend/
├── public/
├── src/
│   ├── assets/          # Static assets
│   ├── components/      # Reusable Vue components
│   ├── router/          # Route configuration
│   ├── services/        # API and authentication services
│   ├── views/           # Application pages
│   ├── App.vue          # Root Vue component
│   └── main.js          # Application entry point
├── index.html
├── package.json
├── vite.config.js
└── README.md
```

*Note: The structure above is a guide. Update it if your actual project folders differ.*

## Prerequisites

Install the following before running the application:

- Node.js (a version compatible with the installed Vite version)
- npm
- The EMSystem Django backend, configured and running

## Installation

Open a terminal in the `emsystem-frontend` directory.

Install dependencies:

```bash
npm install
```

## Running the Application

Start the development server:

```bash
npm run dev
```

Open the local URL printed in the terminal by Vite.

## Production Build

Create an optimized production build:

```bash
npm run build
```

The generated production files are placed in the `dist/` directory.

To preview the production build locally:

```bash
npm run preview
```

## Backend Integration

The frontend communicates with the Django backend through HTTP API requests using Axios.

Before using the application:

1. Start the Django backend.
2. Confirm the backend API is reachable.
3. Verify that the frontend API base URL matches the backend configuration.
4. Check browser developer tools if requests fail.

Configure the API base URL according to the existing configuration in `src/services/`. Do not commit passwords, JWT secrets, database credentials, or other sensitive values to source control.

## Manual Testing Checklist

- [ ] Register a new account.
- [ ] Log in with valid credentials.
- [ ] Confirm invalid login details display an appropriate message.
- [ ] Test password reset.
- [ ] View and update the user profile.
- [ ] View the user list and test pagination.
- [ ] Create, update, and delete a user.
- [ ] Test account renewal and reactivation, where applicable.
- [ ] Log out and verify protected routes require authentication.

## Troubleshooting

### API requests fail

- Confirm that the Django backend is running.
- Verify the API base URL and endpoint paths.
- Inspect the browser Network and Console tabs.
- Check backend logs for errors.

### Dependencies or development server fail

Run:

```bash
npm install
npm run dev
```

### Production build fails

Run:

```bash
npm run build
```

Review the terminal output and resolve the reported errors.

## Related Documentation

For the complete project overview, backend setup, architecture, and API summary, see the universal README in the parent `emsystem/` directory.
