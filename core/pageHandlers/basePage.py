"""
Base page handler class for common functionality
"""

from abc import ABC, abstractmethod
from typing import Dict
from selenium import webdriver

from core.utils.pageUtils import PageUtilities, SurveyConfig
from utils.logger import get_logger

logger = get_logger(__name__)


class BasePage(ABC):
    """Abstract base class for page handlers"""
    
    def __init__(self, driver: webdriver.Chrome, data: Dict, config: SurveyConfig = None):
        """Initialize page handler"""
        self.driver = driver
        self.data = data
        self.config = config or SurveyConfig()
        self.utils = PageUtilities(driver, self.config)
    
    @abstractmethod
    def process(self):
        """Process the page - must be implemented by subclasses"""
        pass
    
    def get_page_name(self) -> str:
        """Get page name for logging"""
        return self.__class__.__name__
    
    def log_start(self):
        """Log page processing start"""
        logger.info(f"{self.get_page_name()} - Starting page processing")
    
    def log_complete(self):
        """Log page processing completion"""
        logger.info(f"{self.get_page_name()} - Page processing completed")
    
    def handle_error(self, error: Exception, take_screenshot: bool = True):
        """Handle page processing errors"""
        logger.error(f"{self.get_page_name()} - Error: {error}")
        if take_screenshot:
            self.utils.take_screenshot(f"error_{self.get_page_name().lower()}")
        raise error