---
title: "AI-Assisted Development: Containerized Agent Execution Pattern"
status: "Draft"
version: "0.1.0"
author: "[YOUR_NAME]"
role: "[YOUR_ROLE]"
team: "[YOUR_TEAM]"
confluence_space: "[SPACE_KEY]"
confluence_ancestor: "[PARENT_PAGE_TITLE]"
confluence_labels:
  - architecture-pattern
  - ai-assisted-development
  - security
  - "[ADD_ADDITIONAL_LABELS]"
classification: "[CLASS_1_OR_2 — CONFIRM BEFORE PUBLISHING]"
created: "2026-04-18"
last_updated: "2026-04-18"
review_date: "[DATE — RECOMMENDED: 6 MONTHS FROM APPROVAL]"
---

# AI-Assisted Development: Containerized Agent Execution Pattern

## Status

| Field | Value |
|---|---|
| Status | Draft — Not for Distribution |
| Version | 0.1.0 |
| Author | [YOUR_NAME] |
| Last Updated | 2026-04-18 |
| Review Date | [DATE] |
| Classification | [CLASS] |

---

## 1. Problem Statement

### The Opportunity

AI coding agents are becoming a practical part of the software development lifecycle. Engineers
are already using approved tools (GitHub Copilot, VertexAI-backed assistants) to accelerate
individual development tasks. The natural next step is extending agent assistance into broader
workflows — code generation, refactoring, infrastructure-as-code authoring, and eventually
pipeline automation.

### The Challenge

Agents are not deterministic. Unlike traditional developer tooling, an agent can:

- Misinterpret scope and modify files outside the intended change set
- Generate plausible but incorrect infrastructure changes with real consequences
- Operate across thousands of files in a microservice estate if not explicitly bounded
- Produce output that is syntactically correct but semantically wrong

In an environment of thousands of microservices, heavy IaC, and stringent regulatory obligations,
an unbounded agent is an unacceptable risk — not because agents are untrustworthy in principle,
but because the blast radius of a misunderstood task is potentially enormous.

### The Gap

Existing developer tooling controls — approved vendor lists, trusted source requirements,
data classification policies — are necessary but insufficient for agentic workflows. They
govern *what tools* can be used and *what data* can be touched. They do not govern *how
broadly* an agent can act within an approved context.

This pattern addresses that gap.

---

## 2. What This Pattern Is Not

Before describing what this pattern enables, it is important to be explicit about what it
does not authorize or replace.

- **Not a replacement for deterministic pipeline controls.** Existing GitHub workflow
  automation is fully deterministic by design. This pattern does not introduce agents
  into those workflows without explicit, scoped, gated integration points.

- **Not an authorization to expose Class 5 data to agents.** PII and Class 5 data are
  categorically excluded from this pattern. No mount strategy, no vendor approval, and
  no compensating control changes this.

- **Not an autonomous execution model.** Agents operating under this pattern produce
  output for human review. They do not self-approve, self-merge, or self-deploy.

- **Not a production execution pattern.** Agents do not execute against production
  environments, production infrastructure, or production data under this pattern.

- **Not a shortcut around the security review process.** Repositories marked sensitive,
  Class 4 code with elevated risk profiles, and any IaC execution beyond `plan` require
  a separate security review before agent use.

---

## 3. Pattern Overview

### Core Concept

A container provides an OS-enforced execution boundary around an agent's working environment.
The agent operates inside the container. The agent's access to the codebase, filesystem, and
network is determined by what is explicitly mounted and permitted — not by what the agent
decides to access.

The container is the control. Agent compliance directives are a supplement, not a substitute.

### The Two Deployment Contexts

This pattern covers two distinct contexts with different risk profiles, control requirements,
and implementation approaches:

**Context A — Local Developer Environment**

- An engineer uses an agent to assist with a bounded development task
- The agent operates inside a container on the engineer's workstation
- Output is reviewed by the engineer before anything leaves the container
- Risk profile: moderate — governed by existing developer tooling controls

**Context B — Agentic CI/CD Pipeline Step**

- An agent operates as a controlled, scoped step within a GitHub workflow
- The agent is not autonomous — it operates within explicitly defined pipeline boundaries
- Output is gated: agent output becomes a PR, never a direct merge
- Risk profile: elevated — requires stricter controls and explicit security review

### The Agent Execution Model

Within both contexts, two agent roles are maintained:

- **Thinking Agent** — the primary agent the engineer interacts with for planning, design,
  and task decomposition. Produces handoff prompts for execution agents.
- **Execution Agent** — receives a discrete, scoped, self-contained task prompt. Operates
  inside the container. Has no session context beyond the prompt it receives.

This separation is intentional. The thinking agent reasons. The execution agent executes.
Conflating the two roles removes the review gate that makes the pattern safe.

---

## 4. Trust Model & Data Classification

### Approved AI Vendors

This pattern inherits the existing approved vendor policy. Agents must use approved AI
vendors only. At time of writing:

- **Approved for local desktop use:** GitHub Copilot
- **Approved for cloud-based agent execution:** Google Cloud VertexAI
- **Other vendors:** Require separate security review and approval before use

> [!NOTE]
> The approved vendor list is the authoritative source. This document references
> it but does not define it. Always verify current approved vendor status before use.

### Data Classification Constraints

| Classification | Description | Agent Use |
|---|---|---|
| Class 1 | Fully public knowledge | Permitted — no restrictions |
| Class 2 | Internal, non-sensitive | Permitted — standard controls apply |
| Class 3 | Internal, business sensitive | Permitted — mount scope controls required |
| Class 4 | Internal application code | Permitted with controls — see Section 5 & 6 |
| Class 4 Sensitive | Encryption algorithms, threat models, etc. | Requires separate security review |
| Class 5 | PII and regulated personal data | Categorically excluded |

The Class 4 approval for standard application code inherits the precedent established by
the existing GitHub Copilot desktop approval — agent-assisted development against internal
application code is an accepted risk posture when appropriate controls are in place.

### The Cloud API Boundary

This is the most important control consideration in this pattern and must be understood
clearly by any engineer using it.

When a cloud-based agent (VertexAI, Copilot) processes a task, the content of that task —
including any code or file content included in the prompt — is transmitted to the vendor's
API. **The container isolates execution. It does not prevent code from leaving the
container via an API call.**

This means:

- Code mounted into the container and included in an agent prompt leaves the building
- The data residency and retention policies of the approved vendor govern what happens to it
- Engineers must understand what they are including in agent prompts, not just what they
  are mounting into the container
- Class 4 Sensitive repositories require security review precisely because of this boundary

This is not unique to this pattern — it is true of any AI-assisted development tool.
This pattern makes it explicit because many engineers do not consider it.

---

## 5. Context A: Local Developer Environment

### Container Image Requirements

- Base image must be sourced from the internal Artifact Registry
- Must derive from an approved golden base image
- Custom layers must not introduce unapproved tooling or external dependencies
- All dependencies must be sourced from internal trusted repositories
- Image must be versioned and reproducible — no `latest` tags in production use

### Mount Strategy

The mount scope is the primary control mechanism in the local context.

**What gets mounted:**

- The specific repository or service directory relevant to the task
- No broader filesystem access than the task requires
- Configuration files required for the agent's toolchain (read-only)

**Mount permissions:**

- Source code: read-only by default; read-write only when the agent is explicitly
  generating or modifying files as the task output
- `agents-output/` directory: read-write always — this is the agent's designated
  scratch space (see Scratch Space below)
- `.git/` directory: read-only — the agent can read branch and history context
  but cannot make git operations directly

**What is explicitly excluded from mounts:**

- Credentials, secrets, or `.env` files containing sensitive values
- SSH keys or cloud authentication files
- Any path outside the scoped repository or service directory
- Class 5 data stores or any path known to contain PII
- Class 4 Sensitive repositories (without separate security review)

### Agent Execution Model

**Thinking agent responsibilities (outside the container):**

- Understand the task and decompose it into discrete, bounded subtasks
- Produce handoff prompts that are self-contained and scope-explicit
- Review all output before integration
- Make all judgment calls — the execution agent makes none

**Execution agent responsibilities (inside the container):**

- Execute exactly what the handoff prompt specifies
- Write output to `agents-output/` unless the task is an explicit file modification
- Flag ambiguity rather than resolve it independently
- Produce a diff or artifact for review — not a completed integration

### Scratch Space — `agents-output/`

- All temporary files, intermediate artifacts, and generated drafts go to `agents-output/`
  in the project root inside the container
- If `agents-output/` does not exist, the agent creates it
- `agents-output/` must be in `.gitignore` — the agent adds it if not present
- Contents of `agents-output/` are reviewed by the engineer before any artifact is
  promoted to the working tree

### Branch Protection

- The agent does not commit directly to `main` or `trunk`
- All agent-assisted changes land on a feature branch
- Branch creation is the engineer's responsibility before handing off to the agent
- If no feature branch exists when a file write is initiated, the agent stops and asks

### Audit & Logging Requirements

- Container run logs must be retained for the duration of the associated PR lifecycle
- What the agent was asked to do (the handoff prompt) must be preserved
- What the agent produced must be traceable to the prompt that produced it
- Logging specifics will vary by team toolchain — minimum requirement is prompt + output
  retained until PR is merged or closed

---

## 6. Context B: CI/CD Pipeline Step

> [!IMPORTANT]
> This context has an elevated risk profile. Implementation requires explicit
> security review before use in any pipeline touching Class 4 code or infrastructure.
> The guidance below is directional — it is not an implementation authorization.

### Where Agents Fit in the Pipeline Model

Agents in a pipeline context are not autonomous actors. They are scoped, bounded steps
that produce output for downstream human or automated review gates.

The mental model:

```
Trigger (PR, schedule, event)
  ↓
[Deterministic steps — unchanged]
  ↓
Agent Step (scoped, containerized, time-bounded)
  ↓
Output Gate (human review via PR, or automated validation)
  ↓
[Deterministic steps — unchanged]
```

Agents do not replace deterministic steps. They operate between them, within explicit
boundaries, with their output validated before anything downstream consumes it.

### Container Image Requirements (Pipeline)

Stricter than local context:

- Immutable image — digest-pinned, not tag-referenced
- No interactive shell access
- Network egress restricted to approved endpoints only (vendor API, internal registries)
- No mount of credentials beyond the minimum required for the agent's task
- Image scanning required before use in any pipeline

### Permitted vs. Prohibited Operations

| Operation | Permitted | Notes |
|---|---|---|
| Code generation | ✅ | Output to PR only |
| Code modification | ✅ | Output to PR only |
| Test generation | ✅ | Output to PR only |
| IaC authoring (Terraform plan) | ✅ | Plan output for review — not apply |
| IaC execution (Terraform apply) | ❌ | Categorically prohibited in agent context |
| Direct commit to main/trunk | ❌ | Always prohibited |
| Secrets access beyond task scope | ❌ | Always prohibited |
| Network access beyond approved endpoints | ❌ | Always prohibited |
| Production environment interaction | ❌ | Always prohibited |

### Output Gating

- Agent output in a pipeline context always surfaces as a PR — never as a direct merge
- The PR is the review artifact — it must clearly identify that content was agent-generated
- Agent-generated PRs must be reviewed by a human before merge
- Automated merge of agent-generated PRs is not permitted under this pattern

### Audit Trail Requirements

Pipeline context has stricter audit requirements than local context:

- The handoff prompt that produced the agent's output must be stored as a pipeline artifact
- Agent model version and vendor must be recorded
- Container image digest must be recorded
- All of the above must be retained per existing pipeline artifact retention policy

### Rollback Posture

- Agent-generated changes that cause issues are reverted via standard git revert
- No special rollback procedure is required beyond existing pipeline practices
- The PR review gate is the primary prevention mechanism — rollback is the recovery mechanism

---

## 7. Control Requirements Summary

> [!NOTE]
> This section maps pattern controls to control categories. Specific control
> identifiers should be validated against the current control register before submission
> for formal review.

| Control Area | Pattern Control | Relevant Frameworks |
|---|---|---|
| Data classification enforcement | Mount scope restrictions, Class 5 exclusion | SOC2, PCI, ISO 27001 |
| Approved vendor use | Inherits existing approved vendor policy | SOC2, ISO 27001 |
| Access control | Container mount permissions, read-only defaults | SOC2, PCI, ISO 27001 |
| Change management | Branch protection, PR-only output, human review gate | SOC2, ISO 27001 |
| Audit logging | Prompt + output retention, pipeline artifact requirements | SOC2, PCI, ISO 27001 |
| Secrets management | Explicit exclusion from mounts | SOC2, PCI, ISO 27001 |
| Network controls | Approved endpoint restriction (pipeline context) | SOC2, PCI, ISO 27001 |
| Incident response | Standard git revert as recovery mechanism | SOC2, ISO 27001 |

### Compensating Controls

The following areas have identified gaps where compensating controls apply:

- **Cloud API data boundary:** The container does not prevent code from reaching vendor
  APIs. Compensating control: approved vendor policy governs data handling at the API level.
  Engineers must be trained on what this boundary means in practice.
- **Agent output correctness:** No automated control validates that agent output is
  semantically correct. Compensating control: mandatory human review gate before any
  agent output is integrated.
- **Prompt injection:** Agent output in pipeline context could be influenced by malicious
  content in the codebase being processed. Compensating control: treat all agent output
  as untrusted input — validate before use.

---

## 8. Implementation Guidance

### Local Setup (Context A)

**Prerequisites:**

- Docker Desktop installed and running
- Access to internal Artifact Registry
- Approved AI vendor tooling configured (Copilot / VertexAI)
- Feature branch created before beginning agent-assisted work

**Getting started:**

```bash
# Pull approved base image from internal registry
docker pull [INTERNAL_REGISTRY]/[APPROVED_BASE_IMAGE]:[VERSION]

# Run container with scoped mount
docker run -it \
  --rm \
  -v /path/to/your/service:/workspace:ro \
  -v /path/to/your/service/agents-output:/workspace/agents-output:rw \
  [INTERNAL_REGISTRY]/[APPROVED_BASE_IMAGE]:[VERSION]
```

> [!NOTE]
> Base image names, registry paths, and recommended toolchain
> configuration will be defined as part of the formal pattern implementation. The above
> illustrates the structural approach only.

**Confirming the scratch space:**

```bash
# Inside the container — verify agents-output exists and is writable
ls -la /workspace/agents-output

# If it doesn't exist, create it
mkdir -p /workspace/agents-output

# Confirm .gitignore coverage (from host, after container run)
grep "agents-output" /path/to/your/service/.gitignore
```

### Pipeline Integration (Context B)

> [!WARNING]
> Pipeline integration requires security review before implementation.
> The below is directional structure only.

High-level GitHub workflow step structure:

```yaml
# Illustrative structure only — not a ready-to-use workflow
- name: Agent-Assisted [TASK_NAME]
  uses: [INTERNAL_REGISTRY]/[APPROVED_AGENT_ACTION]@[DIGEST]
  with:
    image: [INTERNAL_REGISTRY]/[APPROVED_BASE_IMAGE]@[DIGEST]
    prompt_file: .github/agent-prompts/[TASK_PROMPT].md
    output_path: agents-output/
    max_execution_time: [TIME_LIMIT]
  env:
    AGENT_VENDOR_ENDPOINT: ${{ vars.APPROVED_AGENT_ENDPOINT }}
    # No secrets beyond minimum required scope
```

Key implementation requirements:

- Use digest-pinned image references — never tags
- Prompt stored as a versioned file in the repository — not inline in the workflow
- Output path explicitly bounded to `agents-output/`
- Execution time limit enforced — unbounded agent execution is not permitted
- Downstream PR creation step is separate from agent execution step

### Backstage Integration Path

- This pattern is a candidate for inclusion in the engineering handbook as an approved
  development practice
- A Backstage software template for scaffolding agent-ready service repositories
  (pre-configured `.gitignore`, `agents-output/` structure, approved base image reference)
  is a logical extension once the pattern is formally approved
- TechDocs publication of this document will be configured via the standard publishing
  pipeline upon approval

---

## 9. Known Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Prompt injection via codebase content | Medium | High | Treat all agent output as untrusted — validate before integration |
| Mount scope creep over time | Medium | Medium | Mount scope defined in handoff prompt — reviewed as part of PR process |
| Agent output used without review | Medium | High | PR-only output gate — human review mandatory before merge |
| Vendor API data residency | Low | High | Approved vendor policy governs — engineers trained on cloud API boundary |
| Unapproved base image use | Low | Medium | Image sourcing policy — internal Artifact Registry only |
| Class 4 Sensitive code exposure | Low | Critical | Categorical exclusion — separate security review required |
| Unbounded pipeline execution | Low | High | Execution time limits enforced at workflow level |
| Agent makes infrastructure changes | Low | Critical | `terraform apply` and equivalent categorically prohibited |

---

## 10. What Requires Security Review Before Use

The following scenarios are outside the scope of this pattern's general approval and require
a separate security review before an agent may be used:

- Any repository marked sensitive (regardless of classification level)
- Class 4 code where the application handles financial transactions or authentication
- Any pipeline context where agent output could influence production infrastructure
- IaC execution beyond `plan` output (apply, destroy, or equivalent)
- Agent use with any vendor not on the current approved vendor list
- Any scenario involving data that may be Class 5 adjacent — when in doubt, escalate

---

## 11. Future Considerations

The following are not in scope for this pattern version but represent logical evolution
as the practice matures:

- **Self-hosted model execution** — air-gapped agent execution using internally hosted
  models eliminates the cloud API boundary risk entirely. Viable as GCP-hosted model
  serving matures.
- **VertexAI native agent execution pattern** — a GCP-native implementation that leverages
  VertexAI agent infrastructure rather than container-wrapped API calls. Likely the
  long-term architecture for pipeline context.
- **Backstage plugin for agent execution governance** — centralized visibility into
  agent use across the engineering organization. Audit, policy enforcement, and
  approved prompt library management.
- **Approved prompt library** — a governed, version-controlled library of validated
  agent handoff prompts for common development tasks. Reduces prompt engineering burden
  on individual engineers and creates a consistent, reviewable baseline.
- **Expanded approved vendor list** — as the AI vendor landscape matures and additional
  vendors complete security review, this pattern should be revisited to ensure controls
  remain appropriate for the approved vendor set.

---

## 12. Architecture Decision Record

### Decision

Establish a containerized execution boundary as the standard control mechanism for
AI agent use in software development workflows, covering both local developer environments
and CI/CD pipeline integration.

### Rationale

- **Blast radius containment:** Container isolation enforces scope boundaries at the OS
  level, not through agent compliance directives alone
- **Existing precedent:** Approved use of GitHub Copilot for desktop development establishes
  that AI-assisted development against Class 4 code is an accepted risk posture
- **Regulatory alignment:** Mount scope controls, mandatory review gates, and audit
  logging requirements map to existing SOC2, PCI, and ISO 27001 obligations
- **Platform alignment:** Container-based execution aligns with existing GCP and GitHub
  infrastructure — no net-new platforms required
- **Engineer adoption:** The pattern extends existing developer workflows rather than
  replacing them — lower adoption friction

### Implications

- Engineers using agents for development tasks should follow this pattern
- Pipeline integration requires security review before implementation
- Class 5 data and sensitive Class 4 repositories remain excluded
- An approved base image must be maintained in the internal Artifact Registry
- Training will be required — particularly on the cloud API boundary and data classification
  constraints

### Alternatives Considered

| Alternative | Reason Not Selected |
|---|---|
| No formal pattern — ad hoc agent use | Inconsistent controls, no audit trail, unacceptable blast radius risk |
| Agent use without containerization | No OS-level scope enforcement — relies entirely on agent compliance |
| Prohibit agent use entirely | Foregoes legitimate productivity and quality benefits; not sustainable |
| VM-based isolation | Higher overhead, slower iteration, no meaningful security advantage over containers for this use case |

### Open Questions

- [ ] Approved base image definition and ownership
- [ ] Minimum logging and retention specification
- [ ] Training requirements and delivery mechanism
- [ ] Backstage template scope and timeline
- [ ] Security review process for elevated-risk scenarios

### Review & Approval

| Role | Name | Status | Date |
|---|---|---|---|
| Author | [YOUR_NAME] | Draft | 2026-04-18 |
| Architecture Review | [REVIEWER] | Pending | — |
| Security Review | [REVIEWER] | Pending | — |
| [ADDITIONAL_REVIEWERS] | — | Pending | — |

---

## Appendix A: Glossary

| Term | Definition |
|---|---|
| Thinking Agent | The primary AI agent the engineer interacts with for planning and task decomposition |
| Execution Agent | A scoped AI agent that receives a discrete handoff prompt and executes within the container |
| Handoff Prompt | A self-contained task prompt produced by the thinking agent for the execution agent |
| Blast Radius | The scope of unintended impact if an agent misunderstands or misexecutes a task |
| Mount | A filesystem path from the host machine made accessible inside a container |
| `agents-output/` | The designated scratch space inside the container for agent-generated temporary artifacts |
| Class 4 Sensitive | Class 4 repositories with elevated risk profiles requiring separate security review |
| PR Gate | The requirement that agent output surfaces as a pull request for human review before integration |

---

## Appendix B: Related Resources

- Approved AI Vendor List — [INTERNAL_LINK]
- Data Classification Policy — [INTERNAL_LINK]
- Internal Artifact Registry — [INTERNAL_LINK]
- GitHub Workflow Golden Path — [INTERNAL_LINK]
- Engineering Handbook — [INTERNAL_LINK]
- Backstage Developer Portal — [INTERNAL_LINK]
- Security Review Request Process — [INTERNAL_LINK]
