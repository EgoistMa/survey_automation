"""
Page 10 Handler - Personal Information and Prize Draw Options
"""

import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from .basePage import BasePage
from utils.logger import get_logger

logger = get_logger(__name__)


class Page10Handler(BasePage):
    """Handle page 10 - Personal information and prize draw opt-out"""
    
    def __init__(self, driver, data, config=None, submit=False):
        """Initialize with submit flag"""
        super().__init__(driver, data, config)
        self.submit = submit
    
    def process(self):
        """Process page 10 - Filling Personal Information and Prize Draw Options"""
        try:
            self.log_start()
            
            # Wait for the form container to be present
            WebDriverWait(self.driver, self.config.DEFAULT_TIMEOUT).until(
                EC.presence_of_element_located((By.XPATH, "//div[contains(@id, 'QuestionAnswers_') and contains(@id, '_container')]"))
            )
            
            # Fill in personal information fields using dynamic locators
            self._fill_personal_information()
            
            # Handle prize draw opt-out checkbox dynamically
            self._handle_prize_draw_opt_out()
            
            # Final submission
            if self.submit:
                self.utils.click_next_button()
                logger.info("Survey submitted successfully!")
            else:
                logger.info("Survey completed (not submitted - test mode)")
            
            self.log_complete()
            
        except Exception as e:
            self.handle_error(e)
    
    def _fill_personal_information(self):
        """Fill personal information fields"""
        personal_info_fields = [
            ("Name", self.data.get('name', '')),
            ("State", self.data.get('state', 'NSW')),
            ("Email address", self.data.get('email', '')),
            ("Contact number", self.data.get('contact', ''))
        ]
        
        for field_label, value in personal_info_fields:
            self.utils.fill_personal_info_field_dynamic(field_label, value)
    
    def _handle_prize_draw_opt_out(self):
        """Handle prize draw opt-out checkbox"""
        opt_out_value = self.data.get('opt_out_draw', 'NO')
        self.utils.handle_prize_draw_opt_out_dynamic(opt_out_value)