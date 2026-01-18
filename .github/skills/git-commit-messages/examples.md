# Git Commit Message Examples

This file contains examples of good and bad commit messages to illustrate best practices.

## Good Commit Messages

### Feature Additions

```
feat(auth): implement JWT token refresh mechanism

Add automatic token refresh functionality to prevent user
session timeouts. Includes retry logic for failed refresh
attempts and proper error handling.

- Add TokenRefreshService class
- Implement exponential backoff for retries
- Update auth middleware to handle refresh
- Add configuration options for refresh timing

Closes #123
```

```
feat(dashboard): add interactive data visualization

Implement chart.js integration with real-time data updates.
- Add chart component library
- Create data transformation utilities
- Implement WebSocket data streaming
- Add responsive design for mobile devices

Resolves #456
```

### Bug Fixes

```
fix(validation): prevent XSS in user input fields

Sanitize HTML input to prevent cross-site scripting attacks.
Replace dangerous HTML tags with safe alternatives and
add content security policy headers.

- Add input sanitization middleware
- Implement HTML escaping for user content
- Add CSP headers to responses
- Update existing forms to use sanitized inputs

Fixes #789
```

```
fix(memory): resolve memory leak in file upload handler

Fix memory accumulation when processing large file uploads.
Implement proper stream cleanup and add file size limits.

- Add stream.destroy() in error handlers
- Implement file size validation
- Add timeout for stalled uploads
- Update error logging for debugging
```

### Documentation Updates

```
docs(api): update authentication endpoint documentation

Add comprehensive examples for OAuth2 flows and clarify
parameter requirements. Include error response formats
and rate limiting information.

- Add code examples for each grant type
- Document all required and optional parameters
- Include error response schemas
- Add troubleshooting section
```

### Refactoring

```
refactor(database): extract query builder to separate module

Move complex SQL query construction logic into dedicated
QueryBuilder class for better maintainability and testing.

- Create lib/query-builder.js module
- Move 5 query methods from DatabaseService
- Add comprehensive unit tests
- Update existing service to use new module
- Improve error handling and logging
```

### Performance Improvements

```
perf(api): optimize database queries with indexes

Reduce query execution time by 60% through strategic
indexing and query optimization.

- Add composite index on user_id + created_at
- Optimize JOIN operations in user queries
- Implement query result caching
- Add database query monitoring
```

## Bad Commit Messages

### Too Vague

```
fix bug
update code
changes
fix issue
```

### Too Long

```
fix the authentication system because users were having problems logging in when they tried to use the forgot password feature and it wasn't working properly so I had to update the email service configuration and also fix the validation logic
```

### Wrong Tense

```
Fixed the login bug
Added new feature
Updated documentation
```

### Unprofessional

```
finally fixed this stupid bug
hack to make it work
quick fix for demo
```

### Irrelevant Information

```
late night commit - fix memory leak
coffee break - add error handling
friday afternoon - refactor code
```

## Commit Message Templates

### Feature Template

```
feat({{scope}}): {{brief description}}

{{detailed explanation of the feature}}

{{bullet points of changes made}}

{{issue references}}
```

### Bug Fix Template

```
fix({{scope}}): {{brief description}}

{{explanation of the bug and fix}}

{{steps taken to resolve}}

{{testing performed}}

{{issue references}}
```

### Breaking Change Template

```
{{type}}({{scope}}): {{brief description}}

{{explanation of changes}}

BREAKING CHANGE: {{description of breaking changes}}

{{migration instructions}}

{{issue references}}
```

## Conventional Commit Types Reference

| Type | Description | Example |
|------|-------------|---------|
| feat | New feature | feat(auth): add OAuth login |
| fix | Bug fix | fix(api): resolve null pointer exception |
| docs | Documentation | docs(readme): update installation guide |
| style | Code style | style(lint): fix eslint errors |
| refactor | Code refactoring | refactor(utils): simplify date helpers |
| test | Testing | test(auth): add login integration tests |
| chore | Maintenance | chore(deps): update dependencies |
| perf | Performance | perf(db): optimize query performance |
| ci | CI/CD | ci(pipeline): add automated deployment |
| build | Build system | build(webpack): update bundler config |

## Scope Guidelines

Use specific scopes that match your project structure:

- **Component names**: `auth`, `dashboard`, `api`, `database`
- **File/feature areas**: `validation`, `routing`, `styling`
- **Third-party**: `deps`, `config`, `build`
- **General**: Use when change affects multiple areas

## Quick Reference

### Subject Line Checklist
- [ ] Under 50 characters
- [ ] Starts with capital letter
- [ ] No ending punctuation
- [ ] Imperative mood ("Add" not "Added")
- [ ] Specific and descriptive

### Body Checklist
- [ ] Separated from subject by blank line
- [ ] Wrapped at 72 characters
- [ ] Explains what and why
- [ ] Uses bullet points for lists
- [ ] References issues when applicable

### Footer Checklist
- [ ] BREAKING CHANGE: for breaking changes
- [ ] Closes/Fixes/Refs: for issue references
- [ ] Co-authored-by: for multiple authors