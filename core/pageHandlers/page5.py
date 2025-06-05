"""
Page 5 Handler - Rating Grid
"""

import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException

from .basePage import BasePage
from core.utils.pageUtils import ElementClickHelper
from utils.logger import get_logger

logger = get_logger(__name__)


class Page5Handler(BasePage):
    """Handle page 5 - Rating grid"""
    
    def process(self):
        """Process page 5 - Filling Rating Grid"""
        try:
            self.log_start()
            
            # Wait for the rating grid table to be present
            WebDriverWait(self.driver, self.config.DEFAULT_TIMEOUT).until(
                EC.presence_of_element_located((By.XPATH, "//table[contains(@id, 'survey_options')]"))
            )
            
            # Find all radio buttons with the specified rating value
            rating_value = self.data['worth_rating']
            rating_buttons = WebDriverWait(self.driver, self.config.DEFAULT_TIMEOUT).until(
                EC.presence_of_all_elements_located((By.XPATH, f"//input[@type='radio' and @value='{rating_value}']"))
            )
            
            # Click each rating option
            self._select_all_ratings(rating_buttons)
            
            self.utils.click_next_button()
            self.log_complete()
            
        except Exception as e:
            self.handle_error(e)
    
    def _select_all_ratings(self, rating_buttons):
        """Select all rating options"""
        for i, button in enumerate(rating_buttons):
            try:
                button_id = button.get_attribute('id')
                if not button_id:
                    logger.warning(f"Button {i+1} has no ID, skipping")
                    continue
                
                if ElementClickHelper.safe_click(self.driver, button_id, self.config.SHORT_TIMEOUT):
                    logger.info(f"Selected rating for question {i+1}: {button_id}")
                else:
                    logger.warning(f"Failed to select option for question {i+1}")
                
            except StaleElementReferenceException:
                logger.warning(f"Stale element reference for question {i+1}, skipping")
                continue
            except Exception as e:
                logger.error(f"Error selecting question {i+1}: {e}")
                continue