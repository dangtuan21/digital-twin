#!/bin/bash

# Automated build and packaging for AWS Lambda (Python 3.12, Amazon Linux)
set -e

BACKEND_DIR="$(cd "$(dirname "$0")" && pwd)"
LAMBDA_PACKAGE="$BACKEND_DIR/lambda-package"
DEPLOYMENT_ZIP="$BACKEND_DIR/lambda-deployment.zip"

# Clean previous builds
rm -rf "$LAMBDA_PACKAGE" "$DEPLOYMENT_ZIP"
mkdir -p "$LAMBDA_PACKAGE"

# Build dependencies in Amazon Linux Docker
DOCKER_IMAGE="public.ecr.aws/lambda/python:3.12"
docker run --rm --platform linux/x86_64 --entrypoint bash -v "$BACKEND_DIR":/var/task $DOCKER_IMAGE -c "pip install -r /var/task/requirements.txt -t /var/task/lambda-package"

# Verify pydantic_core native binary exists
PYDANTIC_CORE_SO=$(find "$LAMBDA_PACKAGE/pydantic_core" -name "_pydantic_core*.so" 2>/dev/null || true)
if [[ -z "$PYDANTIC_CORE_SO" ]]; then
  echo "Error: pydantic_core native binary not found in package. Lambda will fail to import." >&2
  exit 1
else
  echo "Found pydantic_core native binary: $PYDANTIC_CORE_SO"
  # Print architecture info for debugging
  file "$PYDANTIC_CORE_SO"
fi

# Zip dependencies
cd "$LAMBDA_PACKAGE"
zip -r "$DEPLOYMENT_ZIP" .
cd "$BACKEND_DIR"

# Add test handler for pydantic_core import
cp "$BACKEND_DIR/test_lambda_pydantic_core.py" "$LAMBDA_PACKAGE/lambda_handler.py"
cd "$LAMBDA_PACKAGE"
zip -g "$DEPLOYMENT_ZIP" lambda_handler.py
cd "$BACKEND_DIR"

# Output result
if [ -f "$DEPLOYMENT_ZIP" ]; then
  echo "Lambda deployment package created: $DEPLOYMENT_ZIP"
else
  echo "Error: Deployment zip not created." >&2
  exit 1
fi
