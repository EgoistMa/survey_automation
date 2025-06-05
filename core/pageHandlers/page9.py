"""
Page 9 Handler - Next Visit Timing Selection
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


class Page9Handler(BasePage):
    """Handle page 9 - Next visit timing selection"""
    
    def process(self):
        """Process page 9 - Selecting Next Visit Timing"""
        try:
            self.log_start()
            
            # Wait for the radio button group to be present
            radio_group = WebDriverWait(self.driver, self.config.DEFAULT_TIMEOUT).until(
                EC.presence_of_element_located((By.XPATH, "//div[@data-role='controlgroup'][@class='ui-corner-all ui-controlgroup ui-controlgroup-vertical']"))
            )
            
            # Get the next visit timing from data
            next_visit = self.data.get('next_visit', 'Today')
            logger.debug(f"Target next visit timing: {next_visit}")
            
            # Select the next visit timing
            self._select_next_visit_timing(next_visit)
            
            # Small delay to ensure selection is registered
            time.sleep(self.config.CLICK_DELAY)
            
            self.utils.click_next_button()
            self.log_complete()
            
        except TimeoutException:
            logger.error("Timeout waiting for next visit timing options")
            raise
        except Exception as e:
            self.handle_error(e)
    
    def _select_next_visit_timing(self, next_visit):
        """Select the next visit timing radio button"""
        try:
            # Validate the next visit option
            if next_visit not in self.config.NEXT_VISIT_MAPPING:
                logger.warning(f"Invalid next visit option: {next_visit}, defaulting to 'Today'")
                next_visit = 'Today'
            
            target_text = self.config.NEXT_VISIT_MAPPING[next_visit]
            
            # Find the radio button by its exact label text
            target_radio = None
            
            # Try multiple XPath strategies to find the radio button
            xpath_strategies = [
                f"//span[@class='ui-btn-text'][text()='{target_text}']/../../input[@type='radio']",
                f"//label[contains(., '{target_text}')]/preceding-sibling::input[@type='radio']",
                f"//input[@type='radio']/following-sibling::label[contains(., '{target_text}')]/../input"
            ]
            
            for i, xpath in enumerate(xpath_strategies):
                try:
                    target_radio = WebDriverWait(self.driver, self.config.SHORT_TIMEOUT).until(
                        EC.presence_of_element_located((By.XPATH, xpath))
                    )
                    logger.debug(f"Found radio button using strategy {i+1}")
                    break
                except TimeoutException:
                    continue
            
            if not target_radio:
                raise Exception(f"Could not locate radio button for next visit option: {target_text}")
            
            # Get the radio button ID
            radio_id = target_radio.get_attribute('id')
            logger.debug(f"Found target next visit radio button with ID: {radio_id}")
            
            # Use the ElementClickHelper to click the radio button
            if ElementClickHelper.safe_click(self.driver, radio_id, self.config.SHORT_TIMEOUT):
                logger.info(f"Successfully selected next visit timing: {next_visit}")
            else:
                # Fallback strategies
                try:
                    # Try clicking the associated label
                    label = self.driver.find_element(By.XPATH, f"//label[@for='{radio_id}']")
                    label.click()
                    logger.info(f"Selected next visit using label click: {next_visit}")
                except Exception:
                    # Last resort: JavaScript click
                    self.driver.execute_script("arguments[0].click();", target_radio)
                    logger.info(f"Selected next visit using JavaScript: {next_visit}")
                    
        except Exception as e:
            logger.error(f"Error selecting next visit timing: {e}")
            raise