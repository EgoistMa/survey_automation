"""
Page 1 Handler - Start Survey
"""

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from .basePage import BasePage
from utils.logger import get_logger

logger = get_logger(__name__)


class Page1Handler(BasePage):
    """Handle page 1 - Start Survey"""
    
    def process(self):
        """Process page 1 - Start Survey"""
        try:
            self.log_start()
            
            # Navigate to survey URL
            self.driver.get(self.config.SURVEY_URL)
            self.utils.wait_for_page_load()
            
            # Click start button
            start_button = WebDriverWait(self.driver, self.config.DEFAULT_TIMEOUT).until(
                EC.element_to_be_clickable((By.ID, "ibStartButton"))
            )
            start_button.click()
            logger.info("Clicked 'Start Survey' button")
            
            self.log_complete()
            
        except Exception as e:
            self.handle_error(e)