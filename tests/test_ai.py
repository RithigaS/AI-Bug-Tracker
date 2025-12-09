import sys
import os
from dotenv import load_dotenv

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ai_engine import analyze_log_content

def test_ai_connection():
    print("Testing AI Engine...")
    sample_log = "Error: Connection refused at 192.168.1.1. TimeoutException."
    
    try:
        result = analyze_log_content(sample_log)
        print("\nAnalysis Result:")
        print(result)
        
        if result.get('issue_type') == "Analysis Failed":
            print("\n❌ AI Analysis Failed. Check error message above.")
        else:
            print("\n✅ AI Analysis Successful!")
            
    except Exception as e:
        print(f"\n❌ Test Failed with Exception: {e}")

if __name__ == "__main__":
    test_ai_connection()
