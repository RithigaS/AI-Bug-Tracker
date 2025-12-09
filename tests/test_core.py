import unittest
import sys
import os

# Add parent directory to path to import utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.redaction import redact_sensitive_data
from utils.hashing import generate_log_hash

class TestCoreLogic(unittest.TestCase):
    
    def test_redaction_ip(self):
        text = "Connection failed from 192.168.1.1 at midnight."
        redacted = redact_sensitive_data(text)
        self.assertIn("[REDACTED_IP]", redacted)
        self.assertNotIn("192.168.1.1", redacted)

    def test_redaction_email(self):
        text = "Contact support@example.com for help."
        redacted = redact_sensitive_data(text)
        self.assertIn("[REDACTED_EMAIL]", redacted)
        self.assertNotIn("support@example.com", redacted)
        
    def test_redaction_api_key(self):
        text = "API_KEY = 'sk-1234567890abcdef1234567890abcdef'"
        redacted = redact_sensitive_data(text)
        self.assertIn("[REDACTED_SECRET]", redacted)
        self.assertNotIn("sk-1234567890abcdef1234567890abcdef", redacted)

    def test_hashing_consistency(self):
        text1 = "Error log content"
        text2 = "Error log content"
        text3 = "Different content"
        
        self.assertEqual(generate_log_hash(text1), generate_log_hash(text2))
        self.assertNotEqual(generate_log_hash(text1), generate_log_hash(text3))

if __name__ == '__main__':
    unittest.main()
