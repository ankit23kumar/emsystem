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
