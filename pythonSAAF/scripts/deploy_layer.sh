#!/bin/bash
# Lambda Layer Deployment Script
# Usage: ./deploy_layer.sh [LAYER_NAME] [FUNCTION_NAME]

# Configuration
LAYER_NAME="${1:-pdf-deps}"  # Default layer name
FUNCTION_NAME="${2:-ProcessS3Uploads}"  # Default Lambda function
PYTHON_VERSION="python3.13"  # Must match Lambda runtime
DEPENDENCIES=("PyPDF2")  # Add other packages as needed

# Create temporary directory
WORK_DIR=$(mktemp -d)
trap 'rm -rf "$WORK_DIR"' EXIT

echo "📦 Installing dependencies..."
mkdir -p "$WORK_DIR/python"
pip install "${DEPENDENCIES[@]}" -t "$WORK_DIR/python" --quiet

echo "🛠️ Creating layer package..."
(cd "$WORK_DIR" && zip -r layer.zip python > /dev/null)

echo "🚀 Publishing layer..."
LAYER_ARN=$(aws lambda publish-layer-version \
    --layer-name "$LAYER_NAME" \
    --description "Dependencies: ${DEPENDENCIES[*]}" \
    --zip-file "fileb://$WORK_DIR/layer.zip" \
    --compatible-runtimes "$PYTHON_VERSION" \
    --query 'LayerVersionArn' \
    --output text)

echo "🔗 Attaching to Lambda..."
aws lambda update-function-configuration \
    --function-name "$FUNCTION_NAME" \
    --layers "$LAYER_ARN" \
    --output text  # ← Clean output

echo -e "\n✅ Success!\nLayer ARN: $LAYER_ARN\nAttached to: $FUNCTION_NAME"