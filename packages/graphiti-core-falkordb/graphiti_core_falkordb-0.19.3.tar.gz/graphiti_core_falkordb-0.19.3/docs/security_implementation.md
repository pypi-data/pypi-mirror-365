# Graphiti Server Security Implementation

## Overview

This document describes the comprehensive security implementation for the Graphiti server, including authentication, authorization, data isolation, and safety restrictions.

## Security Features

### 1. Authentication & Authorization
- **API Key Authentication**: Bearer token authentication using secure API keys
- **User Context**: Each request includes user context with permissions
- **Admin vs User Access**: Different permission levels for different operations

### 2. Data Isolation (Group ID Enforcement)
- **Mandatory Group IDs**: All operations require valid group_id for data isolation
- **Group Access Control**: Users can only access groups they have permission for
- **Cross-Group Prevention**: No accidental data leakage between groups

### 3. Rate Limiting
- **Request Throttling**: Configurable rate limits per user/IP
- **Abuse Prevention**: Protects against DoS and excessive usage
- **Sliding Window**: Time-based rate limiting with configurable windows

### 4. Input Validation & Sanitization
- **Group ID Validation**: Strict alphanumeric + dash/underscore only
- **Schema Validation**: All inputs validated against Pydantic schemas
- **SQL Injection Prevention**: Parameterized queries throughout

### 5. Security Headers
- **OWASP Compliance**: Standard security headers on all responses
- **XSS Protection**: Content Security Policy and XSS prevention
- **HTTPS Enforcement**: Strict Transport Security headers

## Configuration

### Environment Variables

```bash
# Security Enforcement
GRAPHITI_SECURITY_ENABLED=true                    # Enable/disable security
GRAPHITI_API_KEY=your_secure_api_key_here         # API key for authentication
GRAPHITI_JWT_SECRET=your_jwt_secret_here           # JWT secret (if using JWT)

# Data Isolation
GRAPHITI_REQUIRE_GROUP_ID=true                     # Require group_id for all operations
GRAPHITI_ALLOWED_GROUPS=group1,group2,group3      # Comma-separated allowed groups

# Rate Limiting
GRAPHITI_RATE_LIMIT_REQUESTS=100                   # Max requests per window
GRAPHITI_RATE_LIMIT_WINDOW=3600                    # Time window in seconds
```

### Security Levels

#### Development (Permissive)
```bash
GRAPHITI_SECURITY_ENABLED=false
GRAPHITI_REQUIRE_GROUP_ID=false
GRAPHITI_RATE_LIMIT_REQUESTS=1000
```

#### Production (Strict)
```bash
GRAPHITI_SECURITY_ENABLED=true
GRAPHITI_REQUIRE_GROUP_ID=true
GRAPHITI_ALLOWED_GROUPS=tenant1,tenant2,tenant3
GRAPHITI_RATE_LIMIT_REQUESTS=50
GRAPHITI_RATE_LIMIT_WINDOW=3600
```

#### Multi-Tenant SaaS
```bash
GRAPHITI_SECURITY_ENABLED=true
GRAPHITI_REQUIRE_GROUP_ID=true
GRAPHITI_ALLOWED_GROUPS=customer_123,customer_456
GRAPHITI_RATE_LIMIT_REQUESTS=200
```

## API Usage

### Authentication

All requests must include a Bearer token:

```bash
curl -H "Authorization: Bearer your_api_key_here" \
     "http://localhost:8000/entities/my_group/paginated"
```

### Group ID Requirements

All operations require a valid group_id:

```bash
# ✅ Valid - includes group_id
POST /entities/
{
  "group_id": "customer_123",
  "name": "John Smith",
  "entity_type": "Customer"
}

# ❌ Invalid - missing group_id (if REQUIRE_GROUP_ID=true)
POST /entities/
{
  "name": "John Smith",
  "entity_type": "Customer"
}
```

### Error Responses

#### Authentication Required
```json
{
  "detail": "Authentication required",
  "status_code": 401
}
```

#### Group Access Denied
```json
{
  "detail": "Access denied to group 'restricted_group'. User does not have permission.",
  "status_code": 403
}
```

#### Rate Limit Exceeded
```json
{
  "detail": "Rate limit exceeded: 100 requests per 3600 seconds",
  "status_code": 429
}
```

#### Invalid Group ID
```json
{
  "detail": "group_id \"invalid@group\" must contain only alphanumeric characters, dashes, or underscores",
  "status_code": 400
}
```

## Implementation Details

### Security Middleware

The security system uses FastAPI dependencies:

```python
# All protected endpoints use this dependency
async def security_dependency(
    request: Request,
    user: UserContext = Depends(get_current_user)
) -> UserContext:
    # Rate limiting
    await enforce_rate_limit(user)
    return user

# Group access validation
async def validate_group_access(
    group_id: str,
    user: UserContext = Depends(security_dependency)
) -> str:
    return validate_and_authorize_group(group_id, user)
```

### Protected Endpoints

All entity and data endpoints are protected:

```python
@router.post("/entities/")
async def create_entity(
    request: CreateEntityRequest,
    graphiti: ZepGraphitiDep,
    user: UserContext = Depends(security_dependency),  # ← Security enforced
):
    # Validate group access
    validated_group_id = validate_and_authorize_group(request.group_id, user)
    # ... rest of implementation
```

### User Context

Each authenticated request includes user context:

```python
class UserContext(BaseModel):
    user_id: str                    # Unique user identifier
    allowed_groups: Set[str]        # Groups user can access
    is_admin: bool = False          # Admin privileges
    rate_limit_key: str            # Key for rate limiting
```

## Security Monitoring

### Logging

Security events are logged for monitoring:

```python
# Example security log entries
SECURITY_EVENT: UNAUTHORIZED_ACCESS - User: unknown - Details: {"endpoint": "/entities/", "ip": "192.168.1.1"}
SECURITY_EVENT: RATE_LIMIT_EXCEEDED - User: api_key_user - Details: {"requests": 101, "window": 3600}
SECURITY_EVENT: GROUP_ACCESS_DENIED - User: user_123 - Details: {"group": "restricted_group", "action": "read"}
```

### Monitoring Endpoints

```bash
# Check security configuration
GET /security-config

# Health check (unauthenticated)
GET /healthcheck
```

## Best Practices

### 1. API Key Management
- Generate strong API keys: `openssl rand -hex 32`
- Rotate keys regularly
- Use different keys for different environments
- Store keys securely (environment variables, secrets management)

### 2. Group ID Strategy
- Use meaningful, hierarchical group IDs: `company_123`, `project_456`
- Implement consistent naming conventions
- Document group access patterns
- Regular access reviews

### 3. Rate Limiting
- Set appropriate limits based on usage patterns
- Monitor rate limit violations
- Implement exponential backoff in clients
- Consider different limits for different user types

### 4. Monitoring & Alerting
- Monitor authentication failures
- Alert on rate limit violations
- Track group access patterns
- Log security events for audit

## Migration Guide

### Enabling Security on Existing Installation

1. **Set Environment Variables**:
   ```bash
   export GRAPHITI_SECURITY_ENABLED=true
   export GRAPHITI_API_KEY=$(openssl rand -hex 32)
   export GRAPHITI_REQUIRE_GROUP_ID=true
   ```

2. **Update Client Code**:
   ```python
   # Add authentication header
   headers = {"Authorization": f"Bearer {api_key}"}
   
   # Ensure all requests include group_id
   data = {"group_id": "my_group", ...}
   ```

3. **Test Security**:
   ```bash
   # Should fail without auth
   curl http://localhost:8000/entities/my_group/paginated
   
   # Should succeed with auth
   curl -H "Authorization: Bearer $API_KEY" \
        http://localhost:8000/entities/my_group/paginated
   ```

### Gradual Rollout

1. **Phase 1**: Enable security but allow unauthenticated access
   ```bash
   GRAPHITI_SECURITY_ENABLED=false
   GRAPHITI_REQUIRE_GROUP_ID=true
   ```

2. **Phase 2**: Require authentication but allow all groups
   ```bash
   GRAPHITI_SECURITY_ENABLED=true
   GRAPHITI_REQUIRE_GROUP_ID=true
   GRAPHITI_ALLOWED_GROUPS=  # Empty = allow all
   ```

3. **Phase 3**: Full security with group restrictions
   ```bash
   GRAPHITI_SECURITY_ENABLED=true
   GRAPHITI_REQUIRE_GROUP_ID=true
   GRAPHITI_ALLOWED_GROUPS=prod_group1,prod_group2
   ```

This security implementation ensures that Graphiti can be safely deployed in production environments with proper data isolation, authentication, and abuse prevention.
