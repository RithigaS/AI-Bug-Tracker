import os
from typing import Dict, Any
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field

# Load environment variables
load_dotenv()

# Define the output structure
class LogAnalysis(BaseModel):
    issue_type: str = Field(description="The category of the issue (e.g., Database Error, Network Timeout, Syntax Error)")
    root_cause: str = Field(description="A detailed explanation of the root cause of the error")
    suggested_fix: str = Field(description="Actionable steps or code snippets to fix the issue")
    severity: str = Field(description="Severity level: Low, Medium, High, or Critical")

def get_llm():
    """Initializes the LLM using Groq API key."""
    groq_api_key = os.getenv("GROQ_API_KEY")
    
    if groq_api_key:
        # Using Llama3-70b-8192 as default for Groq
        return ChatGroq(
            temperature=0,
            model_name="llama-3.1-8b-instant",
            api_key=groq_api_key
        )
    else:
        raise ValueError(
            "No GROQ_API_KEY found. Please set GROQ_API_KEY in .env file."
        )

def analyze_log_content(log_content: str) -> Dict[str, Any]:
    """
    Analyzes the provided log content using the configured LLM.
    Returns a dictionary with issue_type, root_cause, suggested_fix, and severity.
    """
    llm = get_llm()
    
    parser = JsonOutputParser(pydantic_object=LogAnalysis)
    
    prompt = PromptTemplate(
        template="""You are an expert software debugger. Analyze the following error log and provide a structured analysis.
        
        Log Content:
        {log_content}
        
        {format_instructions}
        """,
        input_variables=["log_content"],
        partial_variables={"format_instructions": parser.get_format_instructions()},
    )
    
    chain = prompt | llm | parser
    
    try:
        result = chain.invoke({"log_content": log_content})
        return result
    except Exception as e:
        return {
            "issue_type": "Analysis Failed",
            "root_cause": f"AI processing failed: {str(e)}",
            "suggested_fix": "Check GROQ_API_KEY and internet connection.",
            "severity": "Unknown"
        }
