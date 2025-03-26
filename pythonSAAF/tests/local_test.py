import json
import logging
import os
from pythonSAAF.src.handler import lambda_handler


def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

def test_pdf_processing(file_path, save_output=False):
    """Test PDF processing with detailed output"""
    logger = logging.getLogger()
    logger.info(f"\n{' Starting Test ':=^40}")
    
    # Create test event
    event = {"local_file_path": file_path}
    
    try:
        # Process the file
        result = lambda_handler(event, None)
        
        # Display results
        logger.info("\nProcessing Results:")
        print(json.dumps({k: v for k, v in result.items() if k != 'text'}, indent=2))
        
        # Save full text if requested
        if save_output and 'text' in result:
            output_file = f"{file_path}.extracted.txt"
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(result['text'])
            logger.info(f"Full text saved to: {output_file}")
            
        return result
        
    except Exception as e:
        logger.error(f"Test failed: {str(e)}")
        raise

if __name__ == "__main__":
    setup_logging()
    
    # Hard-coded file path
    file_path = "/home/joser27/Documents/code/talkify/pythonSAAF/tests/test_data/sample.pdf"
    save_output = True  # Set to True if you want to save the extracted text
    
    if not os.path.exists(file_path):
        logging.error(f"File not found: {file_path}")
        exit(1)
        
    test_pdf_processing(file_path, save_output=save_output)
