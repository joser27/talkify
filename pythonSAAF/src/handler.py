import json
import boto3
import PyPDF2
import io
import logging

# Set up logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    logger.info("Lambda function started")
    
    try:
        # Extract bucket name and object key from the S3 event
        record = event['Records'][0]['s3']
        bucket = record['bucket']['name']
        key = record['object']['key']
        logger.info(f"Processing file: s3://{bucket}/{key}")
        
        # Initialize S3 client
        s3 = boto3.client('s3')
        
        # Retrieve the PDF file from S3
        file_obj = s3.get_object(Bucket=bucket, Key=key)
        file_content = file_obj['Body'].read()
        
        # Open the PDF file
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(file_content))
        
        # Extract metadata
        metadata = pdf_reader.metadata
        num_pages = len(pdf_reader.pages)
        
        # Prepare response
        response = {
            'Metadata': metadata,
            'Number of Pages': num_pages
        }
        
        logger.info(f"Extracted Metadata: {response}")
        return {
            'statusCode': 200,
            'body': json.dumps(response)
        }
        
    except Exception as e:
        logger.error(f"Error processing file: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
