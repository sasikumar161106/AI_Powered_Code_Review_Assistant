import logging
from github import Github, GithubIntegration
from app.core.config import settings

logger = logging.getLogger(__name__)

def get_github_client(installation_id: int = None) -> Github:
    if settings.github_pat:
        return Github(settings.github_pat)
    
    if settings.github_app_id and settings.github_private_key_path:
        with open(settings.github_private_key_path, "r") as f:
            private_key = f.read()
        
        integration = GithubIntegration(settings.github_app_id, private_key)
        if installation_id:
            access_token = integration.get_access_token(installation_id).token
            return Github(access_token)
    
    logger.warning("GitHub credentials not configured properly.")
    return None

def process_pull_request(repo_full_name: str, pr_number: int, installation_id: int = None):
    from app.utils.diff_parser import parse_git_diff
    from app.ai.reviewer import analyze_code_changes
    
    gh = get_github_client(installation_id)
    if not gh:
        return
        
    try:
        repo = gh.get_repo(repo_full_name)
        pr = repo.get_pull(pr_number)
        files = pr.get_files()
        
        review_comments = []
        
        for file in files:
            if file.status == "removed" or not file.patch:
                continue
                
            line_to_position = parse_git_diff(file.patch)
            ai_comments = analyze_code_changes(file.filename, file.patch)
            
            for comment in ai_comments:
                line_num = comment.get('line_number')
                body = comment.get('body')
                
                position = line_to_position.get(line_num)
                
                if position:
                    review_comments.append({
                        "path": file.filename,
                        "position": position,
                        "body": f"🤖 **AI Reviewer:**\n\n{body}"
                    })
                    
        if review_comments:
            commit = repo.get_commit(pr.head.sha)
            pr.create_review(
                commit=commit,
                body="🤖 I have reviewed your pull request. Please see the inline comments below.",
                event="COMMENT",
                comments=review_comments
            )
            logger.info(f"Successfully posted {len(review_comments)} review comments on PR #{pr_number}")
        else:
            logger.info(f"No actionable issues found for PR #{pr_number}")
            
    except Exception as e:
        logger.error(f"Error processing pull request {repo_full_name}#{pr_number}: {e}")
