import pywhatkit as kit
import time
import logging
from datetime import datetime

# Initialize logger for WhatsApp messaging
def initialize_whatsapp_logger():
    """Initializes a logger for WhatsApp messaging.

    Returns:
        Logger object for WhatsApp message tracking.
    """
    log_filename = f"whatsapp_logs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    log_path = f'logs/{log_filename}'
    
    logger = logging.getLogger('whatsapp')
    logger.setLevel(logging.INFO)
    
    # Create file handler for logging
    file_handler = logging.FileHandler(log_path)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    return logger

def send_whatsapp_message(phone_number, message, logger=None):
    """Sends a WhatsApp message using pywhatkit.

    Args:
        phone_number (str): The recipient's WhatsApp phone number in international format (e.g., +123456789).
        message (str): The message to be sent.
        logger: Logger object to log message status (default is None).

    Returns:
        bool: True if the message is sent successfully, False otherwise.
    """
    if logger is None:
        logger = initialize_whatsapp_logger()

    try:
        logger.info(f"Sending WhatsApp message to {phone_number}: {message}")
        
        # Send message instantly via pywhatkit
        kit.sendwhatmsg_instantly(phone_number, message)
        time.sleep(1)  # Time delay to ensure message is sent
        
        logger.info(f"Message sent to {phone_number}: {message}")
        return True
    except Exception as e:
        logger.error(f"Failed to send WhatsApp message to {phone_number}: {str(e)}")
        return False

# Example usage
if __name__ == "__main__":
    # Test message
    phone_number = "+123456789"  # Replace with recipient's number
    message = "Hello from OpenAI Assistant!"
    
    logger = initialize_whatsapp_logger()
    send_whatsapp_message(phone_number, message, logger)
