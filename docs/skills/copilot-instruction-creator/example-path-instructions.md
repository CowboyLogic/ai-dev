# API Layer Instructions

These instructions apply to all API-related files, backend services, and server-side code.

## API Design Principles
- Follow RESTful API design patterns
- Use consistent HTTP status codes
- Implement proper content negotiation
- Version APIs appropriately (URL versioning preferred)
- Document all endpoints with OpenAPI/Swagger

## Authentication & Authorization
- Implement JWT or OAuth 2.0 for authentication
- Use role-based access control (RBAC)
- Validate tokens on every request
- Implement proper session management
- Log authentication failures for security monitoring

## Data Validation
- Validate all input data on the server side
- Use schema validation libraries (Joi, Yup, etc.)
- Sanitize user inputs to prevent injection attacks
- Implement proper type checking
- Return meaningful validation error messages

## Error Handling
- Use consistent error response format
- Implement proper HTTP status codes
- Log errors with appropriate levels
- Don't expose sensitive information in error messages
- Implement graceful degradation

## Security Best Practices
- Implement HTTPS for all endpoints
- Use security headers (CSP, HSTS, etc.)
- Implement rate limiting and throttling
- Validate and sanitize all inputs
- Use parameterized queries to prevent SQL injection
- Implement CORS policies appropriately

## Performance Optimization
- Implement caching strategies (Redis, in-memory)
- Use database indexes appropriately
- Implement pagination for large datasets
- Optimize database queries
- Use connection pooling
- Implement request/response compression

## Logging & Monitoring
- Log all API requests and responses
- Implement structured logging
- Monitor response times and error rates
- Set up alerts for critical issues
- Use correlation IDs for request tracing

## Testing Strategy
- Write unit tests for all business logic
- Implement integration tests for API endpoints
- Use test databases for testing
- Mock external dependencies
- Test error scenarios and edge cases