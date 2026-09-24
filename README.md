# Student Academic Dashboard

React + Vite frontend, FastAPI backend, MongoDB database, and JWT authentication for the Phase 1 student dashboard.

## Services

| Service | URL | Port |
| --- | --- | --- |
| Frontend | http://localhost:5173 | 5173 |
| FastAPI | http://localhost:8000 | 8000 |
| Swagger | http://localhost:8000/docs | 8000 |
| MongoDB | mongodb://localhost:27018 | 27018 |

MongoDB database: `student_dashboard_db`
MongoDB collection: `users`

## Project Structure

```text
backend/
  app/
    core/                 Settings and JWT security
    db/                   MongoDB connection and indexes
    modules/auth/         Registration, login, profile, and logout API
  .env
  .env.example
  requirements.txt
frontend/
  src/
    components/           Shared layout and route guards
    context/              Authentication state
    features/auth/        Login and registration pages
    features/dashboard/   Protected dashboard
  .env
  .env.example
  package.json
```

## Prerequisites

- Python 3.11 or newer
- Node.js and npm
- MongoDB Server 8.x or compatible

## Start MongoDB

The existing local data directory is `mongodb-data-27018`. Start MongoDB from the project root:

```powershell
& 'C:\Program Files\MongoDB\Server\8.2\bin\mongod.exe' `
  --dbpath 'C:\Mini_Project\mongodb-data-27018' `
  --port 27018 `
  --bind_ip 127.0.0.1
```

Keep this terminal running.

## Start the Backend

The repository contains `backend/venv`. To create it from scratch:

```powershell
cd backend
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
```

Start FastAPI in another terminal:

```powershell
cd backend
.\venv\Scripts\python.exe -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The backend loads MongoDB and JWT settings from `backend/.env`:

```env
MONGODB_URL=mongodb://localhost:27018
DATABASE_NAME=student_dashboard_db
JWT_SECRET=your-local-secret
JWT_ALGORITHM=HS256
```

## Start the Frontend

```powershell
cd frontend
npm install
npm run dev
```

Open http://localhost:5173.

The frontend API base URL is configured in `frontend/.env`:

```env
VITE_API_BASE_URL=http://localhost:8000
```

## Frontend Routes

- `/` redirects to the dashboard route and then to `/login` when unauthenticated.
- `/login` is the public login page.
- `/register` is the public registration page.
- `/dashboard` is protected and requires a valid JWT.

Authenticated users visiting `/login` or `/register` are redirected to `/dashboard`.

## Backend Routes

- `POST /auth/register`
- `POST /auth/login`
- `GET /auth/me` with `Authorization: Bearer <JWT>`
- `POST /auth/logout`

Passwords are stored as bcrypt hashes. Login responses contain the JWT and basic user data, never a password or password hash. Email uniqueness is enforced by the MongoDB unique index on `users.email`.

## Demo Account

```text
Email:    demo@example.com
Password: Demo123!
```

## Validation Commands

Frontend production build:

```powershell
cd frontend
npm run build
```

Backend compilation:

```powershell
cd ..
backend\venv\Scripts\python.exe -m compileall -q backend\app
```

## Manual Authentication Test

1. Start MongoDB on port `27018`.
2. Start FastAPI on port `8000`.
3. Open http://localhost:8000/docs.
4. Register a new account at http://localhost:5173/register.
5. Log in at http://localhost:5173/login.
6. Confirm the app redirects to `/dashboard`.
7. Refresh `/dashboard`; the saved JWT should restore the session through `/auth/me`.
8. Log out.
9. Open `/dashboard` again; it should redirect to `/login`.
10. Verify invalid passwords, missing tokens, and invalid tokens are rejected with `401 Unauthorized`.
