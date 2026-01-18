# PostgreSQL Database Skill

This skill provides comprehensive expertise in PostgreSQL database development, administration, and optimization for AI agents working with relational databases.

## Overview

The PostgreSQL Database skill enables AI agents to:

- Design and implement robust database schemas
- Write efficient SQL queries and stored procedures
- Optimize database performance and indexing
- Implement proper security measures
- Handle database migrations and backups
- Integrate PostgreSQL with various programming languages
- Monitor and troubleshoot database issues

## Key Capabilities

### Database Design & Architecture
- Schema design and normalization
- Data modeling and relationships
- Indexing strategies
- Partitioning and sharding
- JSON/JSONB document storage

### SQL Development
- Complex queries and joins
- Stored procedures and functions
- Triggers and constraints
- Views and materialized views
- Full-text search implementation

### Performance Optimization
- Query optimization and EXPLAIN analysis
- Index tuning and maintenance
- Connection pooling
- Caching strategies
- Monitoring and profiling

### Security & Administration
- User management and permissions
- SSL/TLS configuration
- Backup and recovery strategies
- Replication setup
- Audit logging

### Integration & Development
- Python SQLAlchemy models
- Node.js database connections
- Migration management
- API integration patterns
- Testing strategies

## File Structure

```
postgresql-database/
├── SKILL.md              # Main skill definition and documentation
├── README.md             # This overview file
├── schema-template.sql   # Database schema templates
├── migration-template.sql # Migration script templates
├── query-examples.sql    # SQL query examples
├── monitoring-queries.sql # Database monitoring queries
├── backup-script.sh      # Backup automation script
├── connection-examples.js # Node.js connection examples
└── model-examples.py     # Python SQLAlchemy models
```

## Usage Examples

### Creating a New Database Schema

```sql
-- Create a users table with proper constraints
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(50) UNIQUE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Add indexes for performance
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_created_at ON users(created_at);
```

### Python Integration with SQLAlchemy

```python
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    email = Column(String(255), unique=True)
    username = Column(String(50), unique=True)

# Create engine and tables
engine = create_engine('postgresql://user:pass@localhost/dbname')
Base.metadata.create_all(engine)
```

### Node.js Connection

```javascript
const { Pool } = require('pg');

const pool = new Pool({
    user: 'username',
    host: 'localhost',
    database: 'database_name',
    password: 'password',
    port: 5432,
});

pool.query('SELECT NOW()', (err, res) => {
    console.log(err, res);
    pool.end();
});
```

## Best Practices

### Schema Design
- Use appropriate data types
- Implement proper constraints
- Design for scalability
- Document schema changes

### Query Optimization
- Use EXPLAIN ANALYZE for query analysis
- Create appropriate indexes
- Avoid SELECT * in production
- Use prepared statements

### Security
- Use parameterized queries
- Implement proper authentication
- Encrypt sensitive data
- Regular security audits

### Performance
- Monitor slow queries
- Implement connection pooling
- Use appropriate caching
- Regular maintenance tasks

## Integration with Other Skills

This skill complements other development skills:

- **React/NodeJS Web Apps**: Full-stack application development with PostgreSQL backend
- **.NET API Development**: ASP.NET Core APIs with PostgreSQL data access
- **Python Development**: Django or Flask applications with PostgreSQL

## Learning Resources

- [PostgreSQL Official Documentation](https://www.postgresql.org/docs/)
- [SQLAlchemy Documentation](https://sqlalchemy.org/)
- [pgAdmin Documentation](https://www.pgadmin.org/docs/)
- [PostgreSQL Performance Tuning](https://www.postgresql.org/docs/current/performance-tips.html)

## Contributing

To contribute to this skill:

1. Follow the Agent Skills standard
2. Add comprehensive examples
3. Include performance considerations
4. Test with real PostgreSQL instances
5. Update documentation accordingly

## Validation

This skill has been validated using the skill-creator validation script and follows all Agent Skills standards.