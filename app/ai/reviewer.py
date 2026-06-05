import json
import logging
from google import genai
from pydantic import BaseModel, Field
from app.core.config import settings

logger = logging.getLogger(__name__)

# Initialize Gemini
client = None
if settings.gemini_api_key:
    client = genai.Client(api_key=settings.gemini_api_key)

class ReviewCommentModel(BaseModel):
    line_number: int = Field(description="The exact line number in the NEW file where the issue occurs.")
    body: str = Field(description="The review comment.")

class ReviewResponseModel(BaseModel):
    comments: list[ReviewCommentModel] = Field(description="List of review comments.")

def analyze_code_changes(file_path: str, patch: str) -> list[dict]:
    """
    Analyzes a git patch using Google Gemini and returns a list of comments.
    """
    if not client or not patch:
        return []

    prompt = f"""You are an expert software engineer performing a code review.
Analyze the following code changes for the file `{file_path}` and provide constructive, actionable feedback.
Focus on bugs, security vulnerabilities, code smells, and performance bottlenecks.

If there are no issues, return an empty list of comments.

File: {file_path}
Patch:
```diff
{patch}
```
"""
    try:
        response = client.models.generate_content(
            model='gemini-1.5-pro',
            contents=prompt,
            config={
                'response_mime_type': 'application/json',
                'response_schema': ReviewResponseModel,
            },
        )
        
        result = json.loads(response.text)
        return result.get("comments", [])
    except Exception as e:
        logger.error(f"Error generating review for {file_path}: {e}")
        return []
