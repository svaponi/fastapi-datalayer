#!/bin/bash
set -euo pipefail

# See https://cloud.google.com/blog/products/identity-security/enabling-keyless-authentication-from-github-actions
# Also see https://cloud.google.com/iam/docs/workload-identity-federation-with-deployment-pipelines
# Also see https://medium.com/@bbeesley/notes-on-workload-identity-federation-from-github-actions-to-google-cloud-platform-7a818da2c33e

REMOTE_URL=$(git remote get-url origin)
if [[ ${REMOTE_URL} == git@* ]]; then
  GITHUB_REPOSITORY=$(echo "${REMOTE_URL}" | sed -E 's/^git@[^:]+:(.+)\.git$/\1/')
elif [[ ${REMOTE_URL} == https://* ]]; then
  GITHUB_REPOSITORY=$(echo "${REMOTE_URL}" | sed -E 's/^https:\/\/[^/]+\/(.+)\.git$/\1/')
else
  echo "Unknown remote URL format: ${REMOTE_URL}"
  exit 1
fi

GCP_PROJECT_ID=$(gcloud config get-value project)
GCP_PROJECT_NUMBER=$(gcloud projects list --filter="project_id=${GCP_PROJECT_ID}" --format='value(project_number)')
GCP_REGION=$(gcloud config get compute/region)
SERVICE_NAME="properapp"

GITHUB_ACTIONS_SA="github-actions"
GITHUB_ACTIONS_SA_ID="${GITHUB_ACTIONS_SA}@${GCP_PROJECT_ID}.iam.gserviceaccount.com"

CLOUD_RUN_SA="${SERVICE_NAME}"
CLOUD_RUN_SA_ID="${CLOUD_RUN_SA}@${GCP_PROJECT_ID}.iam.gserviceaccount.com"

echo "Go to https://github.com/${GITHUB_REPOSITORY}/settings/variables/actions and set the following variables:"
echo "GCP_PROJECT_ID = ${GCP_PROJECT_ID}"
echo "GCP_PROJECT_NUMBER = ${GCP_PROJECT_NUMBER}"
echo "GCP_REGION = ${GCP_REGION}"
echo "SERVICE_NAME = ${SERVICE_NAME}"

read -rp "Continue? [y/N] "
[[ ${REPLY} =~ ^[yY] ]] || { echo "Ok, bye"; exit 0; }

# create a service account for the cloud run instance

echo "🔄 Checking for service account ${GITHUB_ACTIONS_SA_ID} ..."
if gcloud iam service-accounts describe "${GITHUB_ACTIONS_SA_ID}" >/dev/null 2>&1; then
  echo "Service account ${GITHUB_ACTIONS_SA_ID} already exists"
else
  gcloud iam service-accounts create "${GITHUB_ACTIONS_SA}" --display-name "${GITHUB_ACTIONS_SA}" --description "Used by GitHub Actions"
fi

echo "🔄 Checking for workload identity pool github-pool ..."
if gcloud iam workload-identity-pools describe "github-pool" --project="${GCP_PROJECT_ID}" --location="global" >/dev/null 2>&1; then
  echo "Workload identity pool github-pool already exists"
else
  gcloud iam workload-identity-pools create "github-pool" --project="${GCP_PROJECT_ID}" --location="global"
fi

echo "🔄 Checking for workload identity provider github-provider ..."
if gcloud iam workload-identity-pools providers describe "github-provider" --project="${GCP_PROJECT_ID}" --location="global" --workload-identity-pool="github-pool" >/dev/null 2>&1; then
  echo "Workload identity provider github-provider already exists"
else
  # see https://console.cloud.google.com/iam-admin/workload-identity-pools/pool/github-pool/provider/github-provider
  gcloud iam workload-identity-pools providers create-oidc "github-provider" --project="${GCP_PROJECT_ID}" --location="global" --workload-identity-pool="github-pool" \
    --display-name="github-provider" \
    --attribute-mapping="google.subject=assertion.sub,attribute.actor=assertion.actor,attribute.repository=assertion.repository" \
    --issuer-uri="https://token.actions.githubusercontent.com"
fi

# basic roles required by workload-identity-federation
# see https://docs.github.com/en/actions/deployment/security-hardening-your-deployments/about-security-hardening-with-openid-connect#example-subject-claims

# add current repository to the workload-identity-pool

echo "🔄 Adding IAM policy binding for ${GITHUB_ACTIONS_SA_ID} to allow workload identity federation from repository ${GITHUB_REPOSITORY} ..."
gcloud iam service-accounts add-iam-policy-binding "${GITHUB_ACTIONS_SA_ID}" \
  --project="${GCP_PROJECT_ID}" \
  --role="roles/iam.workloadIdentityUser" \
  --member="principalSet://iam.googleapis.com/projects/${GCP_PROJECT_NUMBER}/locations/global/workloadIdentityPools/github-pool/attribute.repository/${GITHUB_REPOSITORY}" >/dev/null

# create docker repository if missing

echo "🔄 Checking for Artifact Registry 'docker' repository in region ${GCP_REGION} ..."
if gcloud artifacts repositories describe "docker" --location="${GCP_REGION}" >/dev/null 2>&1; then
  echo "Artifact Registry 'docker' repository already exists in region ${GCP_REGION}"
else
  gcloud artifacts repositories create "docker" --repository-format=docker --location="${GCP_REGION}"
fi

# other roles required by the current project

echo "🔄 Adding IAM policy bindings for ${GITHUB_ACTIONS_SA_ID} for Artifact Registry and Cloud Run ..."
gcloud projects add-iam-policy-binding "${GCP_PROJECT_ID}" \
  --role="roles/artifactregistry.createOnPushWriter" \
  --member="serviceAccount:${GITHUB_ACTIONS_SA_ID}" >/dev/null

echo "🔄 Adding IAM policy binding for ${GITHUB_ACTIONS_SA_ID} for Cloud Run source developer ..."
gcloud projects add-iam-policy-binding "${GCP_PROJECT_ID}" \
  --role="roles/run.sourceDeveloper" \
  --member="serviceAccount:${GITHUB_ACTIONS_SA_ID}" >/dev/null

# prepare the service-account used by the cloud run instance

echo "🔄 Checking for service account ${CLOUD_RUN_SA_ID} ..."
if gcloud iam service-accounts describe "${CLOUD_RUN_SA_ID}" >/dev/null 2>&1; then
  echo "Service account ${CLOUD_RUN_SA_ID} already exists"
else
  gcloud iam service-accounts create "${CLOUD_RUN_SA}" --display-name "${CLOUD_RUN_SA}" --description "Used by Cloud Run"
fi

echo "🔄 Adding IAM policy binding to allow ${GITHUB_ACTIONS_SA_ID} to impersonate ${CLOUD_RUN_SA_ID} ..."
gcloud iam service-accounts add-iam-policy-binding "${CLOUD_RUN_SA_ID}" \
  --project="${GCP_PROJECT_ID}" \
  --role="roles/iam.serviceAccountUser" \
  --member="serviceAccount:${GITHUB_ACTIONS_SA_ID}" >/dev/null

echo "🔄 Adding IAM policy binding for ${CLOUD_RUN_SA_ID} to invoke Cloud Run services ..."
gcloud projects add-iam-policy-binding "${GCP_PROJECT_ID}" \
  --role="roles/run.invoker" \
  --member="serviceAccount:${CLOUD_RUN_SA_ID}" >/dev/null

echo "🔄 Adding IAM policy binding for ${CLOUD_RUN_SA_ID} to access Secret Manager ..."
gcloud projects add-iam-policy-binding "${GCP_PROJECT_ID}" \
  --role="roles/secretmanager.secretAccessor" \
  --member="serviceAccount:${CLOUD_RUN_SA_ID}" >/dev/null

# create a dummy instance (cicd can only update)

echo "🔄 Creating initial Cloud Run service ${SERVICE_NAME} ..."
gcloud run deploy "${SERVICE_NAME}" \
  --service-account "${CLOUD_RUN_SA_ID}" \
  --region "${GCP_REGION}" \
  --image "gcr.io/cloudrun/hello" \
  --platform managed \
  --allow-unauthenticated \
  --memory "128Mi" \
  --timeout "30" \
  --max-instances 1 \
  --min-instances 0 \
  --port "8000"

# ...and you're done

echo "Done ✌️"
