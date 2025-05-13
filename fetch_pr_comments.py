import requests
import datetime
import json
import openpyxl
import argparse
import time

# === CONFIGURATION ===
GITHUB_TOKEN = "your_token_here"  # Replace with your GitHub personal access token
USERNAME = "your_github_username"  # Replace with your GitHub username
HEADERS = {"Authorization": f"token {GITHUB_TOKEN}"}
API_URL = "https://api.github.com"
REPOS_PER_PAGE = 50
DAYS_BACK = 365

# Default hardcoded values
IGNORE_AUTHORS = [USERNAME,'filebased-rnd-tools']  # Default authors to ignore
DEFAULT_ORG = 'evertz-fbrnd'  # Default GitHub organization
DEFAULT_REPO = 'evertz'  # Default GitHub repository

# === ARGUMENT PARSER ===
parser = argparse.ArgumentParser(description="Fetch PR comments")
parser.add_argument("--reviews-only", action="store_true", help="Fetch only review comments")
parser.add_argument("--issues-only", action="store_true", help="Fetch only issue comments")
parser.add_argument("--ignore-authors", nargs="*", help="List of authors whose comments to ignore", default=[])
parser.add_argument("--only-authors", nargs="*", help="List of authors whose comments to allow only", default=[])
parser.add_argument('--days-back', type=int, help='Number of days to fetch comments from. Default is 365 days.')
parser.add_argument("--org", help="GitHub organization name", default=DEFAULT_ORG)  # Default org
parser.add_argument("--repo", help="Repository name", default=DEFAULT_REPO)  # Default repo
args = parser.parse_args()

# Override DAYS_BACK with the argument if provided
if args.days_back:
    DAYS_BACK = int(args.days_back)

# === SAFETY MEASURES ===
def check_rate_limit():
    url = "https://api.github.com/rate_limit"
    r = requests.get(url, headers=HEADERS)
    if r.status_code != 200:
        print(f"Error checking rate limit: {r.status_code} - {r.text}")
        exit()
    data = r.json()
    remaining = data["resources"]["core"]["remaining"]
    print(f"Remaining API calls: {remaining}")
    if remaining == 0:
        reset_time = data["resources"]["core"]["reset"]
        reset_time = datetime.datetime.utcfromtimestamp(reset_time)
        print(f"Rate limit exceeded. Please wait until {reset_time} UTC before retrying.")
        exit()

def handle_error(response):
    """Handle GitHub API errors."""
    if response.status_code != 200:
        print(f"Error: {response.status_code} - {response.text}")
        exit()

def get_user_repos(org_name):
    repos = []
    page = 1
    while True:
        url = f"{API_URL}/orgs/{org_name}/repos?per_page={REPOS_PER_PAGE}&page={page}"
        print(f"Fetching repos for org: {org_name}, page: {page}")
        r = requests.get(url, headers=HEADERS)
        handle_error(r)
        data = r.json()
        if not data:
            break
        repos.extend(data)
        page += 1
    return repos

def get_pull_requests(repo_name, org_name):
    pulls = []
    since = (datetime.datetime.now() - datetime.timedelta(days=DAYS_BACK)).isoformat()
    page = 1
    while True:
        url = f"{API_URL}/repos/{org_name}/{repo_name}/pulls?state=all&sort=created&direction=desc&per_page=50&page={page}"
        print(f"Fetching PRs for repo: {repo_name}, page: {page}")
        r = requests.get(url, headers=HEADERS)
        handle_error(r)
        data = r.json()
        if not data or "message" in data:
            break
        for pr in data:
            if pr["user"]["login"] == USERNAME and pr["created_at"] > since:
                pulls.append(pr)
        page += 1
    return pulls

def get_comments(org_name, repo_name, pr_number):
    comments = []

    if not args.issues_only:
        url_review_comments = f"{API_URL}/repos/{org_name}/{repo_name}/pulls/{pr_number}/comments"
        print(f"Fetching review comments for PR: {pr_number}")
        r = requests.get(url_review_comments, headers=HEADERS)
        handle_error(r)
        comments.extend(r.json())

    if not args.reviews_only:
        url_issue_comments = f"{API_URL}/repos/{org_name}/{repo_name}/issues/{pr_number}/comments"
        print(f"Fetching issue comments for PR: {pr_number}")
        r = requests.get(url_issue_comments, headers=HEADERS)
        handle_error(r)
        comments.extend(r.json())
     
    only_authors = args.only_authors                    # Will be None
    ignore_authors = args.ignore_authors if args.ignore_authors else IGNORE_AUTHORS

    if only_authors:
        filtered_comments = [comment for comment in comments if comment["user"] and comment["user"]["login"] in only_authors]
    else:
        filtered_comments = [comment for comment in comments if comment["user"] and comment["user"]["login"] not in ignore_authors]
        
    return filtered_comments

def main():
    check_rate_limit()  # Check for API rate limits at the beginning

    all_data = []
    org_name = args.org
    repo_name = args.repo

    repos = get_user_repos(org_name)
    
    # Ensure the specified repo exists in the org
    if repo_name not in [repo["name"] for repo in repos]:
        print(f"Error: Repository '{repo_name}' not found in organization '{org_name}'.")
        return

    prs = get_pull_requests(repo_name, org_name)
    for pr in prs:
        pr_number = pr["number"]
        pr_title = pr["title"]
        pr_url = pr["html_url"]
        comments = get_comments(org_name, repo_name, pr_number)
        for comment in comments:
            all_data.append({
                "repo": repo_name,
                "pr_number": pr_number,
                "pr_title": pr_title,
                "pr_url": pr_url,
                "comment_author": comment["user"]["login"],
                "comment_body": comment["body"],
                "comment_url": comment.get("html_url", ""),
                "created_at": comment["created_at"]
            })

    # Export to JSON
    with open("comments.json", "w") as f:
        json.dump(all_data, f, indent=4)

    # Export to Excel
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "PR Comments"
    headers = ["repo", "pr_number", "pr_title", "pr_url", "comment_author", "comment_body", "comment_url", "created_at"]
    ws.append(headers)
    for row in all_data:
        ws.append([row[h] for h in headers])
    wb.save("comments.xlsx")

    print("✅ Exported to comments.json and comments.xlsx")

if __name__ == "__main__":
    main()
