"""
Page 2 Handler - Date, Time and State/Territory
"""

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from .basePage import BasePage
from utils.logger import get_logger

logger = get_logger(__name__)


class Page2Handler(BasePage):
    """Handle page 2 - Date, Time and State/Territory"""
    
    def process(self):
        """Process page 2 - Setting Date, Time and State/Territory"""
        try:
            self.log_start()
            
            # Extract and validate date
            date_parts = self._parse_date()
            day, month, year = date_parts
            
            # Get dynamic question ID
            element = WebDriverWait(self.driver, self.config.DEFAULT_TIMEOUT).until(
                EC.presence_of_element_located((By.XPATH, "//*[starts-with(@id, 'QuestionAnswers_') and contains(@id, '_day')]"))
            )
            question_id = element.get_attribute("id").split("_")[1]
            logger.debug(f"Dynamic question ID: {question_id}")

            # Select date components
            self.utils.select_dropdown(f"QuestionAnswers_{question_id}_day", day)
            self.utils.select_dropdown(f"QuestionAnswers_{question_id}_month", month)
            self.utils.select_dropdown(f"QuestionAnswers_{question_id}_year", year)
            logger.info(f"Date selected: {year}-{month}-{day}")
            
            # Select time period
            self._select_time_period(int(question_id) + 1)
            
            # Select state
            self._select_state(int(question_id) + 2)
            
            self.utils.click_next_button()
            self.log_complete()
            
        except Exception as e:
            self.handle_error(e)
    
    def _parse_date(self):
        """Parse and validate date from data"""
        try:
            date_parts = self.data['date'].split('/')
            if len(date_parts) != 3:
                raise ValueError(f"Invalid date format: {self.data['date']}")
            
            day, month, year = date_parts[0].zfill(2), date_parts[1].zfill(2), date_parts[2]
            return day, month, year
            
        except Exception as e:
            logger.error(f"Date parsing error: {e}")
            raise
    
    def _select_time_period(self, question_id: int):
        """Select time period from dropdown"""
        time_value = self.config.TIME_MAPPING.get(self.data['time_period'])
        if not time_value:
            raise ValueError(f"Invalid time period: {self.data['time_period']}")
        
        self.utils.select_dropdown(f"QuestionAnswers_{question_id}", time_value)
        logger.info(f"Time period selected: {self.data['time_period']}")
    
    def _select_state(self, question_id: int):
        """Select state from dropdown"""
        state_value = self.config.STATE_MAPPING.get(self.data['state'])
        if not state_value:
            raise ValueError(f"Invalid state: {self.data['state']}")
        
        self.utils.select_dropdown(f"QuestionAnswers_{question_id}", state_value)
        logger.info(f"State selected: {self.data['state']}")