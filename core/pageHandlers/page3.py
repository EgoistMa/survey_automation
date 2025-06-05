"""
Page 3 Handler - Location Selection
"""

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC

from .basePage import BasePage
from utils.logger import get_logger

logger = get_logger(__name__)


class Page3Handler(BasePage):
    """Handle page 3 - Location selection"""

    def __init__(self, driver, data, config=None, location="Chatswood"):
        """Initialize with submit flag"""
        super().__init__(driver, data, config)
        self.location = location
    
    def process(self):
        """Process page 3 - Selecting Location"""
        try:
            self.log_start()
            
            # Wait for dropdown to load
            element = WebDriverWait(self.driver, self.config.DEFAULT_TIMEOUT).until(
                EC.presence_of_element_located((By.XPATH, "//*[starts-with(@id, 'QuestionAnswers_')]"))
            )
            
            location_value = self.config.LOCATION_MAPPING.get(self.location)
            if not location_value:
                raise ValueError(f"Invalid location: {self.location}")

            # Select location
            dropdown_element = element.find_element(By.XPATH, "//*[starts-with(@id, 'QuestionAnswers_')]")
            location_select = Select(dropdown_element)
            location_select.select_by_value(location_value)
            logger.info(f"Location selected: {self.location}")

            self.utils.click_next_button()
            self.log_complete()
            
        except Exception as e:
            self.handle_error(e)