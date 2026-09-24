import os
import shutil

PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))

FILES = {
    # -------------------------------------------------------------
    # BACKEND
    # -------------------------------------------------------------
    "backend/requirements.txt": """fastapi>=0.110.0
uvicorn[standard]>=0.28.0
motor>=3.3.2
pydantic>=2.6.4
pydantic-settings>=2.2.1
pyjwt>=2.8.0
bcrypt>=4.0.1
python-multipart>=0.0.9
email-validator>=2.1.1
""",

    "backend/.env.example": """MONGODB_URL=mongodb://localhost:27018
DATABASE_NAME=student_dashboard_db
JWT_SECRET=super_secret_jwt_key_replace_this_with_a_secure_random_string_32chars
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
ALLOWED_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
""",

    "backend/.env": """MONGODB_URL=mongodb://localhost:27018
DATABASE_NAME=student_dashboard_db
JWT_SECRET=super_secret_jwt_key_replace_this_with_a_secure_random_string_32chars
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
ALLOWED_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
""",

    "backend/.gitignore": """__pycache__/
*.py[cod]
*$py.class
.env
venv/
.venv/
.pytest_cache/
""",

    "backend/app/__init__.py": '"""Student Academic Dashboard Backend Application"""\n',

    "backend/app/config.py": """from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    MONGODB_URL: str = "mongodb://localhost:27018"
    DATABASE_NAME: str = "student_dashboard_db"
    JWT_SECRET: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 hours
    ALLOWED_ORIGINS: str = "http://localhost:5173,http://127.0.0.1:5173"

    @property
    def cors_origins(self) -> List[str]:
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",") if origin.strip()]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
""",

    "backend/app/database/__init__.py": '"""Database package"""\n',

    "backend/app/database/connection.py": """from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings

client: AsyncIOMotorClient = None
db = None


async def connect_to_mongo():
    global client, db
    client = AsyncIOMotorClient(settings.MONGODB_URL)
    db = client[settings.DATABASE_NAME]
    
    # Ensure unique index on email
    await db["users"].create_index("email", unique=True)
    print(f" Connected to MongoDB database: '{settings.DATABASE_NAME}'")


async def close_mongo_connection():
    global client
    if client:
        client.close()
        print(" MongoDB connection closed.")


def get_database():
    return db
""",

    "backend/app/utils/__init__.py": '"""Utility functions package"""\n',

    "backend/app/utils/security.py": """from datetime import datetime, timedelta, timezone
import bcrypt
import jwt
from app.core.config import settings


def hash_password(password: str) -> str:
    pwd_bytes = password.encode("utf-8")
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(pwd_bytes, salt).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    pwd_bytes = plain_password.encode("utf-8")
    hash_bytes = hashed_password.encode("utf-8")
    return bcrypt.checkpw(pwd_bytes, hash_bytes)


def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        return payload
    except jwt.PyJWTError:
        return None
""",

    "backend/app/models/__init__.py": '"""Pydantic models package"""\n',

    "backend/app/models/user.py": """from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional


class UserRegisterRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=100, description="Full name of student")
    email: EmailStr = Field(..., description="Valid student email address")
    password: str = Field(..., min_length=6, max_length=128, description="Secure account password")


class UserLoginRequest(BaseModel):
    email: EmailStr = Field(..., description="Registered student email")
    password: str = Field(..., description="Account password")


class UserResponse(BaseModel):
    id: str
    name: str
    email: EmailStr
    created_at: datetime


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class MessageResponse(BaseModel):
    message: str
""",

    "backend/app/services/__init__.py": '"""Business logic services"""\n',

    "backend/app/services/auth_service.py": """from datetime import datetime, timezone
from bson import ObjectId
from fastapi import HTTPException, status
from app.db.mongodb import get_database
from app.modules.auth.schemas import UserRegisterRequest, UserLoginRequest
from app.core.security import hash_password, verify_password, create_access_token


async def register_user(user_in: UserRegisterRequest):
    db = get_database()
    email_clean = user_in.email.strip().lower()

    # Check for existing email
    existing_user = await db["users"].find_one({"email": email_clean})
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this email address already exists."
        )

    user_doc = {
        "name": user_in.name.strip(),
        "email": email_clean,
        "password_hash": hash_password(user_in.password),
        "created_at": datetime.now(timezone.utc)
    }

    result = await db["users"].insert_one(user_doc)
    
    return {
        "id": str(result.inserted_id),
        "name": user_doc["name"],
        "email": user_doc["email"],
        "created_at": user_doc["created_at"]
    }


async def authenticate_user(credentials: UserLoginRequest):
    db = get_database()
    email_clean = credentials.email.strip().lower()

    user = await db["users"].find_one({"email": email_clean})
    if not user or not verify_password(credentials.password, user["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password."
        )

    access_token = create_access_token(
        data={"sub": str(user["_id"]), "email": user["email"]}
    )

    user_data = {
        "id": str(user["_id"]),
        "name": user["name"],
        "email": user["email"],
        "created_at": user.get("created_at", datetime.now(timezone.utc))
    }

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user_data
    }


async def get_current_user_by_id(user_id: str):
    db = get_database()
    if not ObjectId.is_valid(user_id):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authorization payload.")
        
    user = await db["users"].find_one({"_id": ObjectId(user_id)})
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")

    return {
        "id": str(user["_id"]),
        "name": user["name"],
        "email": user["email"],
        "created_at": user.get("created_at", datetime.now(timezone.utc))
    }
""",

    "backend/app/routes/__init__.py": '"""API Routers package"""\n',

    "backend/app/routes/auth.py": """from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.modules.auth.schemas import (
    UserRegisterRequest,
    UserLoginRequest,
    UserResponse,
    TokenResponse,
    MessageResponse
)
from app.modules.auth.service import register_user, authenticate_user, get_current_user_by_id
from app.core.security import decode_access_token

router = APIRouter(prefix="/auth", tags=["Authentication"])
security = HTTPBearer()


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> UserResponse:
    token = credentials.credentials
    payload = decode_access_token(token)
    if not payload or "sub" not in payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired access token.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user_id = payload["sub"]
    user = await get_current_user_by_id(user_id)
    return UserResponse(**user)


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(payload: UserRegisterRequest):
    user = await register_user(payload)
    return UserResponse(**user)


@router.post("/login", response_model=TokenResponse)
async def login(payload: UserLoginRequest):
    auth_data = await authenticate_user(payload)
    return TokenResponse(**auth_data)


@router.get("/me", response_model=UserResponse)
async def get_profile(current_user: UserResponse = Depends(get_current_user)):
    return current_user


@router.post("/logout", response_model=MessageResponse)
async def logout():
    return MessageResponse(message="Successfully logged out.")
""",

    "backend/app/main.py": """from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.db.mongodb import connect_to_mongo, close_mongo_connection
from app.modules.auth.router import router as auth_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_to_mongo()
    yield
    await close_mongo_connection()


app = FastAPI(
    title="Student Academic Dashboard API",
    version="1.0.0",
    description="Backend for Personalized Student Academic Dashboard & Exam Preparation System",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)


@app.get("/", tags=["Health"])
async def root():
    return {
        "status": "online",
        "service": "Student Academic Dashboard API",
        "version": "1.0.0"
    }
""",

    # -------------------------------------------------------------
    # FRONTEND
    # -------------------------------------------------------------
    "frontend/package.json": """{
  "name": "student-academic-dashboard-frontend",
  "private": true,
  "version": "1.0.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview"
  },
  "dependencies": {
    "axios": "^1.6.8",
    "lucide-react": "^0.363.0",
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-router-dom": "^6.22.3"
  },
  "devDependencies": {
    "@types/react": "^18.2.66",
    "@types/react-dom": "^18.2.22",
    "@vitejs/plugin-react": "^4.2.1",
    "autoprefixer": "^10.4.19",
    "postcss": "^8.4.38",
    "tailwindcss": "^3.4.1",
    "vite": "^5.1.6"
  }
}
""",

    "frontend/vite.config.js": """import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    host: true
  }
})
""",

    "frontend/tailwind.config.js": """/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}
""",

    "frontend/postcss.config.js": """export default {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  },
}
""",

    "frontend/index.html": """<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>AcadPrep - Student Academic & Exam Prep Dashboard</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
  </head>
  <body class="bg-slate-50 text-slate-900 font-sans antialiased">
    <div id="root"></div>
    <script type="module" src="/src/main.jsx"></script>
  </body>
</html>
""",

    "frontend/.env.example": """VITE_API_BASE_URL=http://localhost:8000
""",

    "frontend/.env": """VITE_API_BASE_URL=http://localhost:8000
""",

    "frontend/.gitignore": """node_modules
dist
dist-ssr
*.local
.env
""",

    "frontend/src/index.css": """@tailwind base;
@tailwind components;
@tailwind utilities;

body {
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}
""",

    "frontend/src/services/api.js": """import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response && error.response.status === 401) {
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      if (window.location.pathname !== '/login' && window.location.pathname !== '/register') {
        window.location.href = '/login';
      }
    }
    return Promise.reject(error);
  }
);

export default api;
""",

    "frontend/src/services/authService.js": """import api from '../../../services/api';

export const authService = {
  async register(name, email, password) {
    const response = await api.post('/auth/register', { name, email, password });
    return response.data;
  },

  async login(email, password) {
    const response = await api.post('/auth/login', { email, password });
    return response.data;
  },

  async getCurrentUser() {
    const response = await api.get('/auth/me');
    return response.data;
  },

  async logout() {
    try {
      await api.post('/auth/logout');
    } catch {
      // Ignore network errors on logout
    } finally {
      localStorage.removeItem('token');
      localStorage.removeItem('user');
    }
  },
};
""",

    "frontend/src/context/AuthContext.jsx": """import React, { createContext, useContext, useState, useEffect } from 'react';
import { authService } from '../features/auth/services/authService';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const initAuth = async () => {
      const token = localStorage.getItem('token');
      if (token) {
        try {
          const userData = await authService.getCurrentUser();
          setUser(userData);
          localStorage.setItem('user', JSON.stringify(userData));
        } catch {
          localStorage.removeItem('token');
          localStorage.removeItem('user');
          setUser(null);
        }
      }
      setLoading(false);
    };

    initAuth();
  }, []);

  const login = async (email, password) => {
    const data = await authService.login(email, password);
    localStorage.setItem('token', data.access_token);
    localStorage.setItem('user', JSON.stringify(data.user));
    setUser(data.user);
    return data.user;
  };

  const register = async (name, email, password) => {
    return await authService.register(name, email, password);
  };

  const logout = async () => {
    await authService.logout();
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, loading, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
""",

    "frontend/src/components/ProtectedRoute.jsx": """import React from 'react';
  import { Navigate } from 'react-router-dom';
  import { useAuth } from '../../context/AuthContext';

export const ProtectedRoute = ({ children }) => {
  const { user, loading } = useAuth();

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-50">
        <div className="flex flex-col items-center gap-3">
          <div className="w-8 h-8 border-4 border-indigo-600 border-t-transparent rounded-full animate-spin"></div>
          <p className="text-sm font-medium text-slate-600">Verifying session...</p>
        </div>
      </div>
    );
  }

  if (!user) {
    return <Navigate to="/login" replace />;
  }

  return children;
};
""",

    "frontend/src/components/PublicRoute.jsx": """import React from 'react';
  import { Navigate } from 'react-router-dom';
  import { useAuth } from '../../context/AuthContext';

export const PublicRoute = ({ children }) => {
  const { user, loading } = useAuth();

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-50">
        <div className="w-8 h-8 border-4 border-indigo-600 border-t-transparent rounded-full animate-spin"></div>
      </div>
    );
  }

  if (user) {
    return <Navigate to="/dashboard" replace />;
  }

  return children;
};
""",

    "frontend/src/components/Navbar.jsx": """import React from 'react';
  import { GraduationCap, LogOut, User } from 'lucide-react';
  import { useAuth } from '../../context/AuthContext';

export const Navbar = () => {
  const { user, logout } = useAuth();

  return (
    <header className="bg-white border-b border-slate-200 sticky top-0 z-30">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16 items-center">
          <div className="flex items-center gap-3">
            <div className="bg-indigo-600 text-white p-2 rounded-xl shadow-sm">
              <GraduationCap className="w-6 h-6" />
            </div>
            <div>
              <span className="font-bold text-lg text-slate-900 tracking-tight">AcadPrep</span>
              <span className="hidden sm:inline-block ml-2 text-xs bg-indigo-50 text-indigo-700 font-semibold px-2 py-0.5 rounded-full border border-indigo-100">
                Phase 1 MVP
              </span>
            </div>
          </div>

          {user && (
            <div className="flex items-center gap-4">
              <div className="flex items-center gap-2 px-3 py-1.5 bg-slate-100 rounded-lg text-sm text-slate-700">
                <User className="w-4 h-4 text-slate-500" />
                <span className="font-medium">{user.name}</span>
              </div>
              <button
                onClick={logout}
                className="flex items-center gap-1.5 text-sm font-medium text-rose-600 hover:text-rose-700 hover:bg-rose-50 px-3 py-1.5 rounded-lg transition-colors cursor-pointer"
                title="Log out of your account"
              >
                <LogOut className="w-4 h-4" />
                <span>Logout</span>
              </button>
            </div>
          )}
        </div>
      </div>
    </header>
  );
};
""",

    "frontend/src/components/ModuleCard.jsx": """import React from 'react';
import { ArrowUpRight } from 'lucide-react';

export const ModuleCard = ({ title, description, icon: Icon, color, status = "Upcoming in Phase 2" }) => {
  return (
    <div className="bg-white rounded-2xl border border-slate-200/80 p-6 shadow-sm hover:shadow-md transition-all duration-200 flex flex-col justify-between group">
      <div>
        <div className="flex items-center justify-between mb-4">
          <div className={`p-3 rounded-xl ${color}`}>
            <Icon className="w-6 h-6" />
          </div>
          <span className="text-[11px] font-semibold tracking-wide uppercase px-2.5 py-1 bg-slate-100 text-slate-600 rounded-full">
            {status}
          </span>
        </div>
        <h3 className="text-lg font-semibold text-slate-900 group-hover:text-indigo-600 transition-colors">
          {title}
        </h3>
        <p className="text-sm text-slate-500 mt-2 leading-relaxed">
          {description}
        </p>
      </div>

      <div className="mt-6 pt-4 border-t border-slate-100 flex items-center justify-between text-xs text-slate-400">
        <span>Module placeholder</span>
        <ArrowUpRight className="w-4 h-4 opacity-50 group-hover:opacity-100 group-hover:translate-x-0.5 group-hover:-translate-y-0.5 transition-all" />
      </div>
    </div>
  );
};
""",

    "frontend/src/pages/LoginPage.jsx": """import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { GraduationCap, Mail, Lock, AlertCircle, ArrowRight, Loader2 } from 'lucide-react';
import { useAuth } from '../../../context/AuthContext';

export const LoginPage = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    if (!email || !password) {
      setError('Please fill in both email and password.');
      return;
    }

    try {
      setLoading(true);
      await login(email, password);
      navigate('/dashboard');
    } catch (err) {
      const msg = err.response?.data?.detail || 'Failed to sign in. Please verify your credentials.';
      setError(msg);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex flex-col justify-center items-center px-4 py-12 bg-slate-50">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center p-3 bg-indigo-600 text-white rounded-2xl shadow-indigo-200 shadow-lg mb-3">
            <GraduationCap className="w-8 h-8" />
          </div>
          <h1 className="text-2xl font-bold tracking-tight text-slate-900">
            Student Academic Dashboard
          </h1>
          <p className="text-sm text-slate-500 mt-1">
            Exam Preparation & Academic Management System
          </p>
        </div>

        <div className="bg-white p-8 rounded-2xl border border-slate-200 shadow-sm">
          <h2 className="text-xl font-semibold text-slate-900 mb-6">Welcome back</h2>

          {error && (
            <div className="mb-5 p-3.5 bg-rose-50 border border-rose-200 text-rose-700 text-sm rounded-xl flex items-start gap-2.5">
              <AlertCircle className="w-5 h-5 flex-shrink-0 mt-0.5" />
              <span>{error}</span>
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-xs font-semibold uppercase tracking-wider text-slate-600 mb-1.5">
                Email Address
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-slate-400">
                  <Mail className="w-4 h-4" />
                </div>
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="student@example.com"
                  required
                  className="w-full pl-10 pr-4 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 transition-all text-slate-900 placeholder-slate-400"
                />
              </div>
            </div>

            <div>
              <label className="block text-xs font-semibold uppercase tracking-wider text-slate-600 mb-1.5">
                Password
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-slate-400">
                  <Lock className="w-4 h-4" />
                </div>
                <input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••"
                  required
                  className="w-full pl-10 pr-4 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 transition-all text-slate-900 placeholder-slate-400"
                />
              </div>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full mt-2 py-2.5 px-4 bg-indigo-600 hover:bg-indigo-700 disabled:bg-indigo-400 text-white font-medium rounded-xl text-sm shadow-sm transition-all flex items-center justify-center gap-2 cursor-pointer disabled:cursor-not-allowed"
            >
              {loading ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  <span>Signing in...</span>
                </>
              ) : (
                <>
                  <span>Sign In</span>
                  <ArrowRight className="w-4 h-4" />
                </>
              )}
            </button>
          </form>

          <div className="mt-6 text-center text-sm text-slate-500">
            Don't have an account?{' '}
            <Link to="/register" className="font-semibold text-indigo-600 hover:text-indigo-700">
              Create an account
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
};
""",

    "frontend/src/pages/RegisterPage.jsx": """import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { GraduationCap, Mail, Lock, User, AlertCircle, ArrowRight, Loader2, CheckCircle2 } from 'lucide-react';
import { useAuth } from '../../../context/AuthContext';

export const RegisterPage = () => {
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [loading, setLoading] = useState(false);

  const { register } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');

    if (!name.trim()) {
      setError('Please provide your full name.');
      return;
    }

    if (password.length < 6) {
      setError('Password must be at least 6 characters long.');
      return;
    }

    if (password !== confirmPassword) {
      setError('Passwords do not match.');
      return;
    }

    try {
      setLoading(true);
      await register(name, email, password);
      setSuccess('Account created successfully! Redirecting to login...');
      setTimeout(() => {
        navigate('/login');
      }, 1500);
    } catch (err) {
      const msg = err.response?.data?.detail || 'Failed to create account. Please try again.';
      setError(msg);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex flex-col justify-center items-center px-4 py-12 bg-slate-50">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center p-3 bg-indigo-600 text-white rounded-2xl shadow-indigo-200 shadow-lg mb-3">
            <GraduationCap className="w-8 h-8" />
          </div>
          <h1 className="text-2xl font-bold tracking-tight text-slate-900">
            Student Academic Dashboard
          </h1>
          <p className="text-sm text-slate-500 mt-1">
            Exam Preparation & Academic Management System
          </p>
        </div>

        <div className="bg-white p-8 rounded-2xl border border-slate-200 shadow-sm">
          <h2 className="text-xl font-semibold text-slate-900 mb-6">Create your account</h2>

          {error && (
            <div className="mb-5 p-3.5 bg-rose-50 border border-rose-200 text-rose-700 text-sm rounded-xl flex items-start gap-2.5">
              <AlertCircle className="w-5 h-5 flex-shrink-0 mt-0.5" />
              <span>{error}</span>
            </div>
          )}

          {success && (
            <div className="mb-5 p-3.5 bg-emerald-50 border border-emerald-200 text-emerald-700 text-sm rounded-xl flex items-start gap-2.5">
              <CheckCircle2 className="w-5 h-5 flex-shrink-0 mt-0.5" />
              <span>{success}</span>
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-xs font-semibold uppercase tracking-wider text-slate-600 mb-1.5">
                Full Name
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-slate-400">
                  <User className="w-4 h-4" />
                </div>
                <input
                  type="text"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  placeholder="John Doe"
                  required
                  className="w-full pl-10 pr-4 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 transition-all text-slate-900 placeholder-slate-400"
                />
              </div>
            </div>

            <div>
              <label className="block text-xs font-semibold uppercase tracking-wider text-slate-600 mb-1.5">
                Email Address
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-slate-400">
                  <Mail className="w-4 h-4" />
                </div>
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="student@example.com"
                  required
                  className="w-full pl-10 pr-4 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 transition-all text-slate-900 placeholder-slate-400"
                />
              </div>
            </div>

            <div>
              <label className="block text-xs font-semibold uppercase tracking-wider text-slate-600 mb-1.5">
                Password
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-slate-400">
                  <Lock className="w-4 h-4" />
                </div>
                <input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="Minimum 6 characters"
                  required
                  className="w-full pl-10 pr-4 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 transition-all text-slate-900 placeholder-slate-400"
                />
              </div>
            </div>

            <div>
              <label className="block text-xs font-semibold uppercase tracking-wider text-slate-600 mb-1.5">
                Confirm Password
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-slate-400">
                  <Lock className="w-4 h-4" />
                </div>
                <input
                  type="password"
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  placeholder="Re-enter password"
                  required
                  className="w-full pl-10 pr-4 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 transition-all text-slate-900 placeholder-slate-400"
                />
              </div>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full mt-2 py-2.5 px-4 bg-indigo-600 hover:bg-indigo-700 disabled:bg-indigo-400 text-white font-medium rounded-xl text-sm shadow-sm transition-all flex items-center justify-center gap-2 cursor-pointer disabled:cursor-not-allowed"
            >
              {loading ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  <span>Registering...</span>
                </>
              ) : (
                <>
                  <span>Create Account</span>
                  <ArrowRight className="w-4 h-4" />
                </>
              )}
            </button>
          </form>

          <div className="mt-6 text-center text-sm text-slate-500">
            Already registered?{' '}
            <Link to="/login" className="font-semibold text-indigo-600 hover:text-indigo-700">
              Back to sign in
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
};
""",

    "frontend/src/pages/DashboardPage.jsx": """import React from 'react';
  import { useAuth } from '../../../context/AuthContext';
  import { Navbar } from '../../../components/layout/Navbar';
  import { ModuleCard } from '../components/ModuleCard';
import {
  BookOpen,
  FileQuestion,
  CheckSquare,
  BarChart3,
  Bot,
  Sparkles
} from 'lucide-react';

export const DashboardPage = () => {
  const { user } = useAuth();

  const modules = [
    {
      title: "Course Progress",
      description: "Track curriculum completion, topic coverage, and daily study milestones.",
      icon: BookOpen,
      color: "bg-blue-50 text-blue-600"
    },
    {
      title: "PYQs (Previous Years)",
      description: "University past question papers categorized by subject, term, and marks weightage.",
      icon: FileQuestion,
      color: "bg-amber-50 text-amber-600"
    },
    {
      title: "Topic-wise Quizzes",
      description: "Practice multiple choice and subjective quizzes with immediate concept explanations.",
      icon: CheckSquare,
      color: "bg-emerald-50 text-emerald-600"
    },
    {
      title: "Performance Analytics",
      description: "Weak area identification, exam readiness score, and predictive grade estimates.",
      icon: BarChart3,
      color: "bg-purple-50 text-purple-600"
    },
    {
      title: "AI Exam Assistant",
      description: "Smart tutor for doubt clearing, syllabus summarization, and customized revision plans.",
      icon: Bot,
      color: "bg-rose-50 text-rose-600"
    }
  ];

  return (
    <div className="min-h-screen bg-slate-50">
      <Navbar />

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
        <div className="bg-gradient-to-r from-indigo-700 via-indigo-600 to-indigo-800 rounded-3xl p-8 sm:p-10 text-white shadow-xl shadow-indigo-100 mb-10 relative overflow-hidden">
          <div className="relative z-10 max-w-2xl">
            <div className="inline-flex items-center gap-2 bg-indigo-500/30 backdrop-blur-md px-3 py-1 rounded-full text-xs font-medium text-indigo-100 mb-4 border border-indigo-400/20">
              <Sparkles className="w-3.5 h-3.5 text-amber-300" />
              <span>Phase 1 Authentication & Dashboard Shell</span>
            </div>
            <h1 className="text-3xl sm:text-4xl font-extrabold tracking-tight">
              Welcome back, {user?.name || 'Student'}! 👋
            </h1>
            <p className="mt-2 text-indigo-100 text-sm sm:text-base leading-relaxed">
              Your examination prep hub is ready. Future modules below will be incrementally integrated as you proceed with Phase 2.
            </p>
          </div>
          <div className="absolute right-0 -bottom-10 w-80 h-80 bg-white/5 rounded-full blur-2xl pointer-events-none" />
          <div className="absolute right-40 -top-10 w-60 h-60 bg-indigo-400/10 rounded-full blur-xl pointer-events-none" />
        </div>

        <div>
          <div className="flex items-center justify-between mb-6">
            <div>
              <h2 className="text-xl font-bold text-slate-900 tracking-tight">Academic Modules</h2>
              <p className="text-sm text-slate-500">Upcoming preparation modules planned for implementation</p>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {modules.map((mod, index) => (
              <ModuleCard
                key={index}
                title={mod.title}
                description={mod.description}
                icon={mod.icon}
                color={mod.color}
              />
            ))}
          </div>
        </div>
      </main>
    </div>
  );
};
""",

    "frontend/src/App.jsx": """import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import { ProtectedRoute } from './components/guards/ProtectedRoute';
import { PublicRoute } from './components/guards/PublicRoute';
import { LoginPage } from './features/auth/pages/LoginPage';
import { RegisterPage } from './features/auth/pages/RegisterPage';
import { DashboardPage } from './features/dashboard/pages/DashboardPage';

export function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <Routes>
          <Route path="/" element={<Navigate to="/dashboard" replace />} />
          <Route
            path="/login"
            element={
              <PublicRoute>
                <LoginPage />
              </PublicRoute>
            }
          />
          <Route
            path="/register"
            element={
              <PublicRoute>
                <RegisterPage />
              </PublicRoute>
            }
          />
          <Route
            path="/dashboard"
            element={
              <ProtectedRoute>
                <DashboardPage />
              </ProtectedRoute>
            }
          />
          <Route path="*" element={<Navigate to="/dashboard" replace />} />
        </Routes>
      </AuthProvider>
    </BrowserRouter>
  );
}

export default App;
""",

    "frontend/src/main.jsx": """import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.jsx'
import './index.css'

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)
""",

  ".gitignore": """backend/.env
backend/venv/
frontend/node_modules/
frontend/dist/
__pycache__/
*.py[cod]
""",

  "README.md": """# Mini Project

Student Academic Dashboard with an independent FastAPI backend and React + Vite frontend.

## Backend

```powershell
cd backend
python -m venv venv
.\\venv\\Scripts\\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

## Frontend

```powershell
cd frontend
npm install
npm run dev
```

The backend uses MongoDB. Copy `backend/.env.example` to `backend/.env` and adjust the connection settings before starting the API.
""",

  "backend/app/core/__init__.py": """\"\"\"Global configuration and security helpers.\"\"\"\n""",
  "backend/app/db/__init__.py": """\"\"\"Database connection and index definitions.\"\"\"\n""",
  "backend/app/db/indexes.py": """\"\"\"Database index definitions.\"\"\"\n\n\ndef ensure_indexes(database):
  return database[\"users\"].create_index(\"email\", unique=True)
""",
  "backend/app/modules/__init__.py": """\"\"\"Business modules.\"\"\"\n""",
  "backend/app/modules/auth/__init__.py": """\"\"\"Authentication module.\"\"\"\n""",
  "backend/app/modules/courses/__init__.py": """\"\"\"Course tracking module.\"\"\"\n""",
  "backend/app/modules/pyqs/__init__.py": """\"\"\"Previous-year question papers module.\"\"\"\n""",
  "backend/app/modules/quizzes/__init__.py": """\"\"\"Quiz module.\"\"\"\n""",
  "backend/app/modules/analytics/__init__.py": """\"\"\"Analytics module.\"\"\"\n""",
  "backend/app/modules/ai_assistant/__init__.py": """\"\"\"AI assistant module.\"\"\"\n""",
  "frontend/src/assets/.gitkeep": "",
  "frontend/src/components/ui/.gitkeep": "",
  "frontend/src/components/layout/.gitkeep": "",
  "frontend/src/components/guards/.gitkeep": "",
  "frontend/src/features/auth/components/.gitkeep": "",
  "frontend/src/features/auth/services/.gitkeep": "",
  "frontend/src/features/auth/pages/.gitkeep": "",
  "frontend/src/features/dashboard/components/.gitkeep": "",
  "frontend/src/features/dashboard/pages/.gitkeep": "",
  "frontend/src/features/courses/.gitkeep": "",
  "frontend/src/features/pyqs/.gitkeep": "",
  "frontend/src/features/quizzes/.gitkeep": "",
  "frontend/src/features/analytics/.gitkeep": "",
  "frontend/src/features/ai_assistant/.gitkeep": ""
}

LEGACY_MOVES = {
  "backend/app/config.py": "backend/app/core/config.py",
  "backend/app/utils/security.py": "backend/app/core/security.py",
  "backend/app/database/connection.py": "backend/app/db/mongodb.py",
  "backend/app/database/__init__.py": "backend/app/db/__init__.py",
  "backend/app/models/user.py": "backend/app/modules/auth/schemas.py",
  "backend/app/models/__init__.py": "backend/app/modules/auth/__init__.py",
  "backend/app/services/auth_service.py": "backend/app/modules/auth/service.py",
  "backend/app/services/__init__.py": "backend/app/modules/auth/__init__.py",
  "backend/app/routes/auth.py": "backend/app/modules/auth/router.py",
  "backend/app/routes/__init__.py": "backend/app/modules/auth/__init__.py",
  "frontend/src/components/ProtectedRoute.jsx": "frontend/src/components/guards/ProtectedRoute.jsx",
  "frontend/src/components/PublicRoute.jsx": "frontend/src/components/guards/PublicRoute.jsx",
  "frontend/src/components/Navbar.jsx": "frontend/src/components/layout/Navbar.jsx",
  "frontend/src/components/ModuleCard.jsx": "frontend/src/features/dashboard/components/ModuleCard.jsx",
  "frontend/src/pages/LoginPage.jsx": "frontend/src/features/auth/pages/LoginPage.jsx",
  "frontend/src/pages/RegisterPage.jsx": "frontend/src/features/auth/pages/RegisterPage.jsx",
  "frontend/src/pages/DashboardPage.jsx": "frontend/src/features/dashboard/pages/DashboardPage.jsx",
  "frontend/src/services/authService.js": "frontend/src/features/auth/services/authService.js"
}

def create_project():
    print(f"Creating project files in: {PROJECT_ROOT}")
    created_count = 0
    for relative_path, content in FILES.items():
        full_path = os.path.join(PROJECT_ROOT, relative_path.replace("/", os.sep))
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with open(full_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"  [+] Created: {relative_path}")
        created_count += 1

    for source, target in LEGACY_MOVES.items():
        source_path = os.path.join(PROJECT_ROOT, source.replace("/", os.sep))
        target_path = os.path.join(PROJECT_ROOT, target.replace("/", os.sep))
        os.makedirs(os.path.dirname(target_path), exist_ok=True)
        os.replace(source_path, target_path)
        print(f"  [>] Moved: {source} -> {target}")

    for legacy_directory in (
      "backend/app/config.py",
      "backend/app/database",
      "backend/app/models",
      "backend/app/routes",
      "backend/app/services",
      "backend/app/utils",
      "frontend/src/pages",
    ):
      legacy_path = os.path.join(PROJECT_ROOT, legacy_directory.replace("/", os.sep))
      if os.path.isdir(legacy_path):
        shutil.rmtree(legacy_path)
    
    print(f"\n Successfully generated all {created_count} files!")
    print("\nNext steps:")
    print("1. Set up backend:")
    print("   cd backend")
    print("   python -m venv venv")
    print("   .\\venv\\Scripts\\activate")
    print("   pip install -r requirements.txt")
    print("   uvicorn app.main:app --reload --port 8000")
    print("\n2. Set up frontend in a separate terminal:")
    print("   cd ..\\frontend")
    print("   npm install")
    print("   npm run dev")

if __name__ == "__main__":
    create_project()