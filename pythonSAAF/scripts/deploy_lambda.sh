#!/bin/bash
# AWS Lambda Deployment Script
# Usage: ./deploy_lambda.sh [FUNCTION_NAME]

# Configuration
FUNCTION_NAME="${1:-ProcessS3Uploads}"  # Default Lambda function name
RUNTIME="python3.13"                    # Lambda runtime
HANDLER="handler.lambda_handler"        # Lambda handler
MEMORY_SIZE=512                         # Memory size in MB
TIMEOUT=3                               # Timeout in seconds
SRC_DIR="/home/joser27/Documents/code/talkify/pythonSAAF/src"
DEPLOY_ZIP="lambda_function.zip"        # Deployment package name

# Create deployment package
echo "📦 Creating deployment package..."
if [ -f "$DEPLOY_ZIP" ]; then
    rm "$DEPLOY_ZIP"
fi
zip -r "$DEPLOY_ZIP" "$SRC_DIR" -x "**/__pycache__/*" > /dev/null
echo "✅ Deployment package created: $DEPLOY_ZIP"

# Deploy to AWS Lambda
echo "🚀 Deploying to Lambda function: $FUNCTION_NAME..."
aws lambda update-function-code \
    --function-name "$FUNCTION_NAME" \
    --zip-file "fileb://$DEPLOY_ZIP"

echo "⚙️ Updating Lambda configuration..."
aws lambda update-function-configuration \
    --function-name "$FUNCTION_NAME" \
    --handler "$HANDLER" \
    --runtime "$RUNTIME" \
    --memory-size "$MEMORY_SIZE" \
    --timeout "$TIMEOUT"

# Cleanup
echo "🧹 Cleaning up..."
rm "$DEPLOY_ZIP"

echo "✅ Deployment complete!"
echo "Function: $FUNCTION_NAME | Handler: $HANDLER | Memory: ${MEMORY_SIZE}MB | Timeout: ${TIMEOUT}s"