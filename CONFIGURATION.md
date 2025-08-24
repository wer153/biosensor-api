# Configuration Management with Pydantic Settings

This document describes the configuration management system implemented using `pydantic-settings` for the Biosensor API.

## Overview

The application now uses a centralized configuration system that provides:

- **Type Safety**: All configuration values are validated and typed
- **Environment Variable Loading**: Automatic loading from environment variables
- **Default Values**: Sensible defaults for development
- **Validation**: Automatic validation of configuration values
- **Documentation**: Self-documenting configuration with descriptions

## Configuration Structure

The configuration is organized into several modules:

### Main Configuration (`app/config.py`)

- `AppConfig`: Main application configuration
- `DatabaseConfig`: PostgreSQL database settings
- `RedisConfig`: Redis connection settings
- `AWSConfig`: AWS credentials and region
- `S3Config`: S3 bucket and file storage settings
- `JWTConfig`: JWT authentication configuration

## Environment Variables

### Database Configuration
- `DATABASE_URL`: PostgreSQL connection URL (required)
  - Example: `postgresql+asyncpg://user:pass@localhost:5432/biosensor`

### Redis Configuration
- `REDIS_URL`: Redis connection URL
  - Default: `redis://localhost:6379`

### AWS Configuration
- `AWS_ACCESS_KEY_ID`: AWS access key (required)
- `AWS_SECRET_ACCESS_KEY`: AWS secret key (required)
- `AWS_REGION`: AWS region
  - Default: `ap-northeast-2`

### S3 Configuration
- `AWS_S3_BUCKET_NAME`: S3 bucket name (required)
- `AWS_S3_PRESIGNED_URL_EXPIRY`: Presigned URL expiry in seconds
  - Default: `3600` (1 hour)

### JWT Configuration
- `JWT_SECRET`: JWT signing secret (required)
- `JWT_ACCESS_TOKEN_EXPIRE_MINUTES`: Access token expiry
  - Default: `30` minutes
- `JWT_REFRESH_TOKEN_EXPIRE_HOURS`: Refresh token expiry
  - Default: `24` hours

### Application Configuration
- `APP_NAME`: Application name
  - Default: `Biosensor API`
- `APP_VERSION`: Application version
  - Default: `0.1.0`
- `DEBUG`: Debug mode
  - Default: `false`
- `ENVIRONMENT`: Environment name (`development`, `staging`, `production`)
  - Default: `development`

### API Configuration
- `API_HOST`: Server host
  - Default: `0.0.0.0`
- `API_PORT`: Server port
  - Default: `8000`

### CORS Configuration
- `CORS_ALLOW_ORIGINS`: Allowed origins (comma-separated)
  - Default: `*`
- `CORS_ALLOW_CREDENTIALS`: Allow credentials
  - Default: `true`
- `CORS_ALLOW_METHODS`: Allowed methods (comma-separated)
  - Default: `*`
- `CORS_ALLOW_HEADERS`: Allowed headers (comma-separated)
  - Default: `*`

## Usage

### Accessing Configuration

```python
from app.config import settings

# Access database URL
db_url = settings.database.url

# Access S3 bucket name
bucket = settings.s3.bucket_name

# Access JWT secret
jwt_secret = settings.jwt.secret
```

### Environment File

Create a `.env` file in the project root with your configuration:

```env
DATABASE_URL=postgresql+asyncpg://biosensor_user:biosensor_pass@localhost:5432/biosensor
JWT_SECRET=your-super-secret-jwt-key
AWS_ACCESS_KEY_ID=your-access-key-id
AWS_SECRET_ACCESS_KEY=your-secret-access-key
AWS_S3_BUCKET_NAME=your-bucket-name
```

## Migration from os.getenv()

The following files have been updated to use the new configuration system:

- ✅ `src/app/services/s3_service.py` - S3 and AWS configuration
- ✅ `src/app/auth/jwt.py` - JWT configuration
- ✅ `src/app/services/redis_token_service.py` - Redis configuration
- ✅ `src/app/app_factory.py` - Database and CORS configuration
- ✅ `src/app/server.py` - Server host and port configuration

## Benefits

1. **Type Safety**: Configuration values are automatically validated and typed
2. **Centralized**: All configuration is managed in one place
3. **Environment Aware**: Easy switching between environments
4. **Documentation**: Self-documenting with field descriptions
5. **Validation**: Automatic validation prevents configuration errors
6. **IDE Support**: Full IDE autocomplete and type checking

## Error Handling

The configuration system will raise clear validation errors if:
- Required environment variables are missing
- Environment variables have invalid formats
- Database URLs don't use the correct driver

This ensures the application fails fast with clear error messages during startup rather than at runtime.
