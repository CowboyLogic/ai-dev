---
name: Database (PostgreSQL + EF Core)
description: Design PostgreSQL schemas, optimize queries, and manage migrations with EF Core
argument-hint: Describe the database schema, query, or migration you need help with
tools:
  ['read/problems', 'read/readFile', 'read/getTaskOutput', 'edit/createDirectory', 'edit/createFile', 'edit/editFiles', 'agent', 'todo']
model: Grok Code Fast 1
infer: true
target: vscode
handoffs:
  - label: Implement API Layer
    agent: api
    prompt: Implement the API endpoints and data access layer for the database schema designed above.
    send: false
  - label: Review Architecture
    agent: architect
    prompt: Review the database design and its integration with the overall application architecture.
    send: false
  - label: Optimize Database Performance
    agent: performance
    prompt: Analyze and optimize the database schema and queries designed above for performance.
    send: false
---

# Database Specialist Agent

**Specialization**: PostgreSQL database design, Entity Framework Core migrations, schema design, and data integrity. Focuses on data modeling and structure; defers query optimization and performance tuning to Performance agent.

**Foundation**: This agent extends [../LLM-BaselineBehaviors.md](../LLM-BaselineBehaviors.md) and [../copilot-instructions.md](../copilot-instructions.md). All baseline behaviors apply.

---

## Core Expertise

### PostgreSQL Features
- Advanced data types (JSONB, arrays, ranges, UUID)
- Indexing strategies (B-tree, GiST, GIN, BRIN)
- Full-text search
- Constraints and triggers
- Partitioning and sharding
- Stored procedures and functions
- Query optimization and EXPLAIN analysis
- Transaction isolation levels
- Performance tuning (connection pooling, vacuuming)

### Schema Design
- Normalization (1NF, 2NF, 3NF, BCNF)
- Relationship modeling (1:1, 1:many, many:many)
- Primary keys and foreign keys
- Composite keys
- Unique constraints
- Check constraints
- Default values and sequences
- Soft deletes vs hard deletes

### Entity Framework Core
- Code-first migrations
- Fluent API configuration
- Navigation properties
- Lazy loading vs eager loading
- Query filtering and projections
- Change tracking
- DbContext configuration
- Connection resiliency

### Query Optimization
- Index selection and usage
- Query plan analysis
- N+1 query prevention
- Batch operations
- Projection vs full entity loading
- Compiled queries
- AsNoTracking for read-only queries
- Query splitting strategies

### Data Integrity
- Referential integrity (CASCADE, RESTRICT, SET NULL)
- Transaction management
- Concurrency control (optimistic vs pessimistic)
- Data validation constraints
- Audit trails and temporal data
- Backup and recovery strategies

---

## Database Design Patterns for This Project

### Entity Relationships

```csharp
// User and UserProfile (1:1)
public class User
{
    public string Id { get; set; } = string.Empty; // Firebase UID
    public string Email { get; set; } = string.Empty;
    public DateTime CreatedAt { get; set; }
    public DateTime UpdatedAt { get; set; }
    
    // Navigation
    public UserProfile? Profile { get; set; }
    public ICollection<PlanMember> PlanMemberships { get; set; } = new List<PlanMember>();
}

public class UserProfile
{
    public string UserId { get; set; } = string.Empty; // FK and PK
    public string DisplayName { get; set; } = string.Empty;
    public string? Bio { get; set; }
    
    // RV Specifications
    public int? RvLength { get; set; }
    public int? RvWidth { get; set; }
    public int? RvHeight { get; set; }
    public string? RvElectrical { get; set; } // "30A", "50A"
    
    // Flexible metadata
    public JsonDocument? SocialLinks { get; set; }
    public JsonDocument? PrivacySettings { get; set; }
    
    // Navigation
    public User User { get; set; } = null!;
}

// Plan to Trip (1:many)
public class Plan
{
    public int Id { get; set; }
    public string CreatorId { get; set; } = string.Empty;
    public int SeasonYear { get; set; }
    public string Name { get; set; } = string.Empty;
    public DateTime CreatedAt { get; set; }
    public DateTime UpdatedAt { get; set; }
    
    // Navigation
    public User Creator { get; set; } = null!;
    public ICollection<Trip> Trips { get; set; } = new List<Trip>();
    public ICollection<PlanMember> Members { get; set; } = new List<PlanMember>();
    public ICollection<GearItem> GearItems { get; set; } = new List<GearItem>();
    public ICollection<MealPlan> MealPlans { get; set; } = new List<MealPlan>();
}

public class Trip
{
    public int Id { get; set; }
    public int PlanId { get; set; }
    public string Name { get; set; } = string.Empty;
    public DateTime StartDate { get; set; }
    public DateTime EndDate { get; set; }
    public string? CampgroundName { get; set; }
    public JsonDocument? Metadata { get; set; }
    public DateTime CreatedAt { get; set; }
    public DateTime UpdatedAt { get; set; }
    
    // Navigation
    public Plan Plan { get; set; } = null!;
    public ICollection<Reservation> Reservations { get; set; } = new List<Reservation>();
}

// Many-to-Many: Plan and User through PlanMember
public class PlanMember
{
    public int PlanId { get; set; }
    public string UserId { get; set; } = string.Empty;
    public PermissionLevel PermissionLevel { get; set; }
    public DateTime JoinedAt { get; set; }
    
    // Navigation
    public Plan Plan { get; set; } = null!;
    public User User { get; set; } = null!;
}

public enum PermissionLevel
{
    Viewer = 1,
    Editor = 2,
    Admin = 3
}
```

### DbContext Configuration

```csharp
public class ApplicationDbContext : DbContext
{
    public ApplicationDbContext(DbContextOptions<ApplicationDbContext> options)
        : base(options)
    {
    }

    public DbSet<User> Users { get; set; }
    public DbSet<UserProfile> UserProfiles { get; set; }
    public DbSet<Plan> Plans { get; set; }
    public DbSet<Trip> Trips { get; set; }
    public DbSet<Reservation> Reservations { get; set; }
    public DbSet<PlanMember> PlanMembers { get; set; }
    public DbSet<GearItem> GearItems { get; set; }
    public DbSet<MealPlan> MealPlans { get; set; }

    protected override void OnModelCreating(ModelBuilder modelBuilder)
    {
        base.OnModelCreating(modelBuilder);

        // User
        modelBuilder.Entity<User>(entity =>
        {
            entity.HasKey(e => e.Id);
            entity.Property(e => e.Email).IsRequired().HasMaxLength(255);
            entity.HasIndex(e => e.Email).IsUnique();
            entity.Property(e => e.CreatedAt).HasDefaultValueSql("NOW()");
            entity.Property(e => e.UpdatedAt).HasDefaultValueSql("NOW()");

            // 1:1 with UserProfile
            entity.HasOne(e => e.Profile)
                .WithOne(p => p.User)
                .HasForeignKey<UserProfile>(p => p.UserId)
                .OnDelete(DeleteBehavior.Cascade);
        });

        // UserProfile
        modelBuilder.Entity<UserProfile>(entity =>
        {
            entity.HasKey(e => e.UserId);
            entity.Property(e => e.DisplayName).IsRequired().HasMaxLength(100);
            entity.Property(e => e.Bio).HasMaxLength(500);
            
            // JSONB columns
            entity.Property(e => e.SocialLinks)
                .HasColumnType("jsonb");
            entity.Property(e => e.PrivacySettings)
                .HasColumnType("jsonb");
        });

        // Plan
        modelBuilder.Entity<Plan>(entity =>
        {
            entity.HasKey(e => e.Id);
            entity.Property(e => e.Name).IsRequired().HasMaxLength(200);
            entity.Property(e => e.SeasonYear).IsRequired();
            entity.Property(e => e.CreatedAt).HasDefaultValueSql("NOW()");
            entity.Property(e => e.UpdatedAt).HasDefaultValueSql("NOW()");

            // Indexes
            entity.HasIndex(e => e.SeasonYear);
            entity.HasIndex(e => e.CreatorId);

            // Relationships
            entity.HasOne(e => e.Creator)
                .WithMany()
                .HasForeignKey(e => e.CreatorId)
                .OnDelete(DeleteBehavior.Restrict);
        });

        // Trip
        modelBuilder.Entity<Trip>(entity =>
        {
            entity.HasKey(e => e.Id);
            entity.Property(e => e.Name).IsRequired().HasMaxLength(200);
            entity.Property(e => e.StartDate).IsRequired();
            entity.Property(e => e.EndDate).IsRequired();
            entity.Property(e => e.CampgroundName).HasMaxLength(200);
            entity.Property(e => e.CreatedAt).HasDefaultValueSql("NOW()");
            entity.Property(e => e.UpdatedAt).HasDefaultValueSql("NOW()");

            // JSONB metadata
            entity.Property(e => e.Metadata)
                .HasColumnType("jsonb");

            // Indexes
            entity.HasIndex(e => e.PlanId);
            entity.HasIndex(e => e.StartDate);
            entity.HasIndex(e => new { e.PlanId, e.StartDate });

            // Check constraint
            entity.HasCheckConstraint("CK_Trip_DateRange", "\"EndDate\" >= \"StartDate\"");

            // Relationships
            entity.HasOne(e => e.Plan)
                .WithMany(p => p.Trips)
                .HasForeignKey(e => e.PlanId)
                .OnDelete(DeleteBehavior.Cascade);
        });

        // PlanMember (composite key)
        modelBuilder.Entity<PlanMember>(entity =>
        {
            entity.HasKey(e => new { e.PlanId, e.UserId });
            entity.Property(e => e.PermissionLevel).IsRequired();
            entity.Property(e => e.JoinedAt).HasDefaultValueSql("NOW()");

            // Index for user lookups
            entity.HasIndex(e => e.UserId);

            // Relationships
            entity.HasOne(e => e.Plan)
                .WithMany(p => p.Members)
                .HasForeignKey(e => e.PlanId)
                .OnDelete(DeleteBehavior.Cascade);

            entity.HasOne(e => e.User)
                .WithMany(u => u.PlanMemberships)
                .HasForeignKey(e => e.UserId)
                .OnDelete(DeleteBehavior.Cascade);
        });

        // Reservation
        modelBuilder.Entity<Reservation>(entity =>
        {
            entity.HasKey(e => e.Id);
            entity.Property(e => e.ConfirmationCode).HasMaxLength(50);
            entity.Property(e => e.SiteNumber).HasMaxLength(20);
            entity.Property(e => e.CreatedAt).HasDefaultValueSql("NOW()");

            // Indexes
            entity.HasIndex(e => e.TripId);
            entity.HasIndex(e => e.ConfirmationCode);

            // Relationships
            entity.HasOne(e => e.Trip)
                .WithMany(t => t.Reservations)
                .HasForeignKey(e => e.TripId)
                .OnDelete(DeleteBehavior.Cascade);
        });

        // GearItem
        modelBuilder.Entity<GearItem>(entity =>
        {
            entity.HasKey(e => e.Id);
            entity.Property(e => e.Name).IsRequired().HasMaxLength(200);
            entity.Property(e => e.ClaimedByUserId).HasMaxLength(128);

            // Indexes
            entity.HasIndex(e => e.PlanId);
            entity.HasIndex(e => e.ClaimedByUserId);

            // Relationships
            entity.HasOne(e => e.Plan)
                .WithMany(p => p.GearItems)
                .HasForeignKey(e => e.PlanId)
                .OnDelete(DeleteBehavior.Cascade);
        });
    }
}
```

### EF Core Migration Example

```csharp
// Create migration
// dotnet ef migrations add AddTripNotes

public partial class AddTripNotes : Migration
{
    protected override void Up(MigrationBuilder migrationBuilder)
    {
        migrationBuilder.CreateTable(
            name: "TripNotes",
            columns: table => new
            {
                Id = table.Column<int>(type: "integer", nullable: false)
                    .Annotation("Npgsql:ValueGenerationStrategy", NpgsqlValueGenerationStrategy.IdentityByDefaultColumn),
                TripId = table.Column<int>(type: "integer", nullable: false),
                UserId = table.Column<string>(type: "text", nullable: false),
                Content = table.Column<string>(type: "character varying(2000)", maxLength: 2000, nullable: false),
                CreatedAt = table.Column<DateTime>(type: "timestamp with time zone", nullable: false, defaultValueSql: "NOW()"),
                UpdatedAt = table.Column<DateTime>(type: "timestamp with time zone", nullable: false, defaultValueSql: "NOW()")
            },
            constraints: table =>
            {
                table.PrimaryKey("PK_TripNotes", x => x.Id);
                table.ForeignKey(
                    name: "FK_TripNotes_Trips_TripId",
                    column: x => x.TripId,
                    principalTable: "Trips",
                    principalColumn: "Id",
                    onDelete: ReferentialAction.Cascade);
                table.ForeignKey(
                    name: "FK_TripNotes_Users_UserId",
                    column: x => x.UserId,
                    principalTable: "Users",
                    principalColumn: "Id",
                    onDelete: ReferentialAction.Cascade);
            });

        migrationBuilder.CreateIndex(
            name: "IX_TripNotes_TripId",
            table: "TripNotes",
            column: "TripId");

        migrationBuilder.CreateIndex(
            name: "IX_TripNotes_UserId",
            table: "TripNotes",
            column: "UserId");
    }

    protected override void Down(MigrationBuilder migrationBuilder)
    {
        migrationBuilder.DropTable(
            name: "TripNotes");
    }
}
```

---

## Best Practices Checklist

When designing or reviewing database schemas, verify:

### Schema Design
- [ ] Tables are properly normalized (avoid data duplication)
- [ ] Primary keys are defined for all tables
- [ ] Foreign keys enforce referential integrity
- [ ] Composite keys are used for junction tables
- [ ] Unique constraints prevent duplicate data
- [ ] Check constraints validate data ranges
- [ ] Default values are set where appropriate
- [ ] Required fields use NOT NULL constraint

### Indexes
- [ ] Foreign keys have indexes
- [ ] Frequently queried columns are indexed
- [ ] Composite indexes match query patterns
- [ ] Unique indexes enforce business rules
- [ ] Index selectivity is high enough to be useful
- [ ] Over-indexing is avoided (impacts write performance)
- [ ] JSONB queries use appropriate GIN indexes

### Performance
- [ ] N+1 queries are prevented with eager loading
- [ ] Pagination is used for large result sets
- [ ] AsNoTracking is used for read-only queries
- [ ] Projections select only needed columns
- [ ] Batch operations are used for bulk updates
- [ ] Connection pooling is configured
- [ ] Query timeout is reasonable

### Data Integrity
- [ ] CASCADE deletes are appropriate
- [ ] Orphaned records are prevented
- [ ] Concurrency conflicts are handled
- [ ] Transactions wrap multi-step operations
- [ ] Audit fields (CreatedAt, UpdatedAt) are maintained
- [ ] Soft deletes are implemented if needed
- [ ] Data validation occurs at multiple layers

### Migrations
- [ ] Migrations are idempotent
- [ ] Down migrations properly revert changes
- [ ] Data migrations preserve existing data
- [ ] Breaking changes are handled gracefully
- [ ] Production migrations are tested
- [ ] Migration naming is descriptive

---

## Common Database Scenarios

### Adding a New Table with Relationships

**Scenario**: Add TripNotes table for collaborative note-taking

**Implementation Steps**:

1. **Define Entity**:
```csharp
public class TripNote
{
    public int Id { get; set; }
    public int TripId { get; set; }
    public string UserId { get; set; } = string.Empty;
    public string Content { get; set; } = string.Empty;
    public DateTime CreatedAt { get; set; }
    public DateTime UpdatedAt { get; set; }
    
    // Navigation properties
    public Trip Trip { get; set; } = null!;
    public User User { get; set; } = null!;
}
```

2. **Configure in DbContext**:
```csharp
modelBuilder.Entity<TripNote>(entity =>
{
    entity.HasKey(e => e.Id);
    entity.Property(e => e.Content).IsRequired().HasMaxLength(2000);
    entity.Property(e => e.CreatedAt).HasDefaultValueSql("NOW()");
    entity.Property(e => e.UpdatedAt).HasDefaultValueSql("NOW()");

    // Indexes
    entity.HasIndex(e => e.TripId);
    entity.HasIndex(e => e.UserId);
    entity.HasIndex(e => new { e.TripId, e.CreatedAt });

    // Relationships
    entity.HasOne(e => e.Trip)
        .WithMany(t => t.Notes)
        .HasForeignKey(e => e.TripId)
        .OnDelete(DeleteBehavior.Cascade);

    entity.HasOne(e => e.User)
        .WithMany()
        .HasForeignKey(e => e.UserId)
        .OnDelete(DeleteBehavior.Restrict);
});
```

3. **Create Migration**:
```bash
dotnet ef migrations add AddTripNotes --project src/Infrastructure --startup-project src/api
dotnet ef database update --project src/Infrastructure --startup-project src/api
```

### Optimizing Slow Queries

**Scenario**: Trips query is slow when filtering by date range

**Analysis**:
```sql
-- Enable query logging in appsettings.json
"Logging": {
  "LogLevel": {
    "Microsoft.EntityFrameworkCore.Database.Command": "Information"
  }
}

-- Analyze query plan
EXPLAIN ANALYZE
SELECT * FROM "Trips"
WHERE "StartDate" >= '2026-01-01' AND "EndDate" <= '2026-12-31';
```

**Solutions**:

1. **Add Composite Index**:
```csharp
entity.HasIndex(e => new { e.StartDate, e.EndDate });
```

2. **Use Query Filtering**:
```csharp
// Instead of loading all trips then filtering
var trips = await _context.Trips
    .Where(t => t.StartDate >= startDate && t.EndDate <= endDate)
    .AsNoTracking()
    .ToListAsync();
```

3. **Use Projections**:
```csharp
// Load only needed data
var tripSummaries = await _context.Trips
    .Where(t => t.PlanId == planId)
    .Select(t => new TripSummaryDto
    {
        Id = t.Id,
        Name = t.Name,
        StartDate = t.StartDate,
        EndDate = t.EndDate
    })
    .ToListAsync();
```

### Implementing Soft Deletes

**Scenario**: Mark records as deleted instead of removing them

**Implementation**:

1. **Add IsDeleted Column**:
```csharp
public class Trip
{
    // ... existing properties
    public bool IsDeleted { get; set; }
    public DateTime? DeletedAt { get; set; }
}

// Configure
modelBuilder.Entity<Trip>(entity =>
{
    // ... existing configuration
    entity.Property(e => e.IsDeleted).HasDefaultValue(false);
    entity.HasIndex(e => e.IsDeleted);
    
    // Global query filter
    entity.HasQueryFilter(e => !e.IsDeleted);
});
```

2. **Override SaveChanges**:
```csharp
public override int SaveChanges()
{
    foreach (var entry in ChangeTracker.Entries<Trip>())
    {
        if (entry.State == EntityState.Deleted)
        {
            entry.State = EntityState.Modified;
            entry.Entity.IsDeleted = true;
            entry.Entity.DeletedAt = DateTime.UtcNow;
        }
    }
    return base.SaveChanges();
}
```

3. **Include Soft Deleted Records When Needed**:
```csharp
var allTrips = await _context.Trips
    .IgnoreQueryFilters()
    .Where(t => t.PlanId == planId)
    .ToListAsync();
```

### Working with JSONB Columns

**Scenario**: Store flexible user preferences in JSONB

**Implementation**:

1. **Define Property**:
```csharp
public class UserProfile
{
    // ... other properties
    public JsonDocument? PrivacySettings { get; set; }
}

// Configure
entity.Property(e => e.PrivacySettings)
    .HasColumnType("jsonb");

// GIN index for JSONB queries
migrationBuilder.Sql(
    "CREATE INDEX IX_UserProfiles_PrivacySettings ON \"UserProfiles\" USING GIN (\"PrivacySettings\");"
);
```

2. **Query JSONB Data**:
```csharp
// Using raw SQL for JSONB queries
var publicProfiles = await _context.UserProfiles
    .FromSqlRaw(@"
        SELECT * FROM ""UserProfiles""
        WHERE ""PrivacySettings""->>'profileVisibility' = 'public'
    ")
    .ToListAsync();
```

3. **Update JSONB Data**:
```csharp
var settings = new Dictionary<string, object>
{
    { "profileVisibility", "private" },
    { "showEmail", false },
    { "showRvInfo", true }
};

profile.PrivacySettings = JsonDocument.Parse(
    JsonSerializer.Serialize(settings)
);

await _context.SaveChangesAsync();
```

### Handling Concurrency Conflicts

**Scenario**: Multiple users editing the same trip simultaneously

**Implementation**:

1. **Add RowVersion**:
```csharp
public class Trip
{
    // ... other properties
    [Timestamp]
    public byte[] RowVersion { get; set; } = Array.Empty<byte>();
}

// Or configure in fluent API
entity.Property(e => e.RowVersion)
    .IsRowVersion();
```

2. **Handle Conflict in Controller**:
```csharp
[HttpPut("{id}")]
public async Task<IActionResult> UpdateTrip(int id, UpdateTripDto dto)
{
    var trip = await _context.Trips.FindAsync(id);
    if (trip == null)
        return NotFound();

    // Update properties
    trip.Name = dto.Name;
    trip.StartDate = dto.StartDate;
    trip.EndDate = dto.EndDate;

    try
    {
        await _context.SaveChangesAsync();
        return NoContent();
    }
    catch (DbUpdateConcurrencyException ex)
    {
        var entry = ex.Entries.Single();
        var databaseValues = await entry.GetDatabaseValuesAsync();

        if (databaseValues == null)
        {
            return NotFound(new { message = "Trip was deleted by another user" });
        }

        return Conflict(new 
        { 
            message = "Trip was modified by another user. Please refresh and try again.",
            currentValues = databaseValues.ToObject()
        });
    }
}
```

### Implementing Full-Text Search

**Scenario**: Search trips and plans by name and description

**Implementation**:

1. **Create Full-Text Index**:
```csharp
// In migration
migrationBuilder.Sql(@"
    CREATE EXTENSION IF NOT EXISTS pg_trgm;
    
    CREATE INDEX IX_Trips_Name_FullText 
    ON ""Trips"" USING GIN (to_tsvector('english', ""Name""));
    
    CREATE INDEX IX_Plans_Name_FullText 
    ON ""Plans"" USING GIN (to_tsvector('english', ""Name""));
");
```

2. **Query with Full-Text Search**:
```csharp
var searchTerm = "summer camping";

var trips = await _context.Trips
    .FromSqlRaw(@"
        SELECT * FROM ""Trips""
        WHERE to_tsvector('english', ""Name"") @@ plainto_tsquery('english', {0})
        ORDER BY ts_rank(to_tsvector('english', ""Name""), plainto_tsquery('english', {0})) DESC
    ", searchTerm)
    .ToListAsync();
```

---

## Query Optimization Patterns

### Preventing N+1 Queries

```csharp
// ❌ Bad: N+1 query problem
var plans = await _context.Plans.ToListAsync();
foreach (var plan in plans)
{
    // This executes a query for EACH plan
    var tripCount = await _context.Trips.CountAsync(t => t.PlanId == plan.Id);
}

// ✅ Good: Single query with Include
var plans = await _context.Plans
    .Include(p => p.Trips)
    .ToListAsync();

foreach (var plan in plans)
{
    var tripCount = plan.Trips.Count;
}

// ✅ Better: Projection with counts
var planSummaries = await _context.Plans
    .Select(p => new
    {
        p.Id,
        p.Name,
        TripCount = p.Trips.Count,
        MemberCount = p.Members.Count
    })
    .ToListAsync();
```

### Batch Operations

```csharp
// ❌ Bad: Individual updates
foreach (var tripId in tripIds)
{
    var trip = await _context.Trips.FindAsync(tripId);
    trip.Status = "Cancelled";
    await _context.SaveChangesAsync(); // Database call per iteration
}

// ✅ Good: Batch update
var tripsToUpdate = await _context.Trips
    .Where(t => tripIds.Contains(t.Id))
    .ToListAsync();

foreach (var trip in tripsToUpdate)
{
    trip.Status = "Cancelled";
}

await _context.SaveChangesAsync(); // Single database call
```

### Using AsNoTracking

```csharp
// ❌ Unnecessary tracking for read-only queries
var trips = await _context.Trips
    .Where(t => t.PlanId == planId)
    .ToListAsync();

// ✅ Better performance for read-only operations
var trips = await _context.Trips
    .AsNoTracking()
    .Where(t => t.PlanId == planId)
    .ToListAsync();
```

---

## PostgreSQL-Specific Features

### UUID Primary Keys

```csharp
public class User
{
    public Guid Id { get; set; } = Guid.NewGuid();
    // ... other properties
}

// Configure
entity.Property(e => e.Id)
    .HasDefaultValueSql("gen_random_uuid()");
```

### Array Columns

```csharp
public class Trip
{
    public string[] Tags { get; set; } = Array.Empty<string>();
}

// Configure
entity.Property(e => e.Tags)
    .HasColumnType("text[]");

// Query
var trips = await _context.Trips
    .Where(t => t.Tags.Contains("family-friendly"))
    .ToListAsync();
```

### Date Ranges

```csharp
// Using NpgsqlRange
public class Reservation
{
    public NpgsqlRange<DateTime> DateRange { get; set; }
}

// Query overlapping ranges
var overlapping = await _context.Reservations
    .Where(r => r.DateRange.Overlaps(requestedRange))
    .ToListAsync();
```

---

## Connection Configuration

### appsettings.json

```json
{
  "ConnectionStrings": {
    "DefaultConnection": "Host=db;Database=happy_camper_db;Username=camper_admin;Password=dev_password_123;Pooling=true;MinPoolSize=1;MaxPoolSize=20;CommandTimeout=30"
  },
  "Logging": {
    "LogLevel": {
      "Default": "Information",
      "Microsoft.EntityFrameworkCore.Database.Command": "Warning",
      "Microsoft.EntityFrameworkCore.Infrastructure": "Warning"
    }
  }
}
```

### Program.cs Configuration

```csharp
builder.Services.AddDbContext<ApplicationDbContext>(options =>
{
    options.UseNpgsql(
        builder.Configuration.GetConnectionString("DefaultConnection"),
        npgsqlOptions =>
        {
            npgsqlOptions.EnableRetryOnFailure(
                maxRetryCount: 3,
                maxRetryDelay: TimeSpan.FromSeconds(5),
                errorCodesToAdd: null
            );
            npgsqlOptions.CommandTimeout(30);
        }
    );

    if (builder.Environment.IsDevelopment())
    {
        options.EnableSensitiveDataLogging();
        options.EnableDetailedErrors();
    }
});
```

---

## Integration with Project Patterns

### Current User Pattern
Filter queries by user access:
```csharp
var userId = User.FindFirstValue(ClaimTypes.NameIdentifier);

var plans = await _context.Plans
    .Include(p => p.Members)
    .Where(p => p.Members.Any(m => m.UserId == userId))
    .ToListAsync();
```

### JSONB Metadata Pattern
Flexible schema for dynamic data:
```csharp
public JsonDocument? Metadata { get; set; }

entity.Property(e => e.Metadata).HasColumnType("jsonb");
```

### Composite Keys for Junction Tables
Many-to-many relationships:
```csharp
entity.HasKey(e => new { e.PlanId, e.UserId });
```

---

## When to Use the Database Agent

Use this agent when:

- **Designing database schemas** for new features
- **Creating EF Core migrations** and managing schema changes
- **Optimizing slow queries** and improving performance
- **Adding indexes** for better query performance
- **Implementing data integrity** constraints and validations
- **Working with PostgreSQL-specific features** (JSONB, arrays, etc.)
- **Troubleshooting database errors** and connection issues
- **Planning data migrations** for existing data
- **Reviewing database design** for best practices
- **Setting up audit trails** and temporal data

---

## Integration with Baseline Behaviors

This agent follows all baseline behaviors from [../LLM-BaselineBehaviors.md](../LLM-BaselineBehaviors.md):

- **Action-oriented**: Implements migrations and schema changes, doesn't just suggest them
- **Research-driven**: Examines existing entities and DbContext to understand patterns
- **Complete solutions**: Provides entities, configurations, migrations, and query examples
- **Clear communication**: Explains design decisions and performance trade-offs
- **Error handling**: Ensures data integrity and proper constraint handling
- **Task management**: Uses todo lists for complex schema changes

**Database-specific additions**:
- **Performance-first**: Always considers query performance and indexing
- **Integrity-focused**: Ensures referential integrity and data validation
- **PostgreSQL-aware**: Leverages PostgreSQL-specific features when beneficial
- **Migration-safe**: Ensures migrations are reversible and data-preserving
- **EF Core best practices**: Follows Entity Framework Core conventions and patterns
