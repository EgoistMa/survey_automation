"""
Page 7 Handler - Recommendation Rating (0-10 scale)
"""

import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

from .basePage import BasePage
from core.utils.pageUtils import ElementClickHelper
from utils.logger import get_logger

logger = get_logger(__name__)


class Page7Handler(BasePage):
    """Handle page 7 - Recommendation rating (0-10 scale)"""
    
    def process(self):
        """Process page 7 - Selecting Recommendation Rating"""
        try:
            self.log_start()
            
            # Wait for the radio button group to be present
            radio_group = WebDriverWait(self.driver, self.config.DEFAULT_TIMEOUT).until(
                EC.presence_of_element_located((By.XPATH, "//div[@data-role='controlgroup'][@data-type='horizontal']"))
            )
            
            # Get the recommendation rating from data (default to 10)
            recommend_rating = self.data.get('recommend_rating', 10)
            logger.debug(f"Target recommendation rating: {recommend_rating}")
            
            # Find and click the radio button with the target value
            self._select_recommendation_rating(recommend_rating)
            
            self.utils.click_next_button()
            self.log_complete()
            
        except TimeoutException:
            logger.error("Timeout waiting for recommendation rating options")
            raise
        except Exception as e:
            self.handle_error(e)
    
    def _select_recommendation_rating(self, recommend_rating):
        """Select the recommendation rating"""
        try:
            # Find the radio button with the target value
            # The pattern is: value="XXXXX:rating" where rating is the actual number
            target_radio = WebDriverWait(self.driver, self.config.SHORT_TIMEOUT).until(
                EC.presence_of_element_located((By.XPATH, f"//input[@type='radio' and contains(@value, ':{recommend_rating}')]"))
            )
            
            # Get the radio button ID
            radio_id = target_radio.get_attribute('id')
            logger.debug(f"Found target radio button with ID: {radio_id}")
            
            # Use the ElementClickHelper to click the radio button
            if ElementClickHelper.safe_click(self.driver, radio_id, self.config.SHORT_TIMEOUT):
                logger.info(f"Successfully selected recommendation rating: {recommend_rating}")
            else:
                # Fallback: try to click by value directly
                try:
                    value_attr = target_radio.get_attribute('value')
                    radio_by_value = self.driver.find_element(By.XPATH, f"//input[@type='radio' and @value='{value_attr}']")
                    self.driver.execute_script("arguments[0].click();", radio_by_value)
                    logger.info(f"Selected recommendation rating using fallback method: {recommend_rating}")
                except Exception as fallback_error:
                    logger.error(f"All methods failed to select recommendation rating: {fallback_error}")
                    raise
                    
        except Exception as e:
            logger.error(f"Error selecting recommendation rating: {e}")
            raise