import requests

response = requests.get("https://api.github.com/users/pdm-project")
data = response.json()

print(f"PDM GitHub repository: {data['html_url']}")
print(f"PDM has {data['public_repos']} public repositories")
