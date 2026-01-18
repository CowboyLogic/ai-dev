---
name: dotnet-api-development
description: Comprehensive guide for building .NET APIs with ASP.NET Core and Entity Framework, including best practices for data access, authentication, and testing.
license: MIT
---

# .NET API Development with Entity Framework

This skill provides expert guidance for building robust, scalable APIs using ASP.NET Core and Entity Framework Core. It covers the full spectrum of API development from database design to deployment, with a focus on Entity Framework for data access.

## When to Use This Skill

Use this skill when:
- Building new ASP.NET Core Web APIs
- Implementing data access layers with Entity Framework
- Setting up database contexts and migrations
- Creating repository patterns and unit of work
- Implementing authentication and authorization
- Writing comprehensive API tests
- Following .NET API development best practices

## Prerequisites

- .NET 6+ SDK
- SQL Server, PostgreSQL, or another EF Core supported database
- Basic understanding of C# and async programming
- Familiarity with REST API concepts

## Core Components

### 1. Project Setup and Configuration

#### ASP.NET Core Web API Project Structure

```
MyApi/
├── Controllers/
├── Models/
├── Data/
│   ├── ApplicationDbContext.cs
│   ├── Repositories/
│   └── Migrations/
├── Services/
├── DTOs/
├── Mappings/
├── Tests/
├── appsettings.json
├── Program.cs
└── MyApi.csproj
```

#### Essential NuGet Packages

```xml
<PackageReference Include="Microsoft.EntityFrameworkCore" Version="8.0.0" />
<PackageReference Include="Microsoft.EntityFrameworkCore.SqlServer" Version="8.0.0" />
<PackageReference Include="Microsoft.EntityFrameworkCore.Design" Version="8.0.0" />
<PackageReference Include="Microsoft.AspNetCore.Authentication.JwtBearer" Version="8.0.0" />
<PackageReference Include="AutoMapper" Version="12.0.0" />
<PackageReference Include="FluentValidation.AspNetCore" Version="11.0.0" />
<PackageReference Include="Swashbuckle.AspNetCore" Version="6.5.0" />
```

### 2. Entity Framework Core Implementation

#### Database Context Setup

```csharp
using Microsoft.EntityFrameworkCore;

namespace MyApi.Data
{
    public class ApplicationDbContext : DbContext
    {
        public ApplicationDbContext(DbContextOptions<ApplicationDbContext> options)
            : base(options)
        {
        }

        public DbSet<User> Users { get; set; }
        public DbSet<Product> Products { get; set; }
        public DbSet<Order> Orders { get; set; }

        protected override void OnModelCreating(ModelBuilder modelBuilder)
        {
            base.OnModelCreating(modelBuilder);

            // Configure relationships
            modelBuilder.Entity<Order>()
                .HasOne(o => o.User)
                .WithMany(u => u.Orders)
                .HasForeignKey(o => o.UserId);

            modelBuilder.Entity<Order>()
                .HasMany(o => o.OrderItems)
                .WithOne(oi => oi.Order)
                .HasForeignKey(oi => oi.OrderId);

            // Seed data
            modelBuilder.Entity<User>().HasData(
                new User { Id = 1, Email = "admin@example.com", Role = "Admin" }
            );
        }
    }
}
```

#### Entity Models

```csharp
using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;

namespace MyApi.Models
{
    public class User
    {
        [Key]
        public int Id { get; set; }

        [Required]
        [EmailAddress]
        [MaxLength(256)]
        public string Email { get; set; }

        [Required]
        [MaxLength(50)]
        public string Role { get; set; }

        // Navigation properties
        public ICollection<Order> Orders { get; set; }
    }

    public class Product
    {
        [Key]
        public int Id { get; set; }

        [Required]
        [MaxLength(200)]
        public string Name { get; set; }

        [Column(TypeName = "decimal(18,2)")]
        public decimal Price { get; set; }

        [MaxLength(1000)]
        public string Description { get; set; }

        public int StockQuantity { get; set; }
    }

    public class Order
    {
        [Key]
        public int Id { get; set; }

        [Required]
        public int UserId { get; set; }

        [Required]
        public DateTime OrderDate { get; set; }

        [Column(TypeName = "decimal(18,2)")]
        public decimal TotalAmount { get; set; }

        public OrderStatus Status { get; set; }

        // Navigation properties
        public User User { get; set; }
        public ICollection<OrderItem> OrderItems { get; set; }
    }

    public enum OrderStatus
    {
        Pending,
        Processing,
        Shipped,
        Delivered,
        Cancelled
    }
}
```

#### Repository Pattern Implementation

```csharp
using Microsoft.EntityFrameworkCore;
using System.Linq.Expressions;

namespace MyApi.Data.Repositories
{
    public interface IRepository<T> where T : class
    {
        Task<T> GetByIdAsync(int id);
        Task<IEnumerable<T>> GetAllAsync();
        Task<IEnumerable<T>> FindAsync(Expression<Func<T, bool>> predicate);
        Task AddAsync(T entity);
        Task UpdateAsync(T entity);
        Task DeleteAsync(int id);
        Task<bool> ExistsAsync(int id);
    }

    public class Repository<T> : IRepository<T> where T : class
    {
        protected readonly ApplicationDbContext _context;
        protected readonly DbSet<T> _dbSet;

        public Repository(ApplicationDbContext context)
        {
            _context = context;
            _dbSet = context.Set<T>();
        }

        public async Task<T> GetByIdAsync(int id)
        {
            return await _dbSet.FindAsync(id);
        }

        public async Task<IEnumerable<T>> GetAllAsync()
        {
            return await _dbSet.ToListAsync();
        }

        public async Task<IEnumerable<T>> FindAsync(Expression<Func<T, bool>> predicate)
        {
            return await _dbSet.Where(predicate).ToListAsync();
        }

        public async Task AddAsync(T entity)
        {
            await _dbSet.AddAsync(entity);
            await _context.SaveChangesAsync();
        }

        public async Task UpdateAsync(T entity)
        {
            _dbSet.Update(entity);
            await _context.SaveChangesAsync();
        }

        public async Task DeleteAsync(int id)
        {
            var entity = await GetByIdAsync(id);
            if (entity != null)
            {
                _dbSet.Remove(entity);
                await _context.SaveChangesAsync();
            }
        }

        public async Task<bool> ExistsAsync(int id)
        {
            return await _dbSet.FindAsync(id) != null;
        }
    }
}
```

#### Unit of Work Pattern

```csharp
namespace MyApi.Data
{
    public interface IUnitOfWork : IDisposable
    {
        IRepository<User> Users { get; }
        IRepository<Product> Products { get; }
        IRepository<Order> Orders { get; }
        Task<int> SaveChangesAsync();
        Task BeginTransactionAsync();
        Task CommitTransactionAsync();
        Task RollbackTransactionAsync();
    }

    public class UnitOfWork : IUnitOfWork
    {
        private readonly ApplicationDbContext _context;
        private bool _disposed = false;

        public UnitOfWork(ApplicationDbContext context)
        {
            _context = context;
        }

        private IRepository<User> _users;
        private IRepository<Product> _products;
        private IRepository<Order> _orders;

        public IRepository<User> Users => _users ??= new Repository<User>(_context);
        public IRepository<Product> Products => _products ??= new Repository<Product>(_context);
        public IRepository<Order> Orders => _orders ??= new Repository<Order>(_context);

        public async Task<int> SaveChangesAsync()
        {
            return await _context.SaveChangesAsync();
        }

        public async Task BeginTransactionAsync()
        {
            await _context.Database.BeginTransactionAsync();
        }

        public async Task CommitTransactionAsync()
        {
            await _context.Database.CommitTransactionAsync();
        }

        public async Task RollbackTransactionAsync()
        {
            await _context.Database.RollbackTransactionAsync();
        }

        protected virtual void Dispose(bool disposing)
        {
            if (!_disposed)
            {
                if (disposing)
                {
                    _context.Dispose();
                }
                _disposed = true;
            }
        }

        public void Dispose()
        {
            Dispose(true);
            GC.SuppressFinalize(this);
        }
    }
}
```

### 3. API Controller Implementation

#### Base Controller

```csharp
using Microsoft.AspNetCore.Mvc;

namespace MyApi.Controllers
{
    [ApiController]
    [Route("api/[controller]")]
    public class BaseController : ControllerBase
    {
        protected readonly IUnitOfWork _unitOfWork;
        protected readonly ILogger _logger;

        public BaseController(IUnitOfWork unitOfWork, ILogger logger)
        {
            _unitOfWork = unitOfWork;
            _logger = logger;
        }

        protected IActionResult HandleException(Exception ex, string message = "An error occurred")
        {
            _logger.LogError(ex, message);
            return StatusCode(500, new { message, error = ex.Message });
        }
    }
}
```

#### Products Controller

```csharp
using Microsoft.AspNetCore.Authorization;
using AutoMapper;
using FluentValidation;

namespace MyApi.Controllers
{
    [Authorize]
    [ApiVersion("1.0")]
    public class ProductsController : BaseController
    {
        private readonly IMapper _mapper;
        private readonly IValidator<CreateProductDto> _createValidator;
        private readonly IValidator<UpdateProductDto> _updateValidator;

        public ProductsController(
            IUnitOfWork unitOfWork,
            ILogger<ProductsController> logger,
            IMapper mapper,
            IValidator<CreateProductDto> createValidator,
            IValidator<UpdateProductDto> updateValidator)
            : base(unitOfWork, logger)
        {
            _mapper = mapper;
            _createValidator = createValidator;
            _updateValidator = updateValidator;
        }

        [HttpGet]
        [AllowAnonymous]
        public async Task<IActionResult> GetProducts([FromQuery] ProductQueryParameters parameters)
        {
            try
            {
                var products = await _unitOfWork.Products.FindAsync(p =>
                    (string.IsNullOrEmpty(parameters.Search) ||
                     p.Name.Contains(parameters.Search) ||
                     p.Description.Contains(parameters.Search)) &&
                    (!parameters.MinPrice.HasValue || p.Price >= parameters.MinPrice) &&
                    (!parameters.MaxPrice.HasValue || p.Price <= parameters.MaxPrice));

                var productDtos = _mapper.Map<IEnumerable<ProductDto>>(products);
                return Ok(productDtos);
            }
            catch (Exception ex)
            {
                return HandleException(ex, "Error retrieving products");
            }
        }

        [HttpGet("{id}")]
        [AllowAnonymous]
        public async Task<IActionResult> GetProduct(int id)
        {
            try
            {
                var product = await _unitOfWork.Products.GetByIdAsync(id);
                if (product == null)
                    return NotFound(new { message = "Product not found" });

                var productDto = _mapper.Map<ProductDto>(product);
                return Ok(productDto);
            }
            catch (Exception ex)
            {
                return HandleException(ex, "Error retrieving product");
            }
        }

        [HttpPost]
        [Authorize(Roles = "Admin")]
        public async Task<IActionResult> CreateProduct([FromBody] CreateProductDto createDto)
        {
            try
            {
                var validationResult = await _createValidator.ValidateAsync(createDto);
                if (!validationResult.IsValid)
                    return BadRequest(validationResult.Errors);

                var product = _mapper.Map<Product>(createDto);
                await _unitOfWork.Products.AddAsync(product);

                var productDto = _mapper.Map<ProductDto>(product);
                return CreatedAtAction(nameof(GetProduct), new { id = product.Id }, productDto);
            }
            catch (Exception ex)
            {
                return HandleException(ex, "Error creating product");
            }
        }

        [HttpPut("{id}")]
        [Authorize(Roles = "Admin")]
        public async Task<IActionResult> UpdateProduct(int id, [FromBody] UpdateProductDto updateDto)
        {
            try
            {
                var validationResult = await _updateValidator.ValidateAsync(updateDto);
                if (!validationResult.IsValid)
                    return BadRequest(validationResult.Errors);

                var existingProduct = await _unitOfWork.Products.GetByIdAsync(id);
                if (existingProduct == null)
                    return NotFound(new { message = "Product not found" });

                _mapper.Map(updateDto, existingProduct);
                await _unitOfWork.Products.UpdateAsync(existingProduct);

                return NoContent();
            }
            catch (Exception ex)
            {
                return HandleException(ex, "Error updating product");
            }
        }

        [HttpDelete("{id}")]
        [Authorize(Roles = "Admin")]
        public async Task<IActionResult> DeleteProduct(int id)
        {
            try
            {
                var exists = await _unitOfWork.Products.ExistsAsync(id);
                if (!exists)
                    return NotFound(new { message = "Product not found" });

                await _unitOfWork.Products.DeleteAsync(id);
                return NoContent();
            }
            catch (Exception ex)
            {
                return HandleException(ex, "Error deleting product");
            }
        }
    }
}
```

### 4. DTOs and Validation

#### Data Transfer Objects

```csharp
namespace MyApi.DTOs
{
    public class ProductDto
    {
        public int Id { get; set; }
        public string Name { get; set; }
        public decimal Price { get; set; }
        public string Description { get; set; }
        public int StockQuantity { get; set; }
    }

    public class CreateProductDto
    {
        [Required]
        [MaxLength(200)]
        public string Name { get; set; }

        [Required]
        [Range(0.01, 10000)]
        public decimal Price { get; set; }

        [MaxLength(1000)]
        public string Description { get; set; }

        [Required]
        [Range(0, int.MaxValue)]
        public int StockQuantity { get; set; }
    }

    public class UpdateProductDto
    {
        [Required]
        [MaxLength(200)]
        public string Name { get; set; }

        [Required]
        [Range(0.01, 10000)]
        public decimal Price { get; set; }

        [MaxLength(1000)]
        public string Description { get; set; }

        [Required]
        [Range(0, int.MaxValue)]
        public int StockQuantity { get; set; }
    }

    public class ProductQueryParameters
    {
        public string Search { get; set; }
        public decimal? MinPrice { get; set; }
        public decimal? MaxPrice { get; set; }
        public int PageNumber { get; set; } = 1;
        public int PageSize { get; set; } = 10;
    }
}
```

#### Fluent Validation

```csharp
using FluentValidation;

namespace MyApi.Validators
{
    public class CreateProductDtoValidator : AbstractValidator<CreateProductDto>
    {
        public CreateProductDtoValidator()
        {
            RuleFor(x => x.Name)
                .NotEmpty().WithMessage("Product name is required")
                .MaximumLength(200).WithMessage("Product name cannot exceed 200 characters");

            RuleFor(x => x.Price)
                .GreaterThan(0).WithMessage("Price must be greater than 0")
                .LessThanOrEqualTo(10000).WithMessage("Price cannot exceed 10000");

            RuleFor(x => x.Description)
                .MaximumLength(1000).WithMessage("Description cannot exceed 1000 characters");

            RuleFor(x => x.StockQuantity)
                .GreaterThanOrEqualTo(0).WithMessage("Stock quantity cannot be negative");
        }
    }

    public class UpdateProductDtoValidator : AbstractValidator<UpdateProductDto>
    {
        public UpdateProductDtoValidator()
        {
            RuleFor(x => x.Name)
                .NotEmpty().WithMessage("Product name is required")
                .MaximumLength(200).WithMessage("Product name cannot exceed 200 characters");

            RuleFor(x => x.Price)
                .GreaterThan(0).WithMessage("Price must be greater than 0")
                .LessThanOrEqualTo(10000).WithMessage("Price cannot exceed 10000");

            RuleFor(x => x.Description)
                .MaximumLength(1000).WithMessage("Description cannot exceed 1000 characters");

            RuleFor(x => x.StockQuantity)
                .GreaterThanOrEqualTo(0).WithMessage("Stock quantity cannot be negative");
        }
    }
}
```

### 5. AutoMapper Configuration

```csharp
using AutoMapper;

namespace MyApi.Mappings
{
    public class MappingProfile : Profile
    {
        public MappingProfile()
        {
            CreateMap<Product, ProductDto>();
            CreateMap<CreateProductDto, Product>();
            CreateMap<UpdateProductDto, Product>();
        }
    }
}
```

### 6. Program.cs Configuration

```csharp
using Microsoft.EntityFrameworkCore;
using Microsoft.AspNetCore.Authentication.JwtBearer;
using Microsoft.IdentityModel.Tokens;
using System.Text;
using FluentValidation.AspNetCore;
using MyApi.Data;
using MyApi.Services;

var builder = WebApplication.CreateBuilder(args);

// Add services to the container.
builder.Services.AddControllers()
    .AddFluentValidation(fv => fv.RegisterValidatorsFromAssemblyContaining<CreateProductDtoValidator>());

builder.Services.AddEndpointsApiExplorer();
builder.Services.AddSwaggerGen();

// Database context
builder.Services.AddDbContext<ApplicationDbContext>(options =>
    options.UseSqlServer(builder.Configuration.GetConnectionString("DefaultConnection")));

// Unit of Work and Repositories
builder.Services.AddScoped<IUnitOfWork, UnitOfWork>();

// AutoMapper
builder.Services.AddAutoMapper(typeof(MappingProfile));

// JWT Authentication
builder.Services.AddAuthentication(JwtBearerDefaults.AuthenticationScheme)
    .AddJwtBearer(options =>
    {
        options.TokenValidationParameters = new TokenValidationParameters
        {
            ValidateIssuer = true,
            ValidateAudience = true,
            ValidateLifetime = true,
            ValidateIssuerSigningKey = true,
            ValidIssuer = builder.Configuration["Jwt:Issuer"],
            ValidAudience = builder.Configuration["Jwt:Audience"],
            IssuerSigningKey = new SymmetricSecurityKey(Encoding.UTF8.GetBytes(builder.Configuration["Jwt:Key"]))
        };
    });

// API Versioning
builder.Services.AddApiVersioning(options =>
{
    options.AssumeDefaultVersionWhenUnspecified = true;
    options.DefaultApiVersion = new ApiVersion(1, 0);
    options.ReportApiVersions = true;
});

// CORS
builder.Services.AddCors(options =>
{
    options.AddPolicy("AllowAll", builder =>
    {
        builder.AllowAnyOrigin()
               .AllowAnyMethod()
               .AllowAnyHeader();
    });
});

var app = builder.Build();

// Configure the HTTP request pipeline.
if (app.Environment.IsDevelopment())
{
    app.UseSwagger();
    app.UseSwaggerUI();
}

app.UseHttpsRedirection();
app.UseCors("AllowAll");
app.UseAuthentication();
app.UseAuthorization();

app.MapControllers();

// Database migration
using (var scope = app.Services.CreateScope())
{
    var dbContext = scope.ServiceProvider.GetRequiredService<ApplicationDbContext>();
    await dbContext.Database.MigrateAsync();
}

app.Run();
```

### 7. Database Migrations

```bash
# Create migration
dotnet ef migrations add InitialCreate

# Update database
dotnet ef database update

# Generate SQL script
dotnet ef migrations script
```

### 8. Testing

#### Unit Tests

```csharp
using Xunit;
using Moq;
using AutoMapper;
using MyApi.Controllers;
using MyApi.Data;
using MyApi.DTOs;
using Microsoft.AspNetCore.Mvc;

namespace MyApi.Tests.Controllers
{
    public class ProductsControllerTests
    {
        private readonly Mock<IUnitOfWork> _mockUnitOfWork;
        private readonly Mock<ILogger<ProductsController>> _mockLogger;
        private readonly IMapper _mapper;
        private readonly ProductsController _controller;

        public ProductsControllerTests()
        {
            _mockUnitOfWork = new Mock<IUnitOfWork>();
            _mockLogger = new Mock<ILogger<ProductsController>>();

            var config = new MapperConfiguration(cfg => cfg.AddProfile<MappingProfile>());
            _mapper = config.CreateMapper();

            _controller = new ProductsController(
                _mockUnitOfWork.Object,
                _mockLogger.Object,
                _mapper,
                new CreateProductDtoValidator(),
                new UpdateProductDtoValidator());
        }

        [Fact]
        public async Task GetProduct_ReturnsNotFound_WhenProductDoesNotExist()
        {
            // Arrange
            _mockUnitOfWork.Setup(u => u.Products.GetByIdAsync(1)).ReturnsAsync((Product)null);

            // Act
            var result = await _controller.GetProduct(1);

            // Assert
            Assert.IsType<NotFoundObjectResult>(result);
        }

        [Fact]
        public async Task CreateProduct_ReturnsCreated_WhenValidData()
        {
            // Arrange
            var createDto = new CreateProductDto
            {
                Name = "Test Product",
                Price = 10.99m,
                StockQuantity = 100
            };

            var product = _mapper.Map<Product>(createDto);
            product.Id = 1;

            _mockUnitOfWork.Setup(u => u.Products.AddAsync(It.IsAny<Product>()))
                .Callback<Product>(p => p.Id = 1)
                .Returns(Task.CompletedTask);

            // Act
            var result = await _controller.CreateProduct(createDto);

            // Assert
            var createdResult = Assert.IsType<CreatedAtActionResult>(result);
            Assert.Equal("GetProduct", createdResult.ActionName);
        }
    }
}
```

#### Integration Tests

```csharp
using Microsoft.AspNetCore.Mvc.Testing;
using System.Net.Http.Json;
using Xunit;

namespace MyApi.IntegrationTests
{
    public class ProductsApiTests : IClassFixture<WebApplicationFactory<Program>>
    {
        private readonly WebApplicationFactory<Program> _factory;
        private readonly HttpClient _client;

        public ProductsApiTests(WebApplicationFactory<Program> factory)
        {
            _factory = factory;
            _client = _factory.CreateClient();
        }

        [Fact]
        public async Task GetProducts_ReturnsSuccessStatusCode()
        {
            // Act
            var response = await _client.GetAsync("/api/products");

            // Assert
            response.EnsureSuccessStatusCode();
        }

        [Fact]
        public async Task CreateProduct_ReturnsCreatedStatusCode()
        {
            // Arrange
            var newProduct = new
            {
                Name = "Integration Test Product",
                Price = 19.99m,
                StockQuantity = 50
            };

            // Act
            var response = await _client.PostAsJsonAsync("/api/products", newProduct);

            // Assert
            Assert.Equal(System.Net.HttpStatusCode.Created, response.StatusCode);
        }
    }
}
```

## Best Practices

### Entity Framework Optimization

1. **Use AsNoTracking for read-only queries**
```csharp
var products = await _context.Products.AsNoTracking().ToListAsync();
```

2. **Implement eager loading for related data**
```csharp
var orders = await _context.Orders
    .Include(o => o.User)
    .Include(o => o.OrderItems)
    .ThenInclude(oi => oi.Product)
    .ToListAsync();
```

3. **Use pagination for large datasets**
```csharp
var products = await _context.Products
    .Skip((pageNumber - 1) * pageSize)
    .Take(pageSize)
    .ToListAsync();
```

4. **Implement proper indexing**
```csharp
protected override void OnModelCreating(ModelBuilder modelBuilder)
{
    modelBuilder.Entity<Product>()
        .HasIndex(p => p.Name);
}
```

### API Design Principles

1. **Use consistent naming conventions**
2. **Implement proper HTTP status codes**
3. **Provide meaningful error messages**
4. **Version your APIs**
5. **Document with OpenAPI/Swagger**

### Security Considerations

1. **Validate all inputs**
2. **Use parameterized queries**
3. **Implement proper authentication and authorization**
4. **Handle sensitive data appropriately**
5. **Log security events**

## Common Patterns and Solutions

### Handling Concurrency

```csharp
[HttpPut("{id}")]
public async Task<IActionResult> UpdateProduct(int id, [FromBody] UpdateProductDto updateDto)
{
    try
    {
        var existingProduct = await _unitOfWork.Products.GetByIdAsync(id);
        if (existingProduct == null)
            return NotFound();

        // Check for concurrency conflicts
        if (existingProduct.RowVersion != updateDto.RowVersion)
            return Conflict("Product has been modified by another user");

        _mapper.Map(updateDto, existingProduct);
        await _unitOfWork.Products.UpdateAsync(existingProduct);

        return NoContent();
    }
    catch (DbUpdateConcurrencyException)
    {
        return Conflict("Concurrency conflict occurred");
    }
}
```

### Implementing Soft Deletes

```csharp
public class BaseEntity
{
    public bool IsDeleted { get; set; }
    public DateTime? DeletedAt { get; set; }
}

public class Repository<T> : IRepository<T> where T : BaseEntity
{
    public async Task<IEnumerable<T>> GetAllAsync()
    {
        return await _dbSet.Where(e => !e.IsDeleted).ToListAsync();
    }
}
```

### Global Exception Handling

```csharp
public class GlobalExceptionHandler : IMiddleware
{
    private readonly ILogger<GlobalExceptionHandler> _logger;

    public GlobalExceptionHandler(ILogger<GlobalExceptionHandler> logger)
    {
        _logger = logger;
    }

    public async Task InvokeAsync(HttpContext context, RequestDelegate next)
    {
        try
        {
            await next(context);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "An unhandled exception occurred");

            context.Response.StatusCode = 500;
            context.Response.ContentType = "application/json";

            var errorResponse = new
            {
                message = "An internal server error occurred",
                errorId = Guid.NewGuid().ToString()
            };

            await context.Response.WriteAsJsonAsync(errorResponse);
        }
    }
}
```

This comprehensive skill covers all aspects of building robust .NET APIs with Entity Framework, from database design to deployment and testing.