---
name: entity-framework
description: Specialized skill for Entity Framework Core operations in the Happy Camper Planner project. Handles PostgreSQL database operations, complex entity relationships, JSONB columns, migrations, performance optimization, data seeding, and camping/RV domain model patterns. Use when working with EF Core, database operations, migrations, or query optimization.
---

# Entity Framework Core Skill for Happy Camper Planner

This skill provides specialized guidance for Entity Framework Core operations in the Happy Camper Planner collaborative camping trip planning application using PostgreSQL.

## When to Use This Skill

Use this skill when you need to:
- Create or modify entity models and relationships
- Generate and manage EF Core migrations
- Optimize database queries and resolve performance issues
- Work with JSONB columns and complex data types
- Create database seeding and test data
- Configure entity relationships and constraints
- Debug EF Core issues or analyze query execution
- Implement repository patterns or data access layers

## Technology Context

### Database Stack
- **PostgreSQL 16** as primary database
- **Entity Framework Core** with Npgsql provider
- **JSONB columns** for flexible metadata storage
- **Composite primary keys** for junction tables
- **Docker PostgreSQL** for development environment

### Connection Configuration
```csharp
// Development connection string
Host=db;Database=happy_camper_db;Username=camper_admin;Password=dev_password_123
```

## Domain Model Architecture

### Core Entities and Relationships

**User System (1:1 Relationship)**
```csharp
public class User
{
    public Guid Id { get; set; }
    [Required]
    public string PrimaryEmail { get; set; } = string.Empty;
    public string DisplayName { get; set; } = string.Empty;
    public string? ProfilePicUrl { get; set; }
    public DateTime CreatedAt { get; set; } = DateTime.UtcNow;

    // Navigation Properties
    public UserProfile? Profile { get; set; }
    public ICollection<PlanMember> PlanMemberships { get; set; } = new List<PlanMember>();
}

public class UserProfile
{
    [Key, ForeignKey("User")]
    public Guid UserId { get; set; }
    
    // JSONB columns for flexible data
    [Column(TypeName = "jsonb")]
    public JsonDocument? SocialLinks { get; set; }
    
    [Column(TypeName = "jsonb")]
    public JsonDocument? PrivacySettings { get; set; }
    
    // RV specifications for compatibility matching
    public string? RvManufacturer { get; set; }
    public string? RvModel { get; set; }
    public int? RvYear { get; set; }
    public double? RvLength { get; set; }
    public double? RvWidth { get; set; }
    public double? RvHeight { get; set; }

    public User User { get; set; } = null!;
}
```

**Plan System (1:Many + Junction Table)**
```csharp
public class Plan
{
    public Guid Id { get; set; }
    [Required]
    public string Title { get; set; } = string.Empty;
    public int SeasonYear { get; set; }
    public Guid OwnerId { get; set; }
    public bool IsPublic { get; set; }
    public DateTime CreatedAt { get; set; } = DateTime.UtcNow;

    public ICollection<Trip> Trips { get; set; } = new List<Trip>();
    public ICollection<PlanMember> Members { get; set; } = new List<PlanMember>();
    public ICollection<GearItem> GearItems { get; set; } = new List<GearItem>();
}

// Junction table with additional properties
public class PlanMember
{
    public Guid PlanId { get; set; }
    public Guid UserId { get; set; }
    public PermissionLevel Permission { get; set; }

    public Plan Plan { get; set; } = null!;
    public User User { get; set; } = null!;
}
```

## DbContext Configuration Patterns

### ApplicationDbContext Setup
```csharp
public class ApplicationDbContext : DbContext
{
    public ApplicationDbContext(DbContextOptions<ApplicationDbContext> options) : base(options) { }

    public DbSet<User> Users { get; set; }
    public DbSet<UserProfile> UserProfiles { get; set; }
    public DbSet<Plan> Plans { get; set; }
    public DbSet<PlanMember> PlanMembers { get; set; }
    public DbSet<Trip> Trips { get; set; }
    public DbSet<Reservation> Reservations { get; set; }
    public DbSet<GearItem> GearItems { get; set; }
    public DbSet<MealPlan> MealPlans { get; set; }

    protected override void OnModelCreating(ModelBuilder modelBuilder)
    {
        ConfigureUserEntities(modelBuilder);
        ConfigurePlanEntities(modelBuilder);
        ConfigureIndexes(modelBuilder);
        ConfigureJsonColumns(modelBuilder);
        
        base.OnModelCreating(modelBuilder);
    }
}
```

### Entity Configuration Patterns

**One-to-One Relationships**
```csharp
private static void ConfigureUserEntities(ModelBuilder modelBuilder)
{
    // User-UserProfile 1:1 relationship
    modelBuilder.Entity<User>()
        .HasOne(u => u.Profile)
        .WithOne(p => p.User)
        .HasForeignKey<UserProfile>(p => p.UserId)
        .OnDelete(DeleteBehavior.Cascade);
}
```

**Composite Keys for Junction Tables**
```csharp
private static void ConfigurePlanEntities(ModelBuilder modelBuilder)
{
    // PlanMember composite primary key
    modelBuilder.Entity<PlanMember>()
        .HasKey(pm => new { pm.PlanId, pm.UserId });

    modelBuilder.Entity<PlanMember>()
        .HasOne(pm => pm.Plan)
        .WithMany(p => p.Members)
        .HasForeignKey(pm => pm.PlanId)
        .OnDelete(DeleteBehavior.Cascade);

    modelBuilder.Entity<PlanMember>()
        .HasOne(pm => pm.User)
        .WithMany(u => u.PlanMemberships)
        .HasForeignKey(pm => pm.UserId)
        .OnDelete(DeleteBehavior.Cascade);
}
```

**Performance Indexes**
```csharp
private static void ConfigureIndexes(ModelBuilder modelBuilder)
{
    // Frequently queried fields
    modelBuilder.Entity<Plan>()
        .HasIndex(p => p.SeasonYear)
        .HasDatabaseName("IX_Plans_SeasonYear");
    
    modelBuilder.Entity<Trip>()
        .HasIndex(t => t.StartDate)
        .HasDatabaseName("IX_Trips_StartDate");
    
    modelBuilder.Entity<User>()
        .HasIndex(u => u.PrimaryEmail)
        .IsUnique()
        .HasDatabaseName("IX_Users_PrimaryEmail");
}
```

**JSONB Column Configuration**
```csharp
private static void ConfigureJsonColumns(ModelBuilder modelBuilder)
{
    modelBuilder.Entity<UserProfile>()
        .Property(up => up.SocialLinks)
        .HasColumnType("jsonb");
    
    modelBuilder.Entity<UserProfile>()
        .Property(up => up.PrivacySettings)
        .HasColumnType("jsonb");
        
    // Enable JSONB querying
    modelBuilder.Entity<UserProfile>()
        .Property(up => up.DietaryRestrictions)
        .HasConversion(
            v => JsonSerializer.Serialize(v, (JsonSerializerOptions)null),
            v => JsonSerializer.Deserialize<List<string>>(v, (JsonSerializerOptions)null));
}
```

## Migration Management

### Creating Migrations
```bash
# From the API project directory
dotnet ef migrations add AddUserProfileEnhancements -o Infrastructure/Migrations

# Generate SQL script for review
dotnet ef migrations script --from 20240110000000_InitialCreate --to 20240115000000_AddUserProfileEnhancements
```

### Migration Best Practices
```csharp
public partial class AddRvCompatibilityFields : Migration
{
    protected override void Up(MigrationBuilder migrationBuilder)
    {
        // Add new columns with default values for existing rows
        migrationBuilder.AddColumn<double?>(
            name: "RvLength",
            table: "UserProfiles", 
            type: "double precision",
            nullable: true);
            
        // Create indexes for performance
        migrationBuilder.CreateIndex(
            name: "IX_UserProfiles_RvLength",
            table: "UserProfiles",
            column: "RvLength");
    }

    protected override void Down(MigrationBuilder migrationBuilder)
    {
        migrationBuilder.DropIndex(
            name: "IX_UserProfiles_RvLength",
            table: "UserProfiles");
            
        migrationBuilder.DropColumn(
            name: "RvLength",
            table: "UserProfiles");
    }
}
```

## Query Optimization Patterns

### Efficient Include Strategies
```csharp
// Load complete plan with all related data
var plan = await _context.Plans
    .Include(p => p.Members)
        .ThenInclude(m => m.User)
            .ThenInclude(u => u.Profile) // Include RV specs for compatibility
    .Include(p => p.Trips)
        .ThenInclude(t => t.Reservations)
    .Include(p => p.GearItems)
    .AsSplitQuery() // Prevent cartesian explosion
    .FirstOrDefaultAsync(p => p.Id == planId);
```

### Performance-Optimized Queries
```csharp
// Read-only queries for better performance
var upcomingTrips = await _context.Trips
    .AsNoTracking()
    .Where(t => t.StartDate > DateTime.UtcNow)
    .Where(t => t.Plan.Members.Any(m => m.UserId == userId))
    .Select(t => new TripSummary
    {
        Id = t.Id,
        PlanTitle = t.Plan.Title,
        StartDate = t.StartDate,
        EndDate = t.EndDate
    })
    .ToListAsync();
```

### JSONB Querying
```csharp
// Query JSONB columns using EF.Functions
var usersWithInstagram = await _context.UserProfiles
    .Where(up => EF.Functions.JsonExists(up.SocialLinks, "$.instagram"))
    .Select(up => new { up.UserId, up.User.DisplayName })
    .ToListAsync();

// Query nested JSONB properties
var privateProfiles = await _context.UserProfiles
    .Where(up => EF.Functions.JsonExtract<bool>(up.PrivacySettings, "$.profileVisibility") == false)
    .ToListAsync();
```

### RV Compatibility Queries
```csharp
// Find campgrounds compatible with user's RV
var compatibleCampgrounds = await _context.Campgrounds
    .Where(c => userProfile.RvLength == null || c.MaxRvLength >= userProfile.RvLength)
    .Where(c => userProfile.RvWidth == null || c.MaxRvWidth >= userProfile.RvWidth)
    .Where(c => userProfile.RvHeight == null || c.MaxRvHeight >= userProfile.RvHeight)
    .Where(c => string.IsNullOrEmpty(userProfile.ElectricalRequirement) || 
               c.AvailableElectrical.Contains(userProfile.ElectricalRequirement))
    .ToListAsync();
```

## Data Seeding Strategies

### Development Seed Data
```csharp
public static class DatabaseSeeder
{
    public static async Task SeedDevelopmentData(ApplicationDbContext context)
    {
        if (!context.Users.Any())
        {
            await SeedUsers(context);
            await SeedPlans(context);
            await SeedTrips(context);
        }
    }

    private static async Task SeedUsers(ApplicationDbContext context)
    {
        var users = new[]
        {
            new User 
            { 
                Id = Guid.Parse("550e8400-e29b-41d4-a716-446655440001"),
                PrimaryEmail = "alex@example.com",
                DisplayName = "Alex Thompson",
                CreatedAt = DateTime.UtcNow.AddMonths(-6)
            },
            new User 
            { 
                Id = Guid.Parse("550e8400-e29b-41d4-a716-446655440002"),
                PrimaryEmail = "sarah@example.com", 
                DisplayName = "Sarah Johnson",
                CreatedAt = DateTime.UtcNow.AddMonths(-4)
            }
        };

        context.Users.AddRange(users);
        await context.SaveChangesAsync();

        // Add profiles with RV specifications
        var profiles = new[]
        {
            new UserProfile
            {
                UserId = users[0].Id,
                RvManufacturer = "Airstream",
                RvModel = "Flying Cloud",
                RvYear = 2022,
                RvLength = 25,
                RvWidth = 8.5,
                RvHeight = 9.7,
                SocialLinks = JsonDocument.Parse("""{"instagram": "@alexcamping", "twitter": "@alexrv"}"""),
                DietaryRestrictions = new List<string> { "Vegetarian" }
            }
        };

        context.UserProfiles.AddRange(profiles);
        await context.SaveChangesAsync();
    }
}
```

### Test Data Factories
```csharp
public static class TestDataFactory
{
    public static User CreateUser(string email = "test@example.com", string name = "Test User")
    {
        return new User
        {
            Id = Guid.NewGuid(),
            PrimaryEmail = email,
            DisplayName = name,
            CreatedAt = DateTime.UtcNow
        };
    }

    public static Plan CreatePlan(Guid ownerId, int seasonYear = 2024, string title = "Test Plan")
    {
        return new Plan
        {
            Id = Guid.NewGuid(),
            Title = title,
            SeasonYear = seasonYear,
            OwnerId = ownerId,
            CreatedAt = DateTime.UtcNow
        };
    }

    public static PlanMember CreatePlanMember(Guid planId, Guid userId, PermissionLevel permission = PermissionLevel.Viewer)
    {
        return new PlanMember
        {
            PlanId = planId,
            UserId = userId,
            Permission = permission
        };
    }
}
```

## Common Database Scenarios

### Scenario 1: Adding New Entity with Relationships
```csharp
// Adding a new entity that references multiple existing entities
var mealPlan = new MealPlan
{
    Id = Guid.NewGuid(),
    TripId = tripId,
    MealType = MealType.Dinner,
    PlannedDate = DateTime.Today.AddDays(3),
    ResponsibleUserId = currentUserId,
    Description = "Grilled salmon with vegetables"
};

context.MealPlans.Add(mealPlan);
await context.SaveChangesAsync();
```

### Scenario 2: Complex Updates with Business Rules
```csharp
// Update plan membership with validation
var membership = await context.PlanMembers
    .FirstOrDefaultAsync(pm => pm.PlanId == planId && pm.UserId == userId);

if (membership == null)
    throw new NotFoundException("Plan membership not found");

// Business rule: Can't demote the plan owner
var plan = await context.Plans.FirstOrDefaultAsync(p => p.Id == planId);
if (plan.OwnerId == userId && newPermission != PermissionLevel.Admin)
    throw new BusinessRuleException("Plan owner must maintain Admin permissions");

membership.Permission = newPermission;
await context.SaveChangesAsync();
```

### Scenario 3: Bulk Operations for Performance
```csharp
// Bulk update gear items claimed status
var gearItemIds = request.GearItemIds;
await context.GearItems
    .Where(gi => gearItemIds.Contains(gi.Id))
    .Where(gi => gi.ClaimedByUserId == null) // Only unclaimed items
    .ExecuteUpdateAsync(gi => gi.SetProperty(g => g.ClaimedByUserId, currentUserId));
```

## Performance Monitoring

### Query Analysis
```csharp
// Enable sensitive data logging in development
protected override void OnConfiguring(DbContextOptionsBuilder optionsBuilder)
{
    if (IsDevelopment)
    {
        optionsBuilder.EnableSensitiveDataLogging();
        optionsBuilder.LogTo(Console.WriteLine, LogLevel.Information);
    }
}

// Analyze query execution time
var stopwatch = Stopwatch.StartNew();
var results = await context.Plans
    .Where(/* complex query */)
    .ToListAsync();
stopwatch.Stop();

if (stopwatch.ElapsedMilliseconds > 100)
{
    logger.LogWarning("Slow query detected: {ElapsedMs}ms", stopwatch.ElapsedMilliseconds);
}
```

### Database Index Recommendations
```sql
-- Common indexes for Happy Camper domain queries
CREATE INDEX CONCURRENTLY IX_Plans_SeasonYear_IsPublic ON Plans (SeasonYear, IsPublic);
CREATE INDEX CONCURRENTLY IX_Trips_StartDate_PlanId ON Trips (StartDate, PlanId);
CREATE INDEX CONCURRENTLY IX_UserProfiles_RvLength_RvWidth ON UserProfiles (RvLength, RvWidth) WHERE RvLength IS NOT NULL;

-- JSONB GIN indexes for flexible querying
CREATE INDEX CONCURRENTLY IX_UserProfiles_SocialLinks_gin ON UserProfiles USING gin (SocialLinks);
CREATE INDEX CONCURRENTLY IX_UserProfiles_PrivacySettings_gin ON UserProfiles USING gin (PrivacySettings);
```

## Testing Patterns

### In-Memory Database Setup
```csharp
[TestClass]
public class PlanRepositoryTests
{
    private ApplicationDbContext _context;

    [TestInitialize]
    public void Setup()
    {
        var options = new DbContextOptionsBuilder<ApplicationDbContext>()
            .UseInMemoryDatabase(databaseName: Guid.NewGuid().ToString())
            .Options;

        _context = new ApplicationDbContext(options);

        // Seed test data
        SeedTestData();
    }

    [TestCleanup]
    public void Cleanup()
    {
        _context.Dispose();
    }
}
```

### Integration Testing with PostgreSQL
```csharp
public class IntegrationTestFixture : IAsyncLifetime
{
    private readonly PostgreSqlContainer _container = new PostgreSqlBuilder()
        .WithImage("postgres:16-alpine")
        .WithDatabase("happy_camper_test")
        .WithUsername("test_user")
        .WithPassword("test_password")
        .Build();

    public ApplicationDbContext CreateContext()
    {
        var options = new DbContextOptionsBuilder<ApplicationDbContext>()
            .UseNpgsql(_container.GetConnectionString())
            .Options;

        return new ApplicationDbContext(options);
    }

    public async Task InitializeAsync()
    {
        await _container.StartAsync();
        using var context = CreateContext();
        await context.Database.MigrateAsync();
    }
}
```

## Error Handling and Diagnostics

### Common EF Core Issues and Solutions

**Issue**: N+1 Query Problem
```csharp
// Problem: Loads plans then queries for each plan's members
var plans = await context.Plans.ToListAsync();
foreach (var plan in plans)
{
    Console.WriteLine($"Members: {plan.Members.Count}"); // Triggers N queries
}

// Solution: Use Include to load related data
var plans = await context.Plans
    .Include(p => p.Members)
    .ToListAsync();
```

**Issue**: Cartesian Explosion with Multiple Includes
```csharp
// Problem: Large result set due to cartesian product
var plan = await context.Plans
    .Include(p => p.Members)
    .Include(p => p.Trips)
    .Include(p => p.GearItems)
    .FirstOrDefaultAsync(p => p.Id == planId);

// Solution: Use AsSplitQuery or separate queries
var plan = await context.Plans
    .Include(p => p.Members)
    .Include(p => p.Trips)
    .Include(p => p.GearItems)
    .AsSplitQuery()
    .FirstOrDefaultAsync(p => p.Id == planId);
```

**Issue**: Concurrency Conflicts
```csharp
// Handle optimistic concurrency
try
{
    await context.SaveChangesAsync();
}
catch (DbUpdateConcurrencyException ex)
{
    foreach (var entry in ex.Entries)
    {
        if (entry.Entity is Plan plan)
        {
            var databaseValues = await entry.GetDatabaseValuesAsync();
            if (databaseValues == null)
            {
                // Entity was deleted
                throw new NotFoundException("Plan was deleted by another user");
            }
            
            // Refresh with current database values
            entry.OriginalValues.SetValues(databaseValues);
        }
    }
    
    await context.SaveChangesAsync(); // Retry
}
```

Remember: This skill automatically activates when working on Entity Framework Core tasks. Always consider performance, data integrity, and the camping/RV domain context in your database operations.