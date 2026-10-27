
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
