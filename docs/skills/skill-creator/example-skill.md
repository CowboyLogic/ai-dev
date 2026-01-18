---
name: github-actions-failure-debugging
description: Guide for debugging failing GitHub Actions workflows. Use this when asked to debug failing GitHub Actions workflows or CI/CD pipeline failures.
---

# GitHub Actions Failure Debugging

This skill provides a systematic approach to debugging failing GitHub Actions workflows in pull requests.

## When to Use This Skill

Use this skill when:
- GitHub Actions workflows are failing
- CI/CD pipeline shows red status
- Pull request checks are not passing
- Asked to investigate or fix workflow failures

## Prerequisites

- Access to GitHub MCP Server tools
- Repository with GitHub Actions workflows
- Appropriate permissions to view workflow logs

## Instructions

1. **List recent workflow runs** for the pull request
   
   Use the `list_workflow_runs` tool to retrieve recent runs and their status:
   ```bash
   # Tool will return: workflow names, run IDs, status, conclusion
   ```

2. **Identify failed jobs**
   
   Review the workflow run results to find:
   - Which workflows failed
   - Which specific jobs failed within those workflows
   - Timestamp and trigger information

3. **Get summarized failure information**
   
   Use the `summarize_job_log_failures` tool to get an AI summary of failed job logs:
   - This avoids filling context with thousands of log lines
   - Provides focused failure analysis
   - Highlights key error messages and patterns

4. **Retrieve detailed logs if needed**
   
   If the summary doesn't provide enough information:
   - Use `get_job_logs` tool with the specific job ID
   - Use `get_workflow_run_logs` tool for complete workflow logs
   - Search for error messages, stack traces, or failure indicators

5. **Attempt local reproduction**
   
   Try to reproduce the failure in your own environment:
   - Check out the same branch
   - Run the same commands locally
   - Verify environment variables and dependencies match

6. **Fix the failing build**
   
   Based on the error analysis:
   - Make necessary code changes
   - Update workflow configuration if needed
   - Ensure dependencies are properly specified
   - Add error handling or missing resources

7. **Verify the fix**
   
   Before committing:
   - Test locally if you reproduced the issue
   - Check that the fix addresses the root cause
   - Consider adding tests to prevent regression
   - Review workflow syntax if configuration was changed

## Examples

### Example 1: Test Failure

A workflow fails with test errors.

**Steps:**
1. Use `summarize_job_log_failures` → "3 unit tests failing in user authentication module"
2. Examine specific test failures
3. Run tests locally: `npm test -- --grep authentication`
4. Fix the failing tests
5. Verify all tests pass locally
6. Commit and push changes

### Example 2: Dependency Installation Failure

A workflow fails during dependency installation.

**Steps:**
1. Use `get_job_logs` for the "Install dependencies" step
2. Look for package resolution errors: `npm ERR! 404 Not Found - package@version`
3. Check package.json for typos or incorrect versions
4. Update to correct package version
5. Test installation locally: `npm install`
6. Commit fix with clear message

### Example 3: Environment Configuration Issue

A workflow fails with missing environment variables.

**Steps:**
1. `summarize_job_log_failures` → "Environment variable DATABASE_URL not set"
2. Check workflow file for required secrets/variables
3. Verify secrets are configured in repository settings
4. If missing, add the required secret
5. If configured, check workflow syntax for correct reference
6. Re-run the workflow

## Best Practices

- Start with summarized logs to avoid context overflow
- Focus on the first failure in a sequence (later failures may be cascading)
- Check recent changes to code and workflow files
- Look for common patterns: dependency version conflicts, missing files, permission issues
- Document the root cause in commit messages
- Consider if the failure indicates a broader issue that needs addressing

## Common Issues

**Issue**: Logs show "Resource not available" or timeout errors  
**Solution**: Check if external services or dependencies are accessible. May need to update URLs or credentials.

**Issue**: "File not found" errors in workflow  
**Solution**: Verify file paths are correct relative to repository root. Check if files are committed and pushed.

**Issue**: Tests pass locally but fail in CI  
**Solution**: Check for environment differences (OS, Node version, environment variables). Update workflow to match local environment or fix environment-specific code.

**Issue**: Intermittent failures  
**Solution**: Look for race conditions, timing-dependent tests, or flaky external dependencies. Consider retry logic or more robust test design.

## Additional Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Workflow syntax reference](https://docs.github.com/en/actions/reference/workflow-syntax-for-github-actions)
- [GitHub Actions troubleshooting](https://docs.github.com/en/actions/monitoring-and-troubleshooting-workflows)
