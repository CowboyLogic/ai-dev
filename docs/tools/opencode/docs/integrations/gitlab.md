# OpenCode — GitLab Integration

> Source: <https://opencode.ai/docs/gitlab/>  
> Last updated: April 10, 2026

OpenCode integrates with GitLab through your CI/CD pipeline or GitLab Duo. In both cases, OpenCode runs on your GitLab runners.

---

## GitLab CI

Use OpenCode in a regular GitLab pipeline via the community [CI component](https://gitlab.com/nagyv/gitlab-opencode).

### Features

- **Custom config per job:** Use a custom config directory to enable/disable functionality per invocation
- **Minimal setup:** CI component sets up OpenCode in the background
- **Flexible:** Supports multiple inputs for customizing behavior

### Setup

**1. Store OpenCode auth as a CI/CD variable**

Go to Settings → CI/CD → Variables. Add your OpenCode authentication JSON as a **File** type variable. Mark as "Masked and hidden".

**2. Add to `.gitlab-ci.yml`:**

```yaml
include:
  - component: $CI_SERVER_FQDN/nagyv/gitlab-opencode/opencode@2
    inputs:
      config_dir: ${CI_PROJECT_DIR}/opencode-config
      auth_json: $OPENCODE_AUTH_JSON
      command: optional-custom-command
      message: "Your prompt here"
```

For more inputs and use cases, see the [component docs](https://gitlab.com/explore/catalog/nagyv/gitlab-opencode).

---

## GitLab Duo

OpenCode integrates with GitLab Duo, allowing you to mention `@opencode` in comments.

### Features

- **Triage issues:** Ask OpenCode to explain an issue
- **Fix and implement:** Ask OpenCode to fix an issue, create a branch, and open a merge request
- **Secure:** Runs on your GitLab runners

### Setup

1. Configure your GitLab environment
2. Set up CI/CD
3. Get an AI model provider API key
4. Create a service account
5. Configure CI/CD variables
6. Create a flow config file

See the [GitLab CLI agents docs](https://docs.gitlab.com/user/duo_agent_platform/agent_assistant/) for detailed instructions.

### Examples

```
# Explain an issue
@opencode explain this issue

# Fix an issue (creates branch + merge request)
@opencode fix this

# Review a merge request
@opencode review this merge request
```

You can configure a different trigger phrase than `@opencode`.
