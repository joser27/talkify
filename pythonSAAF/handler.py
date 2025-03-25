#cloud_function(platforms=[Platform.AWS], memory=512, config=config)
def yourFunction(event, context):
    import json
    from Inspector import Inspector
    import PyPDF2
    import io
    import os
    import logging
    
    # Set up logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger()
    
    inspector = Inspector()
    inspector.inspectMinimal()

    def extract_text_from_pdf(pdf_bytes):
        """Improved text extraction with error handling"""
        try:
            text = ""
            pdf = PyPDF2.PdfReader(io.BytesIO(pdf_bytes))
            
            # Improved extraction with page number tracking
            for i, page in enumerate(pdf.pages, 1):
                page_text = page.extract_text()
                if page_text:
                    text += f"\n--- PAGE {i} ---\n{page_text}\n"
                else:
                    text += f"\n--- PAGE {i} (No text detected) ---\n"
                    logger.warning(f"No text extracted from page {i}")
            
            return text.strip()
        except Exception as e:
            logger.error(f"PDF extraction failed: {str(e)}")
            raise

    try:
        # Determine if running locally or in AWS
        is_local = 'local_file_path' in event
        
        if is_local:
            # Local file processing
            file_path = event['local_file_path']
            logger.info(f"Processing local file: {file_path}")
            
            if not file_path.lower().endswith('.pdf'):
                raise ValueError("Local testing only supports PDF files")
                
            with open(file_path, 'rb') as f:
                file_content = f.read()
                
            text = extract_text_from_pdf(file_content)
            inspector.addAttribute("source", "local_file")
            
        else:
            # AWS S3 processing
            import boto3
            s3 = boto3.client('s3')
            record = event['Records'][0]['s3']
            bucket = record['bucket']['name']
            key = record['object']['key']
            logger.info(f"Processing S3 file: s3://{bucket}/{key}")
            
            if not key.lower().endswith('.pdf'):
                raise ValueError("Only PDF files are supported")
                
            file_obj = s3.get_object(Bucket=bucket, Key=key)
            file_content = file_obj['Body'].read()
            
            text = extract_text_from_pdf(file_content)
            inspector.addAttribute("source", "s3")
            
            # Save extracted text back to S3 #TODO: Add this to the config
            if 'SAVE_TO_S3' in os.environ and os.environ['SAVE_TO_S3'].lower() == 'true':
                text_key = f"extracted-text/{os.path.splitext(key)[0]}.txt"
                s3.put_object(
                    Bucket=bucket,
                    Key=text_key,
                    Body=text.encode('utf-8'),
                    ContentType='text/plain'
                )
                inspector.addAttribute("output_location", f"s3://{bucket}/{text_key}")
        
        # Add results to inspection
        inspector.addAttribute("text_length", len(text))
        inspector.addAttribute("page_count", len(PyPDF2.PdfReader(io.BytesIO(file_content)).pages))
        inspector.addAttribute("message", "PDF processed successfully")
        
        # For large texts, include sample in attributes
        sample_length = min(500, len(text))
        inspector.addAttribute("text_sample", text[:sample_length] + ("..." if len(text) > sample_length else ""))
        
    except Exception as e:
        logger.error(f"Processing failed: {str(e)}")
        inspector.addAttribute("error", str(e))
        inspector.addAttribute("message", "PDF processing failed")
        raise  # Re-raise for AWS Lambda error handling
    
    finally:
        inspector.inspectAllDeltas()
    
    return inspector.finish()