from github import GithubIntegration
app_id = '3970625'
key = open('github-private-key.pem', 'r').read()
integration = GithubIntegration(app_id, key)
try:
    token = integration.get_access_token(138387450).token
    print("PyGithub Token Success")
except Exception as e:
    print("PyGithub Token Error:", e)
