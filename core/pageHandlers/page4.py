"""
Page 4 Handler - Dining Option Selection
"""

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from .basePage import BasePage
from core.utils.pageUtils import ElementClickHelper
from utils.logger import get_logger

logger = get_logger(__name__)


class Page4Handler(BasePage):
    """Handle page 4 - Dining option selection"""
    
    def process(self):
        """Process page 4 - Selecting Dining Option"""
        try:
            self.log_start()
            
            # Wait for elements to load
            elements = WebDriverWait(self.driver, self.config.DEFAULT_TIMEOUT).until(
                EC.presence_of_all_elements_located((By.XPATH, "//*[starts-with(@id, 'QuestionAnswers_')]"))
            )
            
            grouped_questions = self.utils.group_question_elements(elements)
            logger.debug(f"Grouped Questions: {grouped_questions}")
            
            option_index = self.config.DINING_OPTION_MAPPING.get(self.data['dining_option'])
            if option_index is None:
                raise ValueError(f"Invalid dining option: {self.data['dining_option']}")
            
            self._select_dining_option(grouped_questions, option_index)
            
            self.utils.click_next_button()
            self.log_complete()
            
        except Exception as e:
            self.handle_error(e)
    
    def _select_dining_option(self, grouped_questions, option_index):
        """Select the dining option based on index"""
        try:
            # Get first question options
            first_question = min(grouped_questions.keys())
            first_sub_question = min(grouped_questions[first_question].keys())
            available_options = grouped_questions[first_question][first_sub_question]
            
            if option_index >= len(available_options):
                raise IndexError(f"Option index {option_index} out of range for {len(available_options)} options")
            
            selected_element_id = available_options[option_index]
            logger.info(f"Selecting dining option: {selected_element_id}")
            
            # Use helper to click element
            if not ElementClickHelper.safe_click(self.driver, selected_element_id):
                raise Exception(f"Failed to click dining option: {selected_element_id}")
                
        except Exception as e:
            logger.error(f"Error selecting dining option: {e}")
            raise