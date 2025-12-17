# Mission 3: Infrastructure & Deployment

## 1. Objective
Deploy the MCP server to Google Cloud Run and configure the CI/CD pipeline via Cloud Build.

## 2. Deployment constraints
- **Platform**: Google Cloud Run (Serverless).
- **Protocol**: Since Cloud Run is HTTP-based, ensure `FastMCP` is configured to run in **SSE (Server-Sent Events)** mode so it can communicate with clients over HTTP.
- **Port**: 8080.

## 3. Implementation Tasks
- [ ] **Dockerfile**:
    - Base image: `python:3.11-slim`.
    - Install system dependencies (if any).
    - Copy `src/`, `prompts/`, and `requirements.txt`.
    - Entrypoint: Command to run the FastMCP server in SSE mode (e.g., `uvicorn src.server:app ...`).
- [ ] **Cloud Build Config**: Create `cloudbuild.yaml`.
    - Step 1: Build Docker image.
    - Step 2: Push to Google Container Registry (GCR) or Artifact Registry.
    - Step 3: `gcloud run deploy` command.
- [ ] **Documentation**: Create `DEPLOY.md` containing "Click-Ops" instructions for:
    - Creating the Secret Manager secrets (`NEO4J_PASSWORD`, `OPENAI_API_KEY`).
    - Mapping those secrets to environment variables in the Cloud Run UI.

## 4. Definition of Done
- Local Docker build succeeds: `docker build -t medical-mcp .`
- Local Docker run works: Container starts and accepts HTTP requests on port 8080.
- `cloudbuild.yaml` is valid (can be verified with `gcloud builds submit --dry-run`).