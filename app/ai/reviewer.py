import json
import logging
import litellm
from pydantic import BaseModel, Field
from app.core.config import settings

logger = logging.getLogger(__name__)

# Set Litellm API keys
if settings.gemini_api_key:
    litellm.api_key = settings.gemini_api_key
if settings.openai_api_key:
    litellm.openai_key = settings.openai_api_key
if settings.anthropic_api_key:
    litellm.anthropic_key = settings.anthropic_api_key

def get_model_name():
    return "groq/llama-3.1-8b-instant"

class ReviewCommentModel(BaseModel):
    line_number: int = Field(description="The exact line number in the NEW file where the issue occurs.")
    body: str = Field(description="The review comment.")
    suggestion: str | None = Field(default=None, description="The exact fixed code replacement for the issue, formatted properly.")

class ReviewResponseModel(BaseModel):
    comments: list[ReviewCommentModel] = Field(description="List of review comments.")

def generate_json_response(prompt: str, schema_class) -> dict | None:
    json_prompt = prompt + "\n\nCRITICAL: You MUST respond ONLY with a valid JSON object. The JSON object must have a single key called 'comments' which contains a list of objects. Each object must have 'line_number' (int), 'body' (string), and 'suggestion' (string or null). DO NOT wrap the JSON in markdown blocks like ```json."
    try:
        response = litellm.completion(
            model=get_model_name(),
            messages=[{"role": "user", "content": json_prompt}],
            response_format={"type": "json_object"},
            temperature=0.2
        )
        content = response.choices[0].message.content
        if content.startswith("```json"):
            content = content.replace("```json", "").replace("```", "").strip()
        elif content.startswith("```"):
            content = content.replace("```", "").strip()
        return json.loads(content)
    except Exception as e:
        logger.error(f"Error calling LLM: {e}")
        return None

def analyze_code_changes(file_path: str, patch: str, custom_rules: str = "", full_file_context: str = "") -> list[dict]:
    """Analyzes a git patch and returns comments with optional suggestions."""
    if not patch:
        return []

    context_str = f"Full File Context:\n```\n{full_file_context}\n```\n" if full_file_context else ""
    rules_str = f"Custom Rules to Enforce:\n{custom_rules}\n" if custom_rules else ""

    prompt = f"""You are an expert software engineer performing a code review.
Analyze the following code changes for the file `{file_path}` and provide constructive, actionable feedback.
Focus on bugs, security vulnerabilities, code smells, and performance bottlenecks.

If you find an issue, optionally provide a direct code fix in the `suggestion` field. The suggestion should contain EXACTLY the replacement code without markdown codeblocks or extra text. It will be wrapped in GitHub's ```suggestion tag by the system.

{rules_str}
{context_str}

File: {file_path}
Patch:
```diff
{patch}
```
"""
    result = generate_json_response(prompt, ReviewResponseModel)
    if result and "comments" in result:
        return result["comments"]
    return []

def generate_pr_summary(title: str, description: str, all_patches: str) -> str:
    """Generates a high-level summary of the PR."""
    prompt = f"""You are an expert software engineer. Review the following Pull Request details and code changes.
Generate a high-level PR Summary and Release Notes. Include "What Changed", "Why it Matters", and "Potential Impact".

PR Title: {title}
PR Description: {description}

Patches:
```diff
{all_patches}
```
"""
    try:
        response = litellm.completion(
            model=get_model_name(),
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )
        return response.choices[0].message.content
    except Exception as e:
        logger.error(f"Error generating PR summary: {e}")
        return "Could not generate PR summary."

def answer_question(comment_context: str, patch_context: str) -> str:
    """Answers a developer's question from a PR comment thread."""
    prompt = f"""You are an AI Code Review Assistant. A developer has replied to one of your comments or mentioned you in a PR.
Read the conversation history and the relevant code context, and provide a helpful, polite, and technical response.

Code Context:
```diff
{patch_context}
```

Conversation History:
{comment_context}

Respond directly to the developer.
"""
    try:
        response = litellm.completion(
            model=get_model_name(),
            messages=[{"role": "user", "content": prompt}],
            temperature=0.4
        )
        return response.choices[0].message.content
    except Exception as e:
        logger.error(f"Error answering question: {e}")
        return "I'm sorry, I encountered an error while trying to process your request."

def generate_tests(file_path: str, patch: str) -> str:
    """Generates unit tests for the modified code."""
    prompt = f"""You are an expert software engineer. Based on the following code changes in `{file_path}`, generate relevant unit tests to verify the new logic. Provide the complete test code.

Patch:
```diff
{patch}
```
"""
    try:
        response = litellm.completion(
            model=get_model_name(),
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )
        return response.choices[0].message.content
    except Exception as e:
        logger.error(f"Error generating tests: {e}")
        return "Could not generate tests."
