import json
import boto3
import PyPDF2
import io
import logging
import urllib.parse
from botocore.exceptions import ClientError

# Set up logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def generate_audio_and_url(text, bucket_name, key_base):
    """Generate audio using Polly and create a presigned URL."""
    try:
        polly = boto3.client('polly')
        s3 = boto3.client('s3')
        
        # Generate audio using Polly
        response = polly.start_speech_synthesis_task(
            Engine='neural',
            LanguageCode='en-US',
            OutputFormat='mp3',
            OutputS3BucketName=bucket_name,
            OutputS3KeyPrefix=f"audio/{key_base}",
            Text=text,
            VoiceId='Matthew'
        )
        
        # Get the task ID
        task_id = response['SynthesisTask']['TaskId']
        output_key = f"audio/{key_base}/{task_id}.mp3"
        
        # Generate presigned URL (valid for 1 hour)
        presigned_url = s3.generate_presigned_url(
            'get_object',
            Params={
                'Bucket': bucket_name,
                'Key': output_key
            },
            ExpiresIn=3600
        )
        
        return {
            'audio_key': output_key,
            'task_id': task_id,
            'presigned_url': presigned_url
        }
        
    except ClientError as e:
        logger.error(f"Error generating audio: {str(e)}")
        raise

def lambda_handler(event, context):
    logger.info("Lambda function started")
    logger.info(f"Received event: {json.dumps(event)}")
    
    try:
        # Extract bucket name and object key from the S3 event
        record = event['Records'][0]['s3']
        bucket = record['bucket']['name']
        key = record['object']['key']
        logger.info(f"Processing file: s3://{bucket}/{key}")
        
        # URL-decode the object key to handle spaces and special characters
        decoded_key = urllib.parse.unquote_plus(key)
        logger.info(f"Decoded object key: {decoded_key}")
        
        # Skip non-PDF files to avoid re-processing .txt files
        if not decoded_key.lower().endswith('.pdf'):
            logger.info(f"Skipping non-PDF file: {decoded_key}")
            return {
                'statusCode': 200,
                'body': json.dumps({'message': 'File is not a PDF. Skipping.'})
            }
        
        # Initialize S3 client
        s3 = boto3.client('s3')
        
        # Retrieve the PDF file from S3
        file_obj = s3.get_object(Bucket=bucket, Key=decoded_key)
        file_content = file_obj['Body'].read()
        
        # Open the PDF file
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(file_content))
        
        # Extract and sanitize metadata
        metadata = {}
        for key, value in pdf_reader.metadata.items():
            if hasattr(value, 'get_object'):
                metadata[key] = str(value.get_object())  # Convert IndirectObject to string
            else:
                metadata[key] = str(value) if value else None
        
        num_pages = len(pdf_reader.pages)
        
        # Extract text from each page
        text_content = []
        for page_num, page in enumerate(pdf_reader.pages, start=1):
            page_text = page.extract_text()
            if page_text:
                text_content.append(f"\n--- PAGE {page_num} ---\n{page_text}")
            else:
                text_content.append(f"\n--- PAGE {page_num} (No text detected) ---")
                logger.warning(f"No text extracted from page {page_num}")
        
        # Join the extracted text into a single string
        full_text = "\n".join(text_content).strip()
        
        # Save extracted text to the extracted-text/ folder in S3
        save_text_to_s3(bucket, decoded_key, full_text)

        # Generate audio and get presigned URL
        key_base = decoded_key.replace('.pdf', '')
        audio_info = generate_audio_and_url(full_text, bucket, key_base)

        # Prepare response with metadata, page count, and audio URL
        response = {
            'Metadata': metadata,
            'Number of Pages': num_pages,
            'Text Saved To': f"s3://{bucket}/extracted-text/{decoded_key.replace('.pdf', '.txt')}",
            'Audio': {
                'TaskId': audio_info['task_id'],
                'AudioKey': audio_info['audio_key'],
                'PreSignedUrl': audio_info['presigned_url']
            }
        }
        
        logger.info(f"Extracted Metadata, Text Saved, and Audio Generated: {response}")
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

def save_text_to_s3(bucket_name, key, text):
    """Save extracted text to S3 as a .txt file."""
    s3 = boto3.client('s3')
    
    # Create the new key for the extracted text
    text_key = f"extracted-text/{key.replace('.pdf', '.txt')}"
    
    # Upload the extracted text to S3
    s3.put_object(
        Bucket=bucket_name,
        Key=text_key,
        Body=text.encode('utf-8'),
        ContentType='text/plain'
    )
    logger.info(f"Extracted text saved to s3://{bucket_name}/{text_key}")
