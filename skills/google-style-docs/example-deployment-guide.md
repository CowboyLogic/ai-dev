# Example: Deploy a Node.js application

This example demonstrates a complete how-to guide written in Google documentation style.

---

# Deploy a Node.js application to Cloud Run

Deploy your Node.js application to Cloud Run, Google Cloud's fully managed serverless platform. After completing these steps, your application will be publicly accessible via HTTPS.

## Before you begin

- Install the [Google Cloud CLI](https://cloud.google.com/sdk/docs/install)
- Create a [Google Cloud project](https://cloud.google.com/resource-manager/docs/creating-managing-projects)
- Enable the [Cloud Run API](https://console.cloud.google.com/apis/library/run.googleapis.com)
- Install [Docker](https://docs.docker.com/get-docker/) (version 20.10 or later)

## Prepare your application

1. Create a `Dockerfile` in your project root:
   ```dockerfile
   FROM node:18-alpine
   
   WORKDIR /app
   
   # Copy package files and install dependencies
   COPY package*.json ./
   RUN npm ci --only=production
   
   # Copy application code
   COPY . .
   
   # Expose port and start application
   EXPOSE 8080
   CMD ["npm", "start"]
   ```

2. Add a `.dockerignore` file to exclude unnecessary files:
   ```
   node_modules
   .git
   .env
   ```

3. Ensure your application listens on the port specified by the `PORT` environment variable:
   ```javascript
   const PORT = process.env.PORT || 8080;
   app.listen(PORT, () => {
     console.log(`Server listening on port ${PORT}`);
   });
   ```
   Cloud Run sets the `PORT` environment variable automatically.

## Build and deploy the application

1. Authenticate with Google Cloud:
   ```bash
   gcloud auth login
   ```
   A browser window opens. Complete the sign-in process with your Google account.

2. Set your project ID:
   ```bash
   gcloud config set project PROJECT_ID
   ```
   Replace `PROJECT_ID` with your Google Cloud project ID.

3. Build and deploy your application in one command:
   ```bash
   gcloud run deploy myapp \
     --source . \
     --region us-central1 \
     --allow-unauthenticated
   ```
   
   This command:
   - Builds a container image from your application
   - Pushes the image to Container Registry
   - Deploys the image to Cloud Run in the `us-central1` region
   - Makes the service publicly accessible
   
   The deployment takes 2-5 minutes. When complete, the command displays your service URL:
   ```
   Service [myapp] revision [myapp-00001] has been deployed and is serving 100 percent of traffic.
   Service URL: https://myapp-abc123-uc.a.run.app
   ```

4. Test your deployed application:
   ```bash
   curl https://SERVICE_URL
   ```
   Replace `SERVICE_URL` with the URL from the previous step.

## Update your application

To deploy a new version:

1. Make changes to your application code.

2. Deploy the updated application:
   ```bash
   gcloud run deploy myapp --source .
   ```
   Cloud Run creates a new revision and gradually shifts traffic to it.

## Configure environment variables

To add environment variables to your service:

```bash
gcloud run services update myapp \
  --set-env-vars="API_KEY=YOUR_API_KEY,DEBUG=true"
```

**Caution:** Don't store sensitive values directly in environment variables. Use [Secret Manager](https://cloud.google.com/secret-manager/docs) for sensitive data.

## Monitor your application

1. View your service logs:
   ```bash
   gcloud run logs read myapp --limit=50
   ```

2. Open the Cloud Run console to view metrics:
   ```bash
   gcloud run services describe myapp --format="value(status.url)"
   ```
   Open the displayed URL in your browser and append `/logs` to view detailed metrics.

## What's next

- [Set up a custom domain](https://cloud.google.com/run/docs/mapping-custom-domains)
- [Configure continuous deployment](https://cloud.google.com/run/docs/continuous-deployment-with-cloud-build)
- [Implement authentication](https://cloud.google.com/run/docs/authenticating/overview)
- [Optimize container startup time](https://cloud.google.com/run/docs/tips/general)

---

## Why This Example Follows Google Style

### Title and Structure
- ✅ Uses sentence case: "Deploy a Node.js application to Cloud Run"
- ✅ Task-oriented and specific
- ✅ Clear introduction stating purpose and outcome
- ✅ Proper heading hierarchy (H1 → H2)

### Voice and Tone
- ✅ Uses second person: "your application", "you complete"
- ✅ Active voice: "Cloud Run sets the PORT variable" (not "The PORT variable is set")
- ✅ Present tense: "The command displays" (not "will display")
- ✅ Conversational: Uses contractions like "don't"

### Instructions
- ✅ Numbered steps with one action each
- ✅ Imperative mood: "Create a Dockerfile", "Deploy your application"
- ✅ Shows expected results after commands
- ✅ Includes verification steps

### Code and Formatting
- ✅ Complete, runnable code examples
- ✅ Language specified for code blocks (dockerfile, javascript, bash)
- ✅ Comments explain non-obvious parts
- ✅ Placeholders clearly marked: PROJECT_ID, SERVICE_URL
- ✅ Inline code uses backticks: `PORT`, `.dockerignore`
- ✅ UI elements would be bolded (none in this example)

### Accessibility
- ✅ Descriptive link text: [Google Cloud CLI] not [here]
- ✅ Proper alt text for images (none in this example)
- ✅ Inclusive language (they/their if pronouns were used)
- ✅ No skipped heading levels

### Additional Elements
- ✅ Prerequisites listed clearly
- ✅ Caution callout for security concern
- ✅ "What's next" section with related resources
- ✅ Expected command output shown
- ✅ Error handling considerations

### Word Choice
- ✅ "Enter" for commands (not "type in")
- ✅ "Complete the sign-in process" (not "login")
- ✅ No "please", "simply", or "just"
- ✅ No Latin abbreviations (would use "for example" not "e.g.")
