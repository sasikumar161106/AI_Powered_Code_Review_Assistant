from github import Github, GithubIntegration, Auth
app_id = '3970625'
key = open('github-private-key.pem', 'r').read()

try:
    integration = GithubIntegration(app_id, key)
    token = integration.get_access_token(138387450).token
    print("Generated token")
    
    gh = Github(token)
    repo = gh.get_repo("sasikumar161106/LogiSync-An_intelligent_multi-agent_logistics_platform_for_automotive_MSMEs")
    print("Success repo fetch:", repo.full_name)
except Exception as e:
    print("Error:", e)
