"""
Core functionality for Crystal HR Automation.
"""
import json
import logging
import random
import time
from datetime import datetime
from typing import Optional, Dict, Any

import requests

from .emailer import EmailNotifier

logger = logging.getLogger(__name__)

class CrystalHRAutomation:
    """Main class for interacting with Crystal HR system."""
    
    def __init__(self, base_url: str = "https://desicrewdtrial.crystalhr.com", 
                 email_notifier: Optional[EmailNotifier] = None):
        """Initialize the Crystal HR Automation.
        
        Args:
            base_url: Base URL of the Crystal HR system
            email_notifier: Optional EmailNotifier instance for notifications
        """
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive'
        })
        self.email_notifier = email_notifier
        self.logged_in = False
    
    def login(self, username: str, password: str, company_id: str = '1') -> bool:
        """Login to Crystal HR system.
        
        Args:
            username: HR system username
            password: HR system password
            company_id: Company ID (usually '1' for single-company setups)
            
        Returns:
            bool: True if login was successful, False otherwise
        """
        logger.info(f"🔐 Attempting login for user: {username}")
        
        try:
            # First, get the login page to establish session
            self.session.get(f"{self.base_url}/")
            
            # Prepare login data
            login_data = {
                'CompanyId': company_id,
                'Username': username,
                'Password': password,
                'From': 'Web',
                'GenerateOTP': 'false',
                'RememberMe': 'false'
            }
            
            # Submit login form
            response = self.session.post(
                f"{self.base_url}/",
                data=login_data,
                headers={'Content-Type': 'application/x-www-form-urlencoded'},
                allow_redirects=True
            )
            
            # Check if login was successful
            if any(x in response.text for x in ['Welcome,', 'Dashboard', 'Home/Index']):
                logger.info("✅ Login successful!")
                self.logged_in = True
                return True
            else:
                error_msg = "Login failed - check credentials"
                logger.error(f"❌ {error_msg}")
                if self.email_notifier:
                    self.email_notifier.send_email("Login Failed", error_msg)
                return False
                
        except Exception as e:
            error_msg = f"Login error: {e}"
            logger.error(f"❌ {error_msg}")
            if self.email_notifier:
                self.email_notifier.send_email("Login Error", error_msg)
            return False
    
    def punch(self, punch_type: str = "in") -> bool:
        """Perform punch in/out operation.
        
        Args:
            punch_type: Either 'in' or 'out' to specify punch type
            
        Returns:
            bool: True if punch was successful, False otherwise
        """
        if not self.logged_in:
            logger.error("❌ Not logged in. Call login() first.")
            return False
            
        punch_mode = 0 if punch_type.lower() == "in" else 1
        punch_action = "Punch In" if punch_mode == 0 else "Punch Out"
        
        logger.info(f"⏰ Attempting {punch_action}...")
        
        try:
            # First, refresh the home page to ensure valid session
            self.session.get(f"{self.base_url}/Home/Index")
            
            # Prepare punch data
            punch_data = {
                'InOutPunchMode': punch_mode,
                'TimeZone': 'Asia/Calcutta'
            }
            
            # Set headers for the punch request
            punch_headers = {
                'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                'X-Requested-With': 'XMLHttpRequest',
                'Origin': self.base_url,
                'Referer': f"{self.base_url}/Home/Index"
            }
            
            # Send punch request
            response = self.session.post(
                f"{self.base_url}/Modules/TimeAttendance/WebPunch",
                data=punch_data,
                headers=punch_headers
            )
            
            # Check response
            if response.status_code == 200:
                try:
                    result = response.json()
                    if 'msg' in result and 'success' in result['msg'].lower():
                        success_msg = f"✅ {punch_action} successful: {result['msg']}"
                        logger.info(success_msg)
                        
                        if self.email_notifier:
                            self.email_notifier.send_email(
                                f"HR Automation: {punch_action} Successful",
                                f"{punch_action} was completed successfully at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                            )
                        return True
                except json.JSONDecodeError:
                    logger.error("❌ Failed to parse punch response as JSON")
                    return False
            
            error_msg = f"Punch {punch_action} failed"
            logger.error(f"❌ {error_msg}")
            if self.email_notifier:
                self.email_notifier.send_email(
                    f"HR Automation: {punch_action} Failed",
                    f"Failed to complete {punch_action}. Status code: {response.status_code}"
                )
            return False
            
        except Exception as e:
            error_msg = f"Error during {punch_action}: {e}"
            logger.error(f"❌ {error_msg}")
            if self.email_notifier:
                self.email_notifier.send_email(
                    f"HR Automation: {punch_action} Error",
                    f"An error occurred during {punch_action}: {e}"
                )
            return False
