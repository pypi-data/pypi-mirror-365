---
id: security-authentication-patterns
title: Authentication and Authorization Patterns
category: security
subcategory: identity-management
version: 1.8.0
tags: [security, authentication, authorization, jwt, oauth2, rbac]
author: Security Team
created: 2024-01-10
lastUpdated: 2025-01-18
applicability: [startup, growth, enterprise, cloud-native]
techStack: [python, fastapi, jwt, oauth2, redis]
prerequisites: [http-security, cryptography-basics]
relatedGuidelines: [api-security, data-protection]
---

# Authentication and Authorization Patterns

Implementing robust authentication and authorization is critical for application security. This guideline covers proven patterns for identity management in modern applications.

## Core Security Principles

1. **Authentication**: Verify who the user is
2. **Authorization**: Determine what the user can do
3. **Principle of Least Privilege**: Grant minimum necessary permissions
4. **Defense in Depth**: Multiple layers of security controls

## Pattern: JWT-Based Authentication

### Description
Use JSON Web Tokens (JWT) for stateless authentication with proper validation and security measures.

### When to use
- Stateless authentication requirements
- Microservices architectures
- Mobile and SPA applications
- When you need scalable authentication

### Implementation
Generate, validate, and manage JWT tokens with appropriate security measures.

### Consequences
- Stateless and scalable
- Self-contained tokens
- Can't revoke tokens easily
- Token size can be large

### Example: JWT Implementation
```python
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta
from typing import Optional
import os

app = FastAPI()
security = HTTPBearer()

# Configuration
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class AuthService:
    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None):
        """Create JWT access token."""
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({"exp": expire, "iat": datetime.utcnow()})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    
    def verify_token(self, token: str) -> dict:
        """Verify and decode JWT token."""
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            username: str = payload.get("sub")
            if username is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid authentication credentials"
                )
            return payload
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials"
            )

auth_service = AuthService()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get current authenticated user."""
    token = credentials.credentials
    payload = auth_service.verify_token(token)
    
    user = user_service.get_user_by_username(payload.get("sub"))
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    return user

@app.post("/auth/login")
async def login(login_data: LoginRequest):
    """Authenticate user and return JWT token."""
    user = user_service.authenticate_user(login_data.username, login_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )
    
    access_token = auth_service.create_access_token(
        data={"sub": user.username, "user_id": user.id, "roles": user.roles}
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/users/me")
async def get_current_user_profile(current_user = Depends(get_current_user)):
    """Get current user profile - requires authentication."""
    return current_user
```

## Pattern: Role-Based Access Control (RBAC)

### Description
Implement authorization using roles and permissions to control access to resources.

### When to use
- When you have different user types with different permissions
- For enterprise applications with complex permission requirements
- When you need fine-grained access control

### Implementation
Define roles, permissions, and implement middleware to check authorization.

### Consequences
- Fine-grained access control
- Scalable permission management
- Clear separation of concerns
- Increased complexity

### Example: RBAC Implementation
```python
from functools import wraps
from enum import Enum
from typing import List, Set

class Permission(Enum):
    READ_USERS = "read:users"
    WRITE_USERS = "write:users"
    DELETE_USERS = "delete:users"
    READ_ORDERS = "read:orders"
    WRITE_ORDERS = "write:orders"
    ADMIN_ACCESS = "admin:access"

class Role(Enum):
    USER = "user"
    MODERATOR = "moderator"
    ADMIN = "admin"

# Role-Permission mapping
ROLE_PERMISSIONS = {
    Role.USER: {Permission.READ_ORDERS, Permission.WRITE_ORDERS},
    Role.MODERATOR: {
        Permission.READ_USERS, Permission.READ_ORDERS, 
        Permission.WRITE_ORDERS
    },
    Role.ADMIN: {
        Permission.READ_USERS, Permission.WRITE_USERS, Permission.DELETE_USERS,
        Permission.READ_ORDERS, Permission.WRITE_ORDERS, Permission.ADMIN_ACCESS
    }
}

class AuthorizationService:
    def user_has_permission(self, user: User, permission: Permission) -> bool:
        """Check if user has a specific permission."""
        user_permissions = set()
        
        for role_name in user.roles:
            try:
                role = Role(role_name)
                user_permissions.update(ROLE_PERMISSIONS.get(role, set()))
            except ValueError:
                continue
        
        return permission in user_permissions
    
    def require_permission(self, permission: Permission):
        """Decorator to require specific permission."""
        def decorator(func):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                # Get current user from dependency injection
                current_user = kwargs.get('current_user')
                if not current_user:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Authentication required"
                    )
                
                if not self.user_has_permission(current_user, permission):
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail=f"Permission required: {permission.value}"
                    )
                
                return await func(*args, **kwargs)
            return wrapper
        return decorator

auth_service = AuthorizationService()

# Usage in endpoints
@app.get("/admin/users")
@auth_service.require_permission(Permission.READ_USERS)
async def list_all_users(current_user = Depends(get_current_user)):
    """List all users - requires read:users permission."""
    return user_service.get_all_users()

@app.delete("/admin/users/{user_id}")
@auth_service.require_permission(Permission.DELETE_USERS)
async def delete_user(user_id: str, current_user = Depends(get_current_user)):
    """Delete user - requires delete:users permission."""
    return user_service.delete_user(user_id)
```

## Pattern: OAuth2 Integration

### Description
Implement OAuth2 for third-party authentication and authorization.

### When to use
- When integrating with external identity providers
- For social login functionality
- When building APIs that need to access third-party services

### Implementation
Use OAuth2 flows with proper token management and validation.

### Consequences
- Delegated authentication
- Access to third-party APIs
- Improved user experience
- Complex token management

### Example: OAuth2 Integration
```python
from authlib.integrations.starlette_client import OAuth
from starlette.config import Config
from starlette.middleware.sessions import SessionMiddleware

config = Config('.env')
oauth = OAuth(config)

# Configure OAuth providers
oauth.register(
    name='google',
    client_id=config('GOOGLE_CLIENT_ID'),
    client_secret=config('GOOGLE_CLIENT_SECRET'),
    server_metadata_url='https://accounts.google.com/.well-known/openid_configuration',
    client_kwargs={
        'scope': 'openid email profile'
    }
)

app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)

@app.get("/auth/google")
async def google_login(request: Request):
    """Initiate Google OAuth2 login."""
    redirect_uri = request.url_for('google_callback')
    return await oauth.google.authorize_redirect(request, redirect_uri)

@app.get("/auth/google/callback")
async def google_callback(request: Request):
    """Handle Google OAuth2 callback."""
    try:
        token = await oauth.google.authorize_access_token(request)
        user_info = token.get('userinfo')
        
        if user_info:
            # Create or update user based on OAuth data
            user = user_service.create_or_update_oauth_user(
                provider='google',
                provider_user_id=user_info['sub'],
                email=user_info['email'],
                name=user_info['name']
            )
            
            # Generate our own JWT token
            access_token = auth_service.create_access_token(
                data={"sub": user.username, "user_id": user.id}
            )
            
            return {"access_token": access_token, "token_type": "bearer"}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="OAuth authentication failed"
        )
```

## Anti-pattern: Storing Passwords in Plain Text

### Description
Storing user passwords without proper hashing and encryption.

### Why it's bad
- Massive security vulnerability
- Violates basic security principles
- Legal and compliance issues
- Complete loss of user trust if breached

### Instead
Always hash passwords using strong, slow hashing algorithms like bcrypt, Argon2, or scrypt.

## Anti-pattern: Long-Lived Tokens Without Refresh

### Description
Using access tokens with very long expiration times without refresh token mechanism.

### Why it's bad
- Increases security risk if tokens are compromised
- No way to revoke access effectively
- Violates principle of short-lived credentials

### Instead
Use short-lived access tokens with refresh token mechanism for better security.

## Best Practices

1. **Use Strong Password Policies**
   - Minimum length requirements
   - Character complexity requirements
   - Password history to prevent reuse
   - Account lockout after failed attempts

2. **Implement Multi-Factor Authentication**
   - Support TOTP, SMS, or hardware tokens
   - Require MFA for sensitive operations
   - Provide backup recovery codes

3. **Secure Token Storage**
   - Use httpOnly cookies for web applications
   - Implement proper token rotation
   - Store refresh tokens securely
   - Implement token blacklisting

4. **Monitor Authentication Events**
   - Log all authentication attempts
   - Detect suspicious login patterns
   - Implement alerting for security events
   - Regular security audits

5. **Handle Session Management**
   - Implement proper session timeout
   - Secure session storage
   - Session invalidation on logout
   - Concurrent session limits