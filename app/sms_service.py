from twilio.rest import Client
from typing import Dict, Optional
import re

class SMSService:
    '''SMS Service for farmer communication via Twilio'''
    
    def __init__(self, account_sid: str, auth_token: str, phone_number: str):
        '''Initialize Twilio client'''
        self.client = Client(account_sid, auth_token)
        self.phone_number = phone_number
        self.sms_log = []
    
    def send_sms(self, to_number: str, message: str) -> Dict:
        '''
        Send SMS to farmer
        
        Args:
            to_number: Recipient phone number (Rwanda format: +250...)
            message: Message text (max 1600 chars)
        
        Returns:
            Dictionary with send status
        '''
        try:
            # Ensure message length is within limits
            if len(message) > 1600:
                message = message[:1597] + "..."
            
            # Send message
            sms = self.client.messages.create(
                body=message,
                from_=self.phone_number,
                to=to_number
            )
            
            # Log the SMS
            log_entry = {
                'sid': sms.sid,
                'to': to_number,
                'status': sms.status,
                'message': message,
                'timestamp': sms.date_created
            }
            self.sms_log.append(log_entry)
            
            return {
                'success': True,
                'sid': sms.sid,
                'status': sms.status
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def send_recommendation(self, to_number: str, recommendation: Dict) -> Dict:
        '''
        Format and send crop recommendation via SMS
        
        Args:
            to_number: Farmer's phone number
            recommendation: Prediction result dictionary
        '''
        # Format message for SMS
        crop = recommendation['prediction']['crop']
        confidence = recommendation['prediction']['confidence_percent']
        soil_status = recommendation['soil_health']['status']
        fertilizer = recommendation['recommendations']['fertilizer']
        season = recommendation['recommendations']['planting_season']
        
        # Build concise SMS message (Rwanda farmers prefer Kinyarwanda, but using English/French)
        message = f"""RWANDA SOIL ADVISORY

Recommended Crop: {crop}
Confidence: {confidence}
Soil Health: {soil_status}

FERTILIZER:
{fertilizer}

PLANTING:
Season: {season}
Spacing: {recommendation['recommendations']['spacing']}

"""
        
        # Add critical soil issues if any
        if recommendation['soil_health']['issues']:
            message += "⚠ SOIL ISSUES:\n"
            for issue in recommendation['soil_health']['issues'][:2]:  # Max 2 issues for SMS
                message += f"- {issue}\n"
        
        message += "\nFor questions, contact your extension officer."
        
        return self.send_sms(to_number, message)
    
    def parse_incoming_sms(self, message: str) -> Optional[Dict]:
        '''
        Parse incoming SMS from farmer to extract soil data
        
        Expected format: "SOIL 6.5 40 20 200" (Ph N P K)
        Alternative: "TEST 6.5 40 20 200"
        
        Returns:
            Dictionary with soil parameters or None if invalid
        '''
        # Clean message
        message = message.strip().upper()
        
        # Pattern: SOIL/TEST followed by 4 numbers
        pattern = r'(SOIL|TEST)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)'
        match = re.search(pattern, message)
        
        if match:
            try:
                return {
                    'Ph': float(match.group(2)),
                    'N': float(match.group(3)),
                    'P': float(match.group(4)),
                    'K': float(match.group(5))
                }
            except ValueError:
                return None
        
        return None
    
    def send_help_message(self, to_number: str) -> Dict:
        '''Send help/usage instructions to farmer'''
        message = """RWANDA SOIL MONITORING SYSTEM

How to use:
Send SMS with format:
SOIL [pH] [N] [P] [K]

Example:
SOIL 6.5 40 20 200

Where:
- pH: Soil acidity (3-10)
- N: Nitrogen (kg/ha)
- P: Phosphorus (kg/ha)
- K: Potassium (kg/ha)

You will receive crop recommendations.

Contact: [Extension Officer]"""
        
        return self.send_sms(to_number, message)
    
    def send_feedback_request(self, to_number: str, crop: str) -> Dict:
        '''Send feedback request after harvest season'''
        message = f"""RWANDA SOIL ADVISORY

Did you plant {crop} as recommended?

Please reply:
YES [yield in kg]
or
NO [what you planted]

Example: YES 1500
or: NO Maize

Your feedback helps us improve!"""
        
        return self.send_sms(to_number, message)