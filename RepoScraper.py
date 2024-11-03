# Code for scraping users.csv file

import requests
import pandas as pd

# GitHub API token for authentication
TOKEN = "GITHUB_ACCESS_TOKEN"
HEADERS = {"Authorization": f"token {TOKEN}"}

# API base URL for users in Austin with over 100 followers
BASE_URL = "https://api.github.com/search/users"
USER_DETAILS_URL = "https://api.github.com/users/"

# Initialize an empty list to store user data
user_data = []

# Pagination loop
page = 1
while True:
    # Search query
    params = {
        "q": "location:Dublin followers:>50",
        "per_page": 30,
        "page": page
    }
    response = requests.get(BASE_URL, headers=HEADERS, params=params)

    # Check for errors in response
    if response.status_code != 200:
        print("Error:", response.status_code, response.text)
        break

    users = response.json().get('items', [])
    print(f"Page {page}, Users found: {len(users)}")  # Debugging: check user count

    # Stop if there are no more users
    if not users:
        break

    # Fetch detailed information for each user
    for user in users:
        user_response = requests.get(USER_DETAILS_URL + user['login'], headers=HEADERS)

        # Check for errors in user detail response
        if user_response.status_code != 200:
            print("Error fetching user:", user['login'], user_response.text)
            continue

        user_info = user_response.json()

        # Format data as per specifications
        user_data.append({
            "login": user_info.get("login", ""),
            "name": user_info.get("name", ""),
            "company": (user_info.get("company", "").replace('@', '').strip().upper()
                        if user_info.get("company") else ""),
            "location": user_info.get("location", ""),
            "email": user_info.get("email", ""),
            "hireable": "true" if user_info.get("hireable") else "false" if user_info.get("hireable") is not None else "",
            "bio": user_info.get("bio", ""),
            "public_repos": user_info.get("public_repos", 0),
            "followers": user_info.get("followers", 0),
            "following": user_info.get("following", 0),
            "created_at": user_info.get("created_at", "")
        })

    # Move to the next page
    page += 1

# Check if user_data is populated
print("Total users collected:", len(user_data))

# Convert list of dictionaries to DataFrame and check for data presence before saving
if user_data:
    df = pd.DataFrame(user_data)
    df.to_csv("users.csv", index=False)
    print("Data saved to users.csv")
else:
    print("No data to save.")



# Code to fetch repositories for each user.

import requests
import pandas as pd
import time

# GitHub API token for authentication
TOKEN = "GITHUB_ACCESS_TOKEN"
HEADERS = {"Authorization": f"token {TOKEN}"}

# Load unique users from users.csv
users_df = pd.read_csv("users.csv")
unique_logins = users_df['login'].unique()  # Ensure only unique logins
repository_data = []

# Loop through each unique user login
for login in unique_logins:
    page = 1
    repo_count = 0

    while repo_count < 500:
        # Fetch repositories for the user, sorted by most recently pushed
        repo_url = f"https://api.github.com/users/{login}/repos"
        params = {
            "sort": "pushed",
            "per_page": 100,
            "page": page
        }
        response = requests.get(repo_url, headers=HEADERS, params=params)

        # Check for errors in response
        if response.status_code != 200:
            print("Error:", response.status_code, response.text)
            break

        repos = response.json()
        if not repos:
            break  # Stop if no more repositories

        # Process each repository
        for repo in repos:
            if repo_count >= 500:
                break  # Stop after collecting 500 repositories

            repository_data.append({
                "login": login,
                "full_name": repo.get("full_name", ""),
                "created_at": repo.get("created_at", ""),
                "stargazers_count": repo.get("stargazers_count", 0),
                "watchers_count": repo.get("watchers_count", 0),
                "language": repo.get("language", ""),
                "has_projects": "true" if repo.get("has_projects") else "false",
                "has_wiki": "true" if repo.get("has_wiki") else "false",
                "license_name": repo["license"]["key"] if repo.get("license") else ""
            })
            repo_count += 1

        page += 1
        time.sleep(1)  # Optional: sleep to avoid rate limiting

# Convert list of dictionaries to DataFrame
df_repos = pd.DataFrame(repository_data)

# Save DataFrame to repositories.csv
df_repos.to_csv("repositories.csv", index=False)
print("Data saved to repositories.csv")
