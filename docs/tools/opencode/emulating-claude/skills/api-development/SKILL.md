---
name: api-development
description: Specialized skill for developing and testing .NET 8 Web API endpoints in the Happy Camper Planner project. Handles Entity Framework Core operations, JWT authentication, RBAC permissions, controller patterns, API testing, and camping/RV domain logic. Use when creating controllers, API endpoints, authentication flows, database operations, or API tests.
---

# API Development Skill for Happy Camper Planner

This skill provides specialized guidance for developing .NET 8 Web API endpoints in the Happy Camper Planner collaborative camping trip planning application.

## When to Use This Skill

Use this skill when you need to:
- Create new API controllers or endpoints
- Implement authentication and authorization logic
- Work with Entity Framework Core and PostgreSQL
- Handle complex domain relationships (Plans, Trips, Users, Reservations)
- Create API tests with JWT authentication
- Implement RBAC permission checks
- Debug API issues or optimize performance
- Generate API documentation or validation

## Architecture Context

### Technology Stack
- **.NET 8 ASP.NET Core Web API**
- **Entity Framework Core** with PostgreSQL (Npgsql)
- **JWT Bearer Authentication** via Firebase
- **Clean Architecture** with Domain/Controllers/Infrastructure separation
- **Docker** development environment

### Domain Model Key Entities
- `User` and `UserProfile` (1:1 relationship)
- `Plan` (annual trip collections) with `PlanMember` junction table
- `Trip` (individual campground stays) belonging to Plans
- `Reservation` and `MealPlan` linked to Trips
- `GearItem` shared across Plans
- **Permission System**: Viewer → Editor → Admin hierarchy

### Database Patterns
- **Current User Pattern**: Extract `CurrentUserId` from JWT claims using `User.FindFirstValue(ClaimTypes.NameIdentifier)`
- **Security-First**: Always check user permissions before data access
- **JSONB Storage**: Use `JsonDocument` for flexible metadata (`SocialLinks`, `PrivacySettings`)
- **Composite Keys**: Many-to-many relationships via junction tables

## Development Procedures

### 1. Creating New Controllers

**Standard Controller Pattern:**
```csharp
[Authorize] // Always require authentication
[ApiController]
[Route("api/[controller]")]
public class YourController : ControllerBase
{
    private readonly ApplicationDbContext _context;

    public YourController(ApplicationDbContext context)
    {
        _context = context;
    }

    // Helper to get current User ID from JWT
    private Guid CurrentUserId => Guid.Parse(User.FindFirstValue(ClaimTypes.NameIdentifier) 
        ?? throw new UnauthorizedAccessException("User ID not found in token."));
}
```

**Required Usings:**
```csharp
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using Microsoft.AspNetCore.Authorization;
using System.Security.Claims;
using HappyCamper.Domain.Entities;
using HappyCamper.Infrastructure;
```

### 2. Implementing RBAC Permission Checks

**Permission Validation Pattern:**
```csharp
// Check if user is Plan member with required permission level
private async Task<PlanMember?> ValidateUserPermission(Guid planId, PermissionLevel requiredLevel)
{
    var userId = CurrentUserId;
    var membership = await _context.PlanMembers
        .FirstOrDefaultAsync(pm => pm.PlanId == planId && pm.UserId == userId);
    
    if (membership == null) return null;
    if (membership.Permission < requiredLevel) return null;
    
    return membership;
}

// Usage in endpoints:
var membership = await ValidateUserPermission(planId, PermissionLevel.Editor);
if (membership == null) return Forbid();
```

**Permission Hierarchy:**
- `Viewer`: Can view plan details, trips, and member information
- `Editor`: Can add/edit trips, reservations, gear items, meal plans
- `Admin`: Can invite/remove members, change permissions, delete plan

### 3. Entity Framework Patterns

**Query Patterns with User Scoping:**
```csharp
// Always scope queries to current user's accessible data
var userPlans = await _context.Plans
    .Where(p => p.Members.Any(m => m.UserId == CurrentUserId))
    .Include(p => p.Members)
        .ThenInclude(m => m.User)
    .Include(p => p.Trips)
    .ToListAsync();
```

**Create Operations:**
```csharp
// Always set audit fields and user context
var entity = new Plan
{
    Id = Guid.NewGuid(),
    CreatedAt = DateTime.UtcNow,
    OwnerId = CurrentUserId,
    // ... other properties
};

_context.Plans.Add(entity);
await _context.SaveChangesAsync();

return CreatedAtAction(nameof(GetPlan), new { id = entity.Id }, entity);
```

**Update Operations with Concurrency:**
```csharp
try
{
    _context.Entry(entity).State = EntityState.Modified;
    await _context.SaveChangesAsync();
}
catch (DbUpdateConcurrencyException)
{
    if (!EntityExists(entity.Id))
        return NotFound();
    throw;
}
```

### 4. RV Compatibility and Domain Logic

**RV Profile Filtering:**
```csharp
// Filter campgrounds based on user's RV specifications
var userProfile = await _context.UserProfiles
    .FirstOrDefaultAsync(up => up.UserId == CurrentUserId);

if (userProfile?.RvLength.HasValue == true)
{
    query = query.Where(c => c.MaxRvLength >= userProfile.RvLength.Value);
}
```

**Business Rule Validation:**
```csharp
// Example: Validate trip dates don't overlap within a plan
private async Task<bool> ValidateNoOverlappingTrips(Guid planId, DateTime startDate, DateTime endDate, Guid? excludeTripId = null)
{
    var overlapping = await _context.Trips
        .Where(t => t.PlanId == planId 
            && (excludeTripId == null || t.Id != excludeTripId)
            && t.StartDate < endDate 
            && t.EndDate > startDate)
        .AnyAsync();
    
    return !overlapping;
}
```

### 5. API Response Patterns

**Standard Response Types:**
- `GET` single item: `ActionResult<T>` with `NotFound()` for missing items
- `GET` collections: `ActionResult<IEnumerable<T>>` or paginated results
- `POST` create: `CreatedAtAction()` with location header
- `PUT` update: `NoContent()` for successful updates
- `DELETE`: `NoContent()` for successful deletions

**Error Handling:**
```csharp
// Security errors - don't leak information
if (!userHasAccess) return Forbid(); // Not NotFound()

// Validation errors
if (!ModelState.IsValid) return BadRequest(ModelState);

// Business rule violations
if (!await ValidateBusinessRule())
    return BadRequest("Specific business rule error message");
```

### 6. API Testing Patterns

**Controller Test Setup:**
```csharp
[TestClass]
public class PlansControllerTests
{
    private ApplicationDbContext _context;
    private PlansController _controller;

    [TestInitialize]
    public void Setup()
    {
        var options = new DbContextOptionsBuilder<ApplicationDbContext>()
            .UseInMemoryDatabase(databaseName: Guid.NewGuid().ToString())
            .Options;
        
        _context = new ApplicationDbContext(options);
        
        // Mock JWT claims
        var claims = new List<Claim>
        {
            new Claim(ClaimTypes.NameIdentifier, "test-user-id")
        };
        var identity = new ClaimsIdentity(claims);
        var principal = new ClaimsPrincipal(identity);
        
        _controller = new PlansController(_context)
        {
            ControllerContext = new ControllerContext
            {
                HttpContext = new DefaultHttpContext { User = principal }
            }
        };
    }
}
```

**Integration Test Pattern:**
```csharp
// Test with proper JWT token
var token = GenerateJwtToken(userId);
client.DefaultRequestHeaders.Authorization = 
    new System.Net.Http.Headers.AuthenticationHeaderValue("Bearer", token);

var response = await client.GetAsync("/api/plans");
```

## Common Scenarios and Solutions

### Scenario 1: Creating a New Resource Endpoint

**Input**: "Create an endpoint to manage trip reservations"

**Steps**:
1. Add reservation-related methods to `TripsController` or create `ReservationsController`
2. Implement permission check (user must be Plan member with Editor+ permissions)
3. Add validation for reservation data (site numbers, confirmation codes)
4. Include user context in creation (`UserId` field)
5. Create corresponding tests with JWT authentication

### Scenario 2: Adding RV Compatibility Filter

**Input**: "Filter campgrounds based on user's RV specifications"

**Steps**:
1. Create specialized endpoint: `GET api/campgrounds/rv-compatible`
2. Load current user's RV profile from `UserProfile`
3. Apply filters for RV length, width, height, electrical requirements
4. Return campgrounds matching specifications with availability data

### Scenario 3: Implementing Collaborative Features

**Input**: "Add gear item claiming functionality"

**Steps**:
1. Add `ClaimedByUserId` to `GearItem` entity
2. Create `POST api/plans/{id}/gear/{itemId}/claim` endpoint
3. Validate user has Editor+ permissions on plan
4. Prevent double-claiming with business rule validation
5. Include claiming/unclaiming in API tests

### Scenario 4: Permission Management

**Input**: "Create endpoint to change member permissions"

**Steps**:
1. Add to `PlansController`: `PUT api/plans/{id}/members/{userId}/permissions`
2. Validate current user has Admin permissions
3. Enforce permission hierarchy (can't promote to higher than own level)
4. Update `PlanMember.Permission` field
5. Return updated member list

## Security Considerations

### Authentication Requirements
- **All endpoints** must have `[Authorize]` attribute
- **Extract user context** via `CurrentUserId` helper
- **Never trust client-provided user IDs**

### Authorization Patterns
- **Scope all queries** to current user's accessible data
- **Validate permissions** before any data modification
- **Use Forbid()** instead of NotFound() to avoid information leakage
- **Check business rules** in addition to basic permissions

### Data Validation
- **Validate all input** using Data Annotations and custom validation
- **Sanitize user content** especially for public-facing fields
- **Check entity relationships** before creating associations

## Performance Guidelines

### Entity Framework Optimization
- **Use Include()** for related data to avoid N+1 queries
- **Project only needed fields** with Select() for large datasets
- **Add database indexes** for frequently queried fields
- **Use AsNoTracking()** for read-only queries

### Caching Strategies
- **Cache reference data** (campground listings, state/country data)
- **Cache user profiles** for RV compatibility checks
- **Consider Redis** for session data and frequently accessed lookups

## API Documentation Standards

### Swagger/OpenAPI
- **Add XML comments** to controllers and actions
- **Use ProducesResponseType** attributes for clear response documentation
- **Document authentication** requirements and permission levels
- **Include example requests/responses** for complex endpoints

### Response Documentation
- **Standard error responses**: 400 (validation), 401 (auth), 403 (forbidden), 404 (not found)
- **Success responses**: 200 (get), 201 (created), 204 (updated/deleted)
- **Include response schemas** with property descriptions

Remember: This skill automatically activates when working on API-related tasks. Always prioritize security, maintainability, and the camping/RV domain context in your implementations.