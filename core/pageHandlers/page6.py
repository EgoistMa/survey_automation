"""
Page 6 Handler - Feedback Text Input
"""

import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

from .basePage import BasePage
from utils.logger import get_logger

logger = get_logger(__name__)


class Page6Handler(BasePage):
    """Handle page 6 - Feedback text input"""
    
    def process(self):
        """Process page 6 - Entering Feedback Text"""
        try:
            self.log_start()
            
            # Wait for the textarea to be present
            textarea = WebDriverWait(self.driver, self.config.DEFAULT_TIMEOUT).until(
                EC.presence_of_element_located((By.XPATH, "//textarea[starts-with(@id, 'QuestionAnswers_')]"))
            )
            
            # Get the textarea ID for logging
            textarea_id = textarea.get_attribute('id')
            logger.debug(f"Found textarea with ID: {textarea_id}")
            
            # Clear any existing text and input the feedback
            textarea.clear()
            feedback_text = self.data.get('feedback_text', ' ')
            textarea.send_keys(feedback_text)
            
            logger.info(f"Feedback text entered: '{feedback_text}' (length: {len(feedback_text)})")
            
            # Optional: Add a small delay to ensure text is properly entered
            time.sleep(self.config.CLICK_DELAY)
            
            self.utils.click_next_button()
            self.log_complete()
            
        except TimeoutException:
            logger.error("Timeout waiting for feedback textarea")
            raise
        except Exception as e:
            self.handle_error(e)