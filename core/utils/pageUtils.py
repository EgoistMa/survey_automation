"""
Utility functions for page interactions and element manipulation
"""

import time
from datetime import datetime
from typing import Dict, Optional
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, ElementClickInterceptedException

try:
    from utils.logger import get_logger
except ImportError:
    import logging
    def get_logger(name):
        return logging.getLogger(name)

logger = get_logger(__name__)


class SurveyConfig:
    """Configuration constants for the survey"""
    SURVEY_URL = "https://www.yourstarbuckssay.com.au/surveys/8d393fb7-7456-4eba-9834-8f8966035e85/v167/Default.aspx?GUID=81b5bbfe-efa7-426d-9afd-7379b78c7ccc"
    DEFAULT_TIMEOUT = 10
    SHORT_TIMEOUT = 5
    CLICK_DELAY = 0.1
    
    # Mapping dictionaries 
    TIME_MAPPING = {
        "Morning (6am-11am)": "1",
        "Lunch (11am – 2pm)": "2",
        "Afternoon (2pm – 6pm)": "3",
        "Evening (6pm – 11pm)": "4",
    }
    
    STATE_MAPPING = {
        "NSW": "1",
        "QLD": "2",
        "VIC": "3",
        "WA": "4",
    }
    
    LOCATION_MAPPING = {
        "525 George Street": "1",
        "Bondi Junction Westfield": "2",
        "Broadway": "65",
        "Castle Towers": "51",
        "Central Park Mall": "3",
        "Chatswood": "4",
        "Childrens Hospital - Westmead": "5",
        "Darling Square": "47",
        "Eastgardens Westfield": "6",
        "Haymarket (Capitol Square)": "7",
        "Hornsby": "77",
        "Hurstville Westfield": "8",
        "Hyde Park": "9",
        "Macquarie Centre": "10",
        "Manly": "11",
        "Marsden Park (drive thru)": "12",
        "Mt Druitt (drive thru)": "13",
        "North Penrith": "48",
        "Parkline Place": "86",
        "Parramatta Westfield": "14",
        "Penrith Westfield": "15",
        "Queen Victoria Building": "16",
        "The Rocks": "43",
        "Warrawong": "75",
        "Westfield Burwood": "46",
        "Westfield Miranda": "54",
        "York Street / Wynyard Station": "17",
    }
    
    DINING_OPTION_MAPPING = {
        "Purchased for takeaway": 0,
        "Dined in at Starbucks": 1
    }

    MEMBERSHIP_MAPPING = {
        "YES": "Yes",
        "NO": "No"
    }

    NEXT_VISIT_MAPPING = {
        "Today": "Today",
        "Tomorrow": "Tomorrow", 
        "Within the next week": "Within the next week",
        "More than a month from now": "More than a month from now",
        "Never": "Never",
        "Don't know": "Don't know"
    }

    REQUIRED_COLUMNS = [
        'date', 'time_period', 'state', 'location', 'dining_option',
        'worth_rating', 'employees_effort_rating', 'beverage_rating', 'cleanliness_rating',
        'order_accuracy_rating', 'employee_exceed_rating', 'time_rating', 'food_rating',
        'feedback_text', 'recommend_rating', 'is_membership', 'next_visit',
        'name', 'email', 'contact', 'opt_out_draw'
    ]


class ElementClickHelper:
    """Helper class for handling element clicks with different strategies"""
    
    @staticmethod
    def safe_click(driver: webdriver.Chrome, element_id: str, wait_time: int = 5) -> bool:
        """Try multiple click strategies for an element"""
        strategies = [
            lambda: ElementClickHelper._click_parent(driver, element_id, wait_time),
            lambda: ElementClickHelper._click_label(driver, element_id, wait_time),
            lambda: ElementClickHelper._click_javascript(driver, element_id, wait_time),
            lambda: ElementClickHelper._click_direct(driver, element_id, wait_time)
        ]
        
        for i, strategy in enumerate(strategies):
            try:
                if strategy():
                    logger.debug(f"Successfully clicked {element_id} using strategy {i+1}")
                    return True
            except Exception as e:
                logger.debug(f"Strategy {i+1} failed for {element_id}: {e}")
                continue
        
        logger.error(f"All click strategies failed for element: {element_id}")
        return False
    
    @staticmethod
    def _click_parent(driver: webdriver.Chrome, element_id: str, wait_time: int) -> bool:
        """Click parent element strategy"""
        parent_element = WebDriverWait(driver, wait_time).until(
            EC.element_to_be_clickable((By.XPATH, f"//*[@id='{element_id}']/parent::*"))
        )
        parent_element.click()
        return True
    
    @staticmethod
    def _click_label(driver: webdriver.Chrome, element_id: str, wait_time: int) -> bool:
        """Click associated label strategy"""
        label = WebDriverWait(driver, wait_time).until(
            EC.element_to_be_clickable((By.XPATH, f"//label[@for='{element_id}']"))
        )
        label.click()
        return True
    
    @staticmethod
    def _click_javascript(driver: webdriver.Chrome, element_id: str, wait_time: int) -> bool:
        """JavaScript click strategy"""
        element = WebDriverWait(driver, wait_time).until(
            EC.presence_of_element_located((By.ID, element_id))
        )
        driver.execute_script("arguments[0].click();", element)
        return True
    
    @staticmethod
    def _click_direct(driver: webdriver.Chrome, element_id: str, wait_time: int) -> bool:
        """Direct click strategy"""
        element = WebDriverWait(driver, wait_time).until(
            EC.element_to_be_clickable((By.ID, element_id))
        )
        element.click()
        return True


class PageUtilities:
    """Common utilities for page interactions"""
    
    def __init__(self, driver: webdriver.Chrome, config: SurveyConfig):
        self.driver = driver
        self.config = config
    
    def wait_for_page_load(self, timeout: Optional[int] = None):
        """Wait for page to fully load"""
        timeout = timeout or self.config.DEFAULT_TIMEOUT
        try:
            WebDriverWait(self.driver, timeout).until(
                lambda driver: driver.execute_script("return document.readyState") == "complete"
            )
        except TimeoutException:
            logger.warning("Page load timeout, continuing anyway")
    
    def take_screenshot(self, name_suffix: str = ""):
        """Take screenshot for debugging"""
        if self.driver:
            try:
                screenshot_path = f"screenshot_{name_suffix}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                self.driver.save_screenshot(screenshot_path)
                logger.info(f"Screenshot saved: {screenshot_path}")
            except Exception as e:
                logger.warning(f"Failed to take screenshot: {e}")
    
    def click_next_button(self):
        """Helper method to click next button"""
        try:
            next_button = WebDriverWait(self.driver, self.config.DEFAULT_TIMEOUT).until(
                EC.element_to_be_clickable((By.ID, "cmdNext1"))
            )
            next_button.click()
            logger.info("Clicked 'Next' button")
        except Exception as e:
            logger.error(f"Failed to click next button: {e}")
            raise
    
    def select_dropdown(self, element_id: str, value: str):
        """Helper method to select dropdown value"""
        try:
            dropdown = Select(self.driver.find_element(By.ID, element_id))
            dropdown.select_by_value(value)
        except Exception as e:
            logger.error(f"Failed to select dropdown {element_id} with value {value}: {e}")
            raise
    
    def group_question_elements(self, elements) -> Dict:
        """Group question answer elements by question and sub-question structure"""
        question_groups = {}
        
        for element in elements:
            try:
                element_id = element.get_attribute('id')
                if not element_id:
                    continue
                    
                parts = element_id.split('_')
                
                if len(parts) >= 3:  # At least QuestionAnswers_a_b format
                    question_num = int(parts[1])
                    
                    if len(parts) >= 4:  # Has sub-question
                        sub_question_num = int(parts[2])
                        
                        if question_num not in question_groups:
                            question_groups[question_num] = {}
                        
                        if sub_question_num not in question_groups[question_num]:
                            question_groups[question_num][sub_question_num] = []
                        
                        question_groups[question_num][sub_question_num].append(element_id)
                    
                    else:  # Simple format
                        if question_num not in question_groups:
                            question_groups[question_num] = {}
                        
                        if 0 not in question_groups[question_num]:
                            question_groups[question_num][0] = []
                        
                        question_groups[question_num][0].append(element_id)
            except (ValueError, IndexError) as e:
                logger.warning(f"Failed to parse element ID {element_id}: {e}")
                continue
        
        # Sort everything
        for question_num in question_groups:
            for sub_question_num in question_groups[question_num]:
                question_groups[question_num][sub_question_num].sort(
                    key=lambda x: self._extract_option_number(x)
                )
        
        return question_groups
    
    def _extract_option_number(self, element_id: str) -> int:
        """Extract option number from element ID for sorting"""
        try:
            parts = element_id.split('_')
            if len(parts) >= 4:
                return int(parts[3]) if parts[3].isdigit() else int(parts[2])
            elif len(parts) >= 3:
                return int(parts[2])
            return 0
        except (ValueError, IndexError):
            return 0
    
    def fill_personal_info_field_dynamic(self, field_label: str, value: str):
        """Dynamically fill personal information fields by label text"""
        try:
            if not value or value.strip() == "":
                logger.info(f"Skipping empty field: {field_label}")
                return
            
            # Multiple strategies to find input fields by label
            input_strategies = [
                # Strategy 1: Find input by preceding label text
                f"//label[contains(text(), '{field_label}')]/following-sibling::input[@type='text']",
                # Strategy 2: Find input by label 'for' attribute
                f"//label[contains(text(), '{field_label}')]/@for",
                # Strategy 3: Find input in same container as label
                f"//div[.//label[contains(text(), '{field_label}')]]//input[@type='text']",
                # Strategy 4: Find input by placeholder text
                f"//input[@type='text' and contains(@placeholder, '{field_label}')]"
            ]
            
            input_element = None
            used_strategy = None
            
            for i, strategy in enumerate(input_strategies):
                try:
                    if i == 1:  # Strategy 2 needs special handling
                        label_element = WebDriverWait(self.driver, self.config.SHORT_TIMEOUT).until(
                            EC.presence_of_element_located((By.XPATH, f"//label[contains(text(), '{field_label}')]"))
                        )
                        for_attr = label_element.get_attribute('for')
                        if for_attr:
                            input_element = self.driver.find_element(By.ID, for_attr)
                            used_strategy = f"Strategy {i+1} (label for attribute)"
                            break
                    else:
                        input_element = WebDriverWait(self.driver, self.config.SHORT_TIMEOUT).until(
                            EC.presence_of_element_located((By.XPATH, strategy))
                        )
                        used_strategy = f"Strategy {i+1}"
                        break
                except TimeoutException:
                    continue
                except Exception as e:
                    logger.debug(f"Strategy {i+1} failed for {field_label}: {e}")
                    continue
            
            if not input_element:
                logger.warning(f"Could not find input field for: {field_label}")
                return
            
            # Clear field and enter value
            input_element.clear()
            input_element.send_keys(value)
            logger.info(f"Filled {field_label}: '{value}' using {used_strategy}")
            
        except Exception as e:
            logger.error(f"Error filling field {field_label}: {e}")
            # Don't raise exception to allow other fields to be processed

    def handle_prize_draw_opt_out_dynamic(self, opt_out_value: str):
        """Handle prize draw opt-out checkbox dynamically"""
        try:
            should_opt_out = opt_out_value.upper() == 'YES'
            
            logger.debug(f"Prize draw opt-out setting: {opt_out_value} (should check: {should_opt_out})")
            
            # Multiple strategies to find the opt-out checkbox
            checkbox_strategies = [
                # Strategy 1: Find by label text containing opt-out keywords
                "//label[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'opt') and contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'out')]/preceding-sibling::input[@type='checkbox']",
                # Strategy 2: Find by label text containing prize or draw keywords  
                "//label[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'prize') or contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'draw')]/preceding-sibling::input[@type='checkbox']",
                # Strategy 3: Find any checkbox (fallback)
                "//input[@type='checkbox']"
            ]
            
            checkbox_element = None
            used_strategy = None
            
            for i, strategy in enumerate(checkbox_strategies):
                try:
                    checkboxes = self.driver.find_elements(By.XPATH, strategy)
                    if checkboxes:
                        checkbox_element = checkboxes[0]  # Take first match
                        used_strategy = f"Strategy {i+1}"
                        break
                except Exception as e:
                    logger.debug(f"Checkbox strategy {i+1} failed: {e}")
                    continue
            
            if not checkbox_element:
                logger.warning("Could not find prize draw opt-out checkbox")
                return
            
            # Check current state
            is_currently_checked = checkbox_element.is_selected()
            logger.debug(f"Checkbox currently checked: {is_currently_checked}, should be checked: {should_opt_out}")
            
            # Click checkbox if state needs to change
            if is_currently_checked != should_opt_out:
                checkbox_id = checkbox_element.get_attribute('id')
                if checkbox_id and ElementClickHelper.safe_click(self.driver, checkbox_id, self.config.SHORT_TIMEOUT):
                    logger.info(f"Prize draw opt-out checkbox toggled using {used_strategy}")
                else:
                    # Fallback: direct click
                    self.driver.execute_script("arguments[0].click();", checkbox_element)
                    logger.info(f"Prize draw opt-out checkbox toggled using JavaScript fallback")
            else:
                logger.info(f"Prize draw opt-out checkbox already in correct state ({should_opt_out})")
                
        except Exception as e:
            logger.error(f"Error handling prize draw opt-out: {e}")
            # Don't raise exception to allow form submission to continue