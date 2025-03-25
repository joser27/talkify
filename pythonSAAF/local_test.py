import json
import logging
import os
from handler import yourFunction

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
        result = yourFunction(event, None)
        
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
    import sys
    import argparse
    
    setup_logging()
    
    parser = argparse.ArgumentParser()
    parser.add_argument("pdf_file", help="Path to PDF file for testing")
    parser.add_argument("--save", action="store_true", help="Save extracted text to file")
    args = parser.parse_args()
    
    if not os.path.exists(args.pdf_file):
        logging.error(f"File not found: {args.pdf_file}")
        sys.exit(1)
        
    test_pdf_processing(args.pdf_file, save_output=args.save)