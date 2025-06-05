"""
Page 8 Handler - Membership Status Selection (Yes/No)
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


class Page8Handler(BasePage):
    """Handle page 8 - Membership status selection (Yes/No)"""
    
    def process(self):
        """Process page 8 - Selecting Membership Status"""
        try:
            self.log_start()
            
            # Wait for the radio button group to be present
            radio_group = WebDriverWait(self.driver, self.config.DEFAULT_TIMEOUT).until(
                EC.presence_of_element_located((By.XPATH, "//div[@data-role='controlgroup'][@class='ui-corner-all ui-controlgroup ui-controlgroup-vertical']"))
            )
            
            # Get the membership status from data
            membership_status = self.data.get('is_membership', 'NO')
            logger.debug(f"Target membership status: {membership_status}")
            
            # Select the membership status
            self._select_membership_status(membership_status)
        
            
            self.utils.click_next_button()
            self.log_complete()
            
        except TimeoutException:
            logger.error("Timeout waiting for membership status options")
            raise
        except Exception as e:
            self.handle_error(e)
    
    def _select_membership_status(self, membership_status):
        """Select the membership status radio button"""
        try:
            # Map the status to the expected label text
            target_text = self.config.MEMBERSHIP_MAPPING.get(membership_status.upper())
            if not target_text:
                raise ValueError(f"Invalid membership status: {membership_status}")
            
            # Find the radio button by its label text
            target_radio = None
            
            # Try multiple strategies to find the radio button
            strategies = [
                f"//span[@class='ui-btn-text'][text()='{target_text}']/../../input[@type='radio']",
                f"//label[contains(., '{target_text}')]/preceding-sibling::input[@type='radio']",
                f"//input[@type='radio']/following-sibling::label[contains(., '{target_text}')]/../input"
            ]
            
            for i, strategy in enumerate(strategies):
                try:
                    target_radio = WebDriverWait(self.driver, self.config.SHORT_TIMEOUT).until(
                        EC.presence_of_element_located((By.XPATH, strategy))
                    )
                    logger.debug(f"Found radio button using strategy {i+1}")
                    break
                except TimeoutException:
                    continue
            
            if not target_radio:
                raise Exception(f"Could not locate radio button for membership status: {target_text}")
            
            # Get the radio button ID
            radio_id = target_radio.get_attribute('id')
            logger.debug(f"Found target membership radio button with ID: {radio_id}")
            
            # Use the ElementClickHelper to click the radio button
            if ElementClickHelper.safe_click(self.driver, radio_id, self.config.SHORT_TIMEOUT):
                logger.info(f"Successfully selected membership status: {membership_status} ({target_text})")
            else:
                # Fallback strategies
                try:
                    # Try clicking the label instead
                    label = self.driver.find_element(By.XPATH, f"//label[@for='{radio_id}']")
                    label.click()
                    logger.info(f"Selected membership status using label click: {membership_status}")
                except Exception:
                    # Last resort: JavaScript click on the radio button
                    self.driver.execute_script("arguments[0].click();", target_radio)
                    logger.info(f"Selected membership status using JavaScript: {membership_status}")
                    
        except ValueError as ve:
            logger.error(f"Invalid membership status value: {ve}")
            raise
        except Exception as e:
            logger.error(f"Error selecting membership status: {e}")
            raise