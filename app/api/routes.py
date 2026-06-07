from fastapi import APIRouter, Request, BackgroundTasks
import logging
from app.core.github_client import process_pull_request, process_issue_comment

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/webhook")
async def github_webhook(request: Request, background_tasks: BackgroundTasks):
    payload = await request.json()
    event = request.headers.get("X-GitHub-Event")
    
    logger.info(f"Received GitHub webhook event: {event}")
    
    if event == "pull_request":
        action = payload.get("action")
        if action in ["opened", "synchronize", "reopened"]:
            logger.info(f"Processing PR event: {action}")
            pr = payload.get("pull_request", {})
            repo = payload.get("repository", {})
            installation = payload.get("installation", {})
            
            repo_full_name = repo.get("full_name")
            pr_number = pr.get("number")
            installation_id = installation.get("id")
            
            if repo_full_name and pr_number:
                background_tasks.add_task(
                    process_pull_request, 
                    repo_full_name, 
                    pr_number, 
                    installation_id
                )
    
    elif event == "issue_comment":
        action = payload.get("action")
        if action == "created":
            logger.info("Processing issue_comment created event")
            issue = payload.get("issue", {})
            comment = payload.get("comment", {})
            repo = payload.get("repository", {})
            installation = payload.get("installation", {})
            
            repo_full_name = repo.get("full_name")
            issue_number = issue.get("number")
            comment_id = comment.get("id")
            installation_id = installation.get("id")
            
            if repo_full_name and issue_number and comment_id:
                background_tasks.add_task(
                    process_issue_comment,
                    repo_full_name,
                    issue_number,
                    comment_id,
                    installation_id
                )
    
    return {"status": "ok", "event": event}
