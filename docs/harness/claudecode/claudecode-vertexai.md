# Claude Code with Google Vertex AI

Run Claude Code against Claude models served through your own Google Cloud project instead of
Anthropic's API. This is the usual route when an organization manages model access, billing, and
audit through Google Cloud.

> [!NOTE]
> Google now calls this service **Google Cloud's Agent Platform**, formerly Vertex AI. Claude Code's
> login prompt still labels it **Google Vertex AI**, and its environment variables keep the `VERTEX`
> name.

This page covers the minimum setup. Anthropic maintains the full procedure, including IAM, region
rules, model pinning, and troubleshooting, in
[Claude Code on Google Cloud's Agent Platform](https://code.claude.com/docs/en/google-vertex-ai).
Follow that page when the two differ.

## Before you start

- A Google Cloud project with billing enabled and the Agent Platform API (`aiplatform.googleapis.com`) enabled
- Access to the Claude models you want, requested in the Agent Platform Model Garden
- The `gcloud` CLI, signed in to an account that holds the `roles/aiplatform.user` role
- Quota in the region you plan to use

## Set it up

There are two routes, and they end in the same place.

### Sign in with the wizard

Run `claude`. At the login prompt choose **3rd-party platform**, then **Google Vertex AI**. If you are
already signed in, run `/login` to reach the same menu. The wizard asks how you authenticate to Google
Cloud, which project and region to use, and which models to pin. It saves the result in the `env` block of
your user settings file, so you do not export anything yourself. Run `/setup-vertex` later to change
any of it.

### Set environment variables

Use this route for CI and scripted rollouts:

```bash
export CLAUDE_CODE_USE_VERTEX=1
export CLOUD_ML_REGION=global
export ANTHROPIC_VERTEX_PROJECT_ID=YOUR-PROJECT-ID
```

Claude Code authenticates with standard Google Cloud credentials. For a developer machine, run
`gcloud auth application-default login`. For a service account, point `GOOGLE_APPLICATION_CREDENTIALS`
at its key file.

`CLOUD_ML_REGION` accepts `global`, a multi-region location such as `eu` or `us`, or a specific region such
as `us-east5`. Not every model is available on every endpoint type, so check Model Garden if you get a
"model not found" error.

## Pin model versions for teams

Without pinning, the model aliases `opus` and `sonnet` resolve to whatever default your Claude Code
version ships, which may not be enabled in your project. When you roll Claude Code out to more than one
person, pin each alias with `ANTHROPIC_DEFAULT_OPUS_MODEL`, `ANTHROPIC_DEFAULT_SONNET_MODEL`, and
`ANTHROPIC_DEFAULT_HAIKU_MODEL`. Model IDs change with each release, so take them from the
[models overview](https://platform.claude.com/docs/en/about-claude/models/overview) rather than from a
copy here.

## Verify

Start `claude` and run `/status`. The `API provider` line should read `Google Vertex AI`, and the project,
region, and model lines should show your values. If the provider line is missing, the variables are not
reaching the process: export them in the shell that launched `claude`, or put them in the `env` block of
your settings file.

## Related

- [Claude Code on Google Cloud's Agent Platform](https://code.claude.com/docs/en/google-vertex-ai): Anthropic's full guide
- [Claude Code Settings Manager skill](../../skills/client-config-claudecode.md): where the `env` block and other settings live
- [Claude Code overview](index.md)
