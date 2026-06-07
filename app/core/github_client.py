import logging
import yaml
from github import Github, GithubIntegration
from app.core.config import settings

logger = logging.getLogger(__name__)

def get_github_client(installation_id: int = None) -> Github:
    if settings.github_pat:
        return Github(settings.github_pat)
    
    if settings.github_app_id:
        private_key = None
        if settings.github_private_key:
            private_key = settings.github_private_key.replace('\\n', '\n')
        elif settings.github_private_key_path:
            with open(settings.github_private_key_path, "r") as f:
                private_key = f.read()
        
        if private_key:
            integration = GithubIntegration(settings.github_app_id, private_key)
            if installation_id:
                access_token = integration.get_access_token(installation_id).token
                return Github(access_token)
    
    logger.warning("GitHub credentials not configured properly.")
    return None

def process_pull_request(repo_full_name: str, pr_number: int, installation_id: int = None):
    from app.utils.diff_parser import parse_git_diff
    from app.ai.reviewer import analyze_code_changes, generate_pr_summary, generate_tests
    
    gh = get_github_client(installation_id)
    if not gh:
        return
        
    try:
        repo = gh.get_repo(repo_full_name)
        pr = repo.get_pull(pr_number)
        
        # 1. Fetch custom rules
        custom_rules = ""
        try:
            rules_file = repo.get_contents(".code-reviewer.yml", ref=pr.head.sha)
            yaml_rules = yaml.safe_load(rules_file.decoded_content)
            if yaml_rules:
                custom_rules = yaml.dump(yaml_rules)
        except Exception:
            pass
            
        files = pr.get_files()
        
        review_comments = []
        all_patches = []
        
        for file in files:
            if file.status == "removed" or not file.patch:
                continue
                
            all_patches.append(f"File: {file.filename}\nPatch:\n{file.patch}")
            
            # 2. Fetch full file context
            full_file_context = ""
            try:
                content_file = repo.get_contents(file.filename, ref=pr.head.sha)
                full_file_context = content_file.decoded_content.decode('utf-8')
            except Exception:
                pass
                
            line_to_position = parse_git_diff(file.patch)
            
            # 3. Call AI with rules and context
            ai_comments = analyze_code_changes(file.filename, file.patch, custom_rules, full_file_context)
            
            for comment in ai_comments:
                line_num = comment.get('line_number')
                body = comment.get('body')
                suggestion = comment.get('suggestion')
                
                position = line_to_position.get(line_num)
                
                if position:
                    final_body = f"🤖 **AI Reviewer:**\n\n{body}"
                    if suggestion:
                        final_body += f"\n\n```suggestion\n{suggestion}\n```"
                        
                    review_comments.append({
                        "path": file.filename,
                        "position": position,
                        "body": final_body
                    })
                    
            # 4. Generate tests
            tests = generate_tests(file.filename, file.patch)
            if tests and "Could not generate tests" not in tests:
                review_comments.append({
                    "path": file.filename,
                    "position": 1,
                    "body": f"🤖 **AI Reviewer Suggested Tests:**\n\n{tests}"
                })
                
        # 5. Generate PR Summary
        summary_body = "🤖 I have reviewed your pull request. Please see the inline comments below."
        if all_patches:
            pr_summary = generate_pr_summary(pr.title, pr.body or "", "\\n".join(all_patches))
            summary_body = f"🤖 **AI PR Summary:**\n\n{pr_summary}\n\n---\n" + summary_body
            
        if review_comments:
            commit = repo.get_commit(pr.head.sha)
            pr.create_review(
                commit=commit,
                body=summary_body,
                event="COMMENT",
                comments=review_comments
            )
            logger.info(f"Successfully posted {len(review_comments)} review comments on PR #{pr_number}")
        else:
            if all_patches:
                pr.create_issue_comment(summary_body)
            logger.info(f"No actionable issues found for PR #{pr_number}")
            
    except Exception as e:
        logger.error(f"Error processing pull request {repo_full_name}#{pr_number}: {e}", exc_info=True)

def process_issue_comment(repo_full_name: str, issue_number: int, comment_id: int, installation_id: int = None):
    from app.ai.reviewer import answer_question
    
    gh = get_github_client(installation_id)
    if not gh:
        return
        
    try:
        repo = gh.get_repo(repo_full_name)
        issue = repo.get_issue(issue_number)
        
        # Ensure it's a PR
        if not issue.pull_request:
            return
            
        comment = issue.get_comment(comment_id)
        
        # Don't reply to ourselves
        if comment.user.type == "Bot":
            return
            
        pr = repo.get_pull(issue_number)
        
        # Gather thread context
        comments = issue.get_comments()
        thread_context = f"PR Description: {issue.body}\n\n"
        for c in comments:
            thread_context += f"{c.user.login}: {c.body}\n"
            
        # Get patches for context
        files = pr.get_files()
        patch_context = ""
        for file in files:
            if file.patch:
                patch_context += f"File: {file.filename}\nPatch:\n{file.patch}\n"
                
        reply = answer_question(thread_context, patch_context)
        
        if reply:
            issue.create_comment(f"🤖 **AI Reviewer:**\n\n{reply}")
            logger.info(f"Replied to comment {comment_id} on PR #{issue_number}")
            
    except Exception as e:
        logger.error(f"Error processing issue comment {repo_full_name}#{issue_number}: {e}", exc_info=True)
