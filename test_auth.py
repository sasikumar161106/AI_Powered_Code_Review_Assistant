import jwt, time, requests
app_id = '3970625'
key = open('github-private-key.pem', 'r').read()
payload = {'iat': int(time.time()), 'exp': int(time.time()) + 600, 'iss': app_id}
encoded_jwt = jwt.encode(payload, key, algorithm='RS256')
r = requests.get('https://api.github.com/app', headers={'Authorization': f'Bearer {encoded_jwt}', 'Accept': 'application/vnd.github.v3+json'})
print(r.status_code)
print(r.json())
