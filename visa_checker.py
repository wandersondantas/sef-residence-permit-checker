import os
import time
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementNotInteractableException

class SEFVisaChecker:
    def __init__(self, username, password, residency_number, telegram_token, chat_id):
        self.username = username
        self.password = password
        self.residency_number = residency_number
        self.telegram_token = telegram_token
        self.chat_id = chat_id

    def send_telegram_message(self, message):
        url = f"https://api.telegram.org/bot{self.telegram_token}/sendMessage"
        params = {
            "chat_id": self.chat_id,
            "text": message
        }
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            print(f"Message sent: {message}")
        except Exception as e:
            print(f"Failed to send Telegram message: {e}")

    def setup_driver(self):
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--window-size=1920,1080')
        return webdriver.Chrome(options=options)

    def wait_and_interact(self, driver, by, value, interaction_type='click', timeout=10):
        """
        Robust method to wait for and interact with an element
        """
        try:
            element = WebDriverWait(driver, timeout).until(
                EC.element_to_be_clickable((by, value))
            )
            
            # Scroll element into view
            driver.execute_script("arguments[0].scrollIntoView(true);", element)
            
            # Small wait to ensure element is ready
            time.sleep(1)
            
            if interaction_type == 'click':
                element.click()
            elif interaction_type == 'send_keys':
                return element
            
            return element
        except Exception as e:
            print(f"Error interacting with element {value}: {e}")
            return None

    def check_visa_renewal(self):
        driver = None
        try:
            driver = self.setup_driver()
            driver.get('https://www.sef.pt/pt/Pages/homepage.aspx')
            
            # Wait and click login launcher with multiple attempts
            max_attempts = 3
            for attempt in range(max_attempts):
                try:
                    login_launcher = self.wait_and_interact(
                        driver, 
                        By.CLASS_NAME, 
                        'login-launcher'
                    )
                    if login_launcher:
                        break
                except Exception as inner_e:
                    print(f"Attempt {attempt + 1} failed: {inner_e}")
                    time.sleep(2)
            
            # Login process with robust interactions
            username_input = self.wait_and_interact(
                driver, 
                By.ID, 
                'txtUsername', 
                interaction_type='send_keys'
            )
            if username_input:
                username_input.send_keys(self.username)
            
            password_input = self.wait_and_interact(
                driver, 
                By.ID, 
                'txtPassword', 
                interaction_type='send_keys'
            )
            if password_input:
                password_input.send_keys(self.password)
            
            login_button = self.wait_and_interact(
                driver, 
                By.ID, 
                'btnLogin'
            )
            
            # Navigate to renewal page
            driver.get('https://www.sef.pt/pt/mySEF/Pages/renovacao-automatica.aspx')
            
            # Detailed interaction with renewal form
            email_input = self.wait_and_interact(
                driver, 
                By.ID, 
                'txtAuthPanelEmail', 
                interaction_type='send_keys'
            )
            if email_input:
                email_input.send_keys(self.username)
            
            password_panel_input = self.wait_and_interact(
                driver, 
                By.ID, 
                'txtAuthPanelPassword', 
                interaction_type='send_keys'
            )
            if password_panel_input:
                password_panel_input.send_keys(self.password)
            
            document_input = self.wait_and_interact(
                driver, 
                By.ID, 
                'txtAuthPanelDocument', 
                interaction_type='send_keys'
            )
            if document_input:
                document_input.send_keys(self.residency_number)
            
            submit_button = self.wait_and_interact(
                driver, 
                By.ID, 
                'btnAutenticaUtilizador'
            )
            
            # Check for errors
            try:
                error_div = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.CLASS_NAME, 'error-row'))
                )
                error_message = error_div.text
                self.send_telegram_message(f"SEF Renewal Error: {error_message}")
            except TimeoutException:
                # No error detected, send specific message
                self.send_telegram_message("Sua AR pode ser renovada")
            
            # Take screenshot for debugging
            driver.save_screenshot('sef_check_result.png')
        
        except Exception as e:
            error_message = f"SEF Checker Error: {str(e)}"
            print(error_message)
            self.send_telegram_message(error_message)
        
        finally:
            if driver:
                driver.quit()

def main():
    # Read credentials from environment variables
    username = os.environ.get('SEF_USERNAME')
    password = os.environ.get('SEF_PASSWORD')
    residency_number = os.environ.get('SEF_RESIDENCY_NUMBER')
    telegram_token = os.environ.get('TELEGRAM_BOT_TOKEN')
    chat_id = os.environ.get('TELEGRAM_CHAT_ID')

    checker = SEFVisaChecker(username, password, residency_number, telegram_token, chat_id)
    checker.check_visa_renewal()

if __name__ == '__main__':
    main()