"""
Main automation class for handling the survey process
"""

from typing import Dict, List
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from core.utils.pageUtils import SurveyConfig
from core.pageHandlers.page1 import Page1Handler
from core.pageHandlers.page2 import Page2Handler
from core.pageHandlers.page3 import Page3Handler
from core.pageHandlers.page4 import Page4Handler
from core.pageHandlers.page5 import Page5Handler
from core.pageHandlers.page6 import Page6Handler
from core.pageHandlers.page7 import Page7Handler
from core.pageHandlers.page8 import Page8Handler
from core.pageHandlers.page9 import Page9Handler
from core.pageHandlers.page10 import Page10Handler

from utils.logger import get_logger

logger = get_logger(__name__)


class SurveyAutomation:
    """Main automation class for Starbucks survey"""

    def __init__(self, data: Dict, submit: bool = False, location: str = "Chatswood"):
        """Initialize automation class with survey data"""
        self.submit = submit
        self.location = location
        self.data = data
        self.driver = None
        self.config = SurveyConfig()
        self.page_handlers = []
    
    def setup_driver(self) -> webdriver.Chrome:
        """Set up WebDriver with optimized configurations"""
        options = Options()
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--window-size=1920,1080')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        # Disable images and CSS for faster loading (optional)
        prefs = {
            "profile.managed_default_content_settings.images": 2,
            "profile.default_content_setting_values.notifications": 2
        }
        options.add_experimental_option("prefs", prefs)
        
        self.driver = webdriver.Chrome(options=options)
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        return self.driver
    
    def initialize_page_handlers(self) -> List:
        """Initialize all page handlers"""
        self.page_handlers = [
            Page1Handler(self.driver, self.data, self.config),
            Page2Handler(self.driver, self.data, self.config),
            Page3Handler(self.driver, self.data, self.config, self.location),
            Page4Handler(self.driver, self.data, self.config),
            Page5Handler(self.driver, self.data, self.config,),
            Page6Handler(self.driver, self.data, self.config),
            Page7Handler(self.driver, self.data, self.config),
            Page8Handler(self.driver, self.data, self.config),
            Page9Handler(self.driver, self.data, self.config),
            Page10Handler(self.driver, self.data, self.config, self.submit)
        ]
        return self.page_handlers
    
    def fill_survey(self) -> bool:
        """Main method to fill out the entire survey"""
        try:
            self.setup_driver()
            self.initialize_page_handlers()
            
            logger.info(f"Starting survey - Date: {self.data['date']}, Location: {self.location}, Submit: {'Yes' if self.submit else 'No'}")
            
            # Process all pages
            for i, page_handler in enumerate(self.page_handlers, 1):
                try:
                    page_handler.process()
                except Exception as e:
                    logger.error(f"Error on page {i} ({page_handler.__class__.__name__}): {e}")
                    page_handler.utils.take_screenshot(f"error_page_{i}")
                    raise

            logger.info(f"Survey successfully completed - Location: {self.location}")
            return True
            
        except Exception as e:
            logger.error(f"Error filling survey: {e}")
            if self.driver and hasattr(self, 'page_handlers') and self.page_handlers:
                self.page_handlers[0].utils.take_screenshot("error_final")
            return False
            
        finally:
            if self.driver:
                import time
                time.sleep(2)  # Brief pause to see results
                self.driver.quit()