"""
Data generation utilities for creating random survey data
"""

import random
from datetime import datetime
from typing import Dict


class DataGenerator:
    """Helper class for generating random survey data"""
    
    @staticmethod
    def generate_random_email() -> str:
        """Generate a random email address"""
        first_names = ["john", "mary", "david", "sarah", "michael", "jennifer", "robert", "lisa"]
        last_names = ["smith", "johnson", "williams", "jones", "brown", "davis", "miller", "wilson"]
        domains = ["gmail.com", "yahoo.com", "hotmail.com", "outlook.com", "icloud.com"]
        
        first_name = random.choice(first_names)
        last_name = random.choice(last_names)
        domain = random.choice(domains)
        
        if random.random() < 0.4:
            number = random.randint(1, 9999)
            return f"{first_name}.{last_name}{number}@{domain}"
        else:
            formats = [
                f"{first_name}.{last_name}@{domain}",
                f"{first_name}_{last_name}@{domain}",
                f"{first_name}{random.randint(1, 99)}@{domain}"
            ]
            return random.choice(formats)

    @staticmethod
    def generate_random_phone() -> str:
        """Generate a random Australian phone number"""
        prefix = "04"
        remaining_digits = ''.join(random.choice("0123456789") for _ in range(8))
        return prefix + remaining_digits

    @staticmethod
    def generate_survey_data() -> Dict:
        """Generate random survey data"""
        return {
            'date': datetime.now().strftime("%d/%m/%Y"),
            'time_period': random.choice([
                "Morning (6am-11am)", 
                "Lunch (11am – 2pm)", 
                "Afternoon (2pm – 6pm)", 
                "Evening (6pm – 11pm)"
            ]),
            'state': "NSW",
            'location': "Manly",
            'dining_option': random.choice(["Purchased for takeaway", "Dined in at Starbucks"]),
            'worth_rating': 7,
            'employees_effort_rating': 7,
            'beverage_rating': 7,
            'cleanliness_rating': 7,
            'order_accuracy_rating': 7,
            'employee_exceed_rating': 7,
            'time_rating': 7,
            'food_rating': 7,
            'feedback_text': " ",
            'recommend_rating': 10,
            'is_membership': random.choice(["YES", "NO"]),
            'next_visit': random.choice([
                "Today", 
                "Tomorrow", 
                "Within the next week", 
                "More than a month from now", 
            ]),
            'name': " ",
            'email': DataGenerator.generate_random_email(),
            'contact': DataGenerator.generate_random_phone(),
            'opt_out_draw': random.choice(["YES", "NO"])
        }