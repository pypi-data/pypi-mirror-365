import logging

def setup_logging():
    # Configure logging settings
    logging.basicConfig(
        level=logging.INFO,  # Set the logging level to INFO to ignore DEBUG messages
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
