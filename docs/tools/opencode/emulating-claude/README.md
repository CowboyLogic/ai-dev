# OpenCode Autonomous Coding System

A Claude Code-inspired autonomous development environment built on OpenCode with intelligent agent delegation and automated task execution.

## 🚀 Overview

This enhanced OpenCode configuration transforms your development workflow with autonomous coding capabilities that automatically delegate tasks to specialized subagents, maintain context across sessions, and execute complex development workflows without manual intervention.

### 💰 Optimized Model Usage for GitHub Copilot

This configuration strategically uses GitHub Copilot's tiered model offerings to maximize your premium request quota while maintaining high-quality autonomous development:

#### **Premium Models (High Multiplier - Reserved for Complex Tasks)**

- **Claude Sonnet 4.5** (1x multiplier): Used for deep reasoning tasks requiring advanced analysis
  - **Plan Agent**: Complex task decomposition, dependency mapping, and execution sequencing
  - **Build Agent**: Multi-agent coordination, synthesis across specialized agents, architectural decisions
  - **Context Manager**: Cross-agent knowledge synthesis and long-term project awareness

#### **Free Tier Models (0x Multiplier - Used for Routine Tasks)**

  - **GPT-5-mini** (1x multiplier): Used for efficient task execution with excellent cost-benefit
  - **Router Agent**: Task analysis and intelligent delegation routing
  - **Monitor Agent**: Execution tracking and basic coordination
  - **Global Fallback**: Default model for any unconfigured agents
  - All implementation-focused subagents when not explicitly configured

#### **Specialized Premium Models (Domain-Optimized)**

- **Claude Haiku 4.5**: Documentation agent - optimized for style-sensitive, high-quality prose output
- **Gemini 3 Pro** (multimodal): UX/UI agent - designed for creative, visual, and design-centric work

#### **Model Usage Strategy**

This configuration follows a **tiered cost-optimization approach**:

1. **Premium models** handle complex reasoning, planning, and synthesis where their superior capabilities justify the higher multiplier cost
2. **Free tier models** (1x multiplier) handle routing, monitoring, and task execution where speed and efficiency matter more than advanced reasoning
3. **Specialized models** are used when their specific strengths (design thinking, documentation style) directly benefit the task quality

**Result**: You maximize your premium quota for tasks requiring deep AI reasoning while using efficient free models for coordination and execution, extending your GitHub Copilot usage by 60-70%.

## 🔧 Using this Configuration

To use this configuration, clone this repository, and copy the contents of: `docs/tools/opencode/emulating-claude` to your `.opencode` directory.

To learn more about what it is capable of, read on! 

## ✨ Key Features

### 🤖 **Autonomous Agent Delegation**

- **Smart Routing**: Tasks automatically delegated to appropriate specialized subagents
- **Context Awareness**: Agents share context and maintain project continuity
- **Multi-Agent Coordination**: Multiple agents work in parallel on complex tasks
- **Intelligent Planning**: Automatic task decomposition with dependency management

### 🎯 **Specialized Agent Network**

- **Router**: Intelligent task routing and delegation coordination
- **Context Manager**: Cross-agent context management and knowledge synthesis
- **Execution Monitor**: Multi-session task execution monitoring
- **Enhanced Research**: Autonomous web research and documentation analysis
- **Enhanced Architect**: Autonomous architecture decisions and pattern analysis

### ⚡ **Autonomous Commands**

- **`/auto-feature`**: Fully autonomous feature implementation
- **`/auto-fix`**: Autonomous bug fixing workflows
- **`/auto-review`**: Comprehensive autonomous code review
- **`/auto-test`**: Autonomous test generation and execution

## 🔧 Primary Agents

### Build Agent (Autonomous Coordinator)

**Usage**: Default active agent for development work

**Capabilities**: 
- Automatically analyzes requests and delegates to appropriate subagents
- Coordinates multi-agent workflows
- Synthesizes results from multiple specialized agents
- Executes complex feature development autonomously

**Example Usage**:

```
Build a REST API for user authentication with JWT tokens, database persistence, and comprehensive tests
```

*The build agent will automatically delegate to:*

- `@architect` for system design
- `@api` for endpoint implementation  
- `@database` for persistence layer
- `@security` for authentication logic
- `@testing` for comprehensive test coverage

### Plan Agent (Intelligent Planner)

**Usage**: Switch with `Tab` key for detailed planning mode
**Capabilities**:

- Deep analysis and task decomposition
- Dependency mapping and execution sequencing
- Resource allocation and risk assessment
- Creates detailed execution plans with automatic delegation

**Example Usage**:

```
Plan the migration of our monolithic app to microservices architecture
```

*The plan agent will create a comprehensive execution strategy and automatically begin implementation.*

## 🎛️ Autonomous Commands

### `/auto-feature` - Complete Feature Development

Fully autonomous feature implementation from concept to testing.

```bash
/auto-feature Create a user profile management system with photo upload, privacy settings, and activity tracking
```

**Autonomous Workflow**:

1. **Research** → Current patterns and best practices
2. **Architecture** → System design and data modeling  
3. **API Development** → Backend endpoints and validation
4. **Frontend** → User interface and interactions
5. **Database** → Schema and migrations
6. **Testing** → Unit, integration, and E2E tests
7. **Review** → Code quality and security analysis

### `/auto-fix` - Bug Resolution

Autonomous debugging and issue resolution.

```bash
/auto-fix Users are getting 500 errors when uploading large files
```

**Autonomous Workflow**:

1. **Research** → Error analysis and log investigation
2. **Review** → Code analysis for potential causes
3. **Fix Implementation** → Code changes and optimizations
4. **Testing** → Verify fix and prevent regression

### `/auto-review` - Code Quality Analysis

Comprehensive autonomous code review process.

```bash
/auto-review Review the entire authentication module for security and performance
```

**Autonomous Workflow**:

1. **Security Analysis** → Vulnerability assessment
2. **Performance Review** → Optimization opportunities
3. **Code Quality** → Best practices and maintainability
4. **Documentation** → Coverage and clarity assessment

### `/auto-test` - Test Suite Generation

Autonomous test creation and execution.

```bash
/auto-test Generate comprehensive tests for the payment processing module
```

**Autonomous Workflow**:

1. **Test Planning** → Test strategy and coverage analysis
2. **Unit Tests** → Component-level testing
3. **Integration Tests** → System interaction testing  
4. **E2E Tests** → User workflow validation

## 🧠 Intelligent Subagents

### Router Agent

- **Purpose**: Intelligent task analysis and delegation
- **Usage**: Automatically invoked by primary agents
- **Capabilities**: Analyzes requests and routes to optimal subagent combinations

### Context Manager  

- **Purpose**: Cross-agent knowledge management
- **Usage**: Maintains project context across all agent interactions
- **Capabilities**: Shares relevant context, tracks project state, synthesizes knowledge

### Execution Monitor

- **Purpose**: Multi-session task coordination
- **Usage**: Monitors complex workflows across sessions
- **Capabilities**: Progress tracking, dependency management, error recovery

### Enhanced Research Agent

- **Purpose**: Autonomous technical discovery
- **Manual Usage**: `@research Investigate GraphQL vs REST for our new API`
- **Capabilities**: Web research, documentation analysis, technology comparison

### Enhanced Architect Agent  

- **Purpose**: Autonomous architecture decisions
- **Manual Usage**: `@architect Design a scalable notification system`
- **Capabilities**: Pattern selection, system design, technology recommendations

## 📁 Domain-Specific Agents

Your existing specialized agents are now enhanced with autonomous capabilities:

- **`@api`** - API development with auto-routing to api-development skill
- **`@database`** - Database operations with entity-framework skill integration  
- **`@uxui`** - Frontend development with react-components/frontend-design skills
- **`@testing`** - Testing workflows with webapp-testing skill automation
- **`@devops`** - DevOps operations with docker-devops skill integration
- **`@security`** - Security analysis and implementation
- **`@performance`** - Performance optimization and monitoring
- **`@reviewer`** - Code review and quality assurance
- **`@documentation`** - Documentation generation and maintenance with google-style-docs skill

## 🛠️ Enhanced Tools & Integrations

### MCP Server Integrations

- **GitHub**: Repository operations and PR management (remote server)
- **Docker Desktop**: Preferred MCP gateway for additional tools and services

### Skills System

Automatically applied based on task domain:

- **api-development**: .NET Web API expertise
- **entity-framework**: Database operations
- **react-components**: React development
- **frontend-design**: UI/UX implementation  
- **webapp-testing**: Playwright testing
- **docker-devops**: Container operations
- **google-style-docs**: Google documentation standards

## 💡 Usage Examples

### Complex Feature Development

```
I need a real-time chat system with user presence, message history, file sharing, and mobile support
```

**Autonomous Response**: The system will automatically:
1. Research WebSocket implementations and real-time architectures
2. Design system architecture with scalability considerations
3. Implement backend API with real-time capabilities
4. Create frontend components with responsive design
5. Set up database schema with message persistence
6. Generate comprehensive tests across all components
7. Review security implications and performance characteristics

### Bug Investigation and Fix

```
Our application is running out of memory after a few hours of operation
```

**Autonomous Response**: The system will automatically:

1. Research common memory leak patterns
2. Analyze code for potential memory issues
3. Implement monitoring and debugging tools
4. Apply fixes based on findings
5. Create tests to prevent regression
6. Monitor performance improvements

### Code Quality Enhancement

```
Improve the code quality of our user management system
```

**Autonomous Response**: The system will automatically:
1. Review current code architecture and patterns
2. Identify technical debt and improvement opportunities
3. Implement refactoring improvements
4. Add missing tests and documentation
5. Verify improvements don't break existing functionality

## 🔄 Autonomous Workflows

### New Project Initialization

1. **Research** → Technology stack analysis
2. **Architecture** → System design and structure
3. **Planning** → Implementation roadmap
4. **Parallel Implementation** → Multiple agents working simultaneously
5. **Testing** → Comprehensive test coverage
6. **Documentation** → Project documentation

### Feature Enhancement

1. **Context Analysis** → Current system understanding
2. **Planning** → Enhancement strategy
3. **Implementation** → Code changes across multiple components
4. **Testing** → Feature validation
5. **Review** → Quality assurance

### Bug Resolution

1. **Investigation** → Root cause analysis
2. **Research** → Solution exploration
3. **Implementation** → Fix application
4. **Testing** → Fix verification and regression prevention

## 📊 Monitoring and Feedback

The autonomous system provides:

- **Progress Updates**: Real-time status of ongoing tasks
- **Context Summaries**: Cross-agent knowledge synthesis  
- **Quality Metrics**: Code quality and test coverage feedback
- **Performance Insights**: System optimization recommendations

## 🎛️ Configuration

The autonomous capabilities are configured in your `opencode.json`:

- **Enhanced Permissions**: Optimized for autonomous operation
- **Extended Steps**: Up to 50 autonomous iterations for complex tasks
- **Custom Commands**: Pre-configured autonomous workflows
- **Experimental Features**: Advanced coordination and monitoring

> [!NOTE]
> This configuration is FULLY autonomous. It WILL operate outside the workspace!
> Primarily this autonomy enables it to install dependency packages as needed to address issues.
> If you are NOT running in sandboxed environment, set `"external_directory": "ask"` for all agents.

## 🚀 Getting Started

1. **Start OpenCode**: Run `opencode` in your project directory
2. **Try Autonomous Commands**: Use `/auto-feature`, `/auto-fix`, `/auto-review`, or `/auto-test`  
3. **Experience Smart Delegation**: Ask for complex tasks and watch automatic subagent coordination
4. **Switch Agents**: Use `Tab` to switch between Build (autonomous) and Plan (detailed planning) modes

## 💭 Tips for Optimal Results

- **Be Specific**: Detailed requirements lead to better autonomous execution
- **Trust the Process**: Let agents coordinate and delegate automatically  
- **Use Context**: The system maintains awareness across sessions
- **Leverage Skills**: Domain-specific skills are automatically applied
- **Review Results**: Autonomous doesn't mean unchecked - review important changes

Your OpenCode environment now operates with Claude Code-like autonomy while maintaining full local development control and extensibility!

## 📚 Related Files

- [`opencode.json`](opencode.json) - Enhanced configuration with autonomous capabilities
- [`prompts/`](prompts/) - Autonomous coordination and planning prompts
- [`agents/`](agents/) - Specialized agent templates and configurations
- [`skills/`](skills/) - Domain-specific skills automatically applied to relevant agents
