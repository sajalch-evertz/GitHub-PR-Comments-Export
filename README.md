# GitHub PR Comments Fetcher

This script fetches pull request (PR) comments from a specified GitHub organization and repository for the past year. It supports the option to filter and export review comments and issue comments into JSON and Excel formats. It also includes functionality to ignore specific authors' comments based on either a default list or user-provided list via the command-line argument.

## Requirements

* Python 3.x (Recommended: Python 3.12+)
* GitHub Personal Access Token with "repo" scope

**Install system packages (for Debian/Ubuntu):**

```bash
sudo apt install python3.12-venv
```

## Setup (one-time)
You can use `setup.sh`
1. **Make it executable:**

   ```bash
   sudo chmod +x setup.sh
   ```
2. **Run the script:**

   ```bash
   ./setup.sh
   ```
   
## OR

1. **Create a virtual environment:**

   ```bash
   python3 -m venv .venv
   ```

2. **Activate the virtual environment:**

   ```bash
   source .venv/bin/activate
   ```

3. **Install required Python packages:**

   ```bash
   pip install requests openpyxl
   ```

4. **Obtain a GitHub personal access token from your GitHub account:**

   * Go to GitHub Settings → Developer Settings → Personal Access Tokens.
   * Generate a new token with `repo` permissions.

5. **Modify the `GITHUB_TOKEN` and `USERNAME` in the script with your GitHub details:**

   ```python
   GITHUB_TOKEN = "your_token_here"  # Replace with your GitHub personal access token
   USERNAME = "your_github_username"  # Replace with your GitHub username
   ```

6. **Optionally, modify the `IGNORE_AUTHORS` list in the script:**

   ```python
   IGNORE_AUTHORS = ['author1', 'author2']
   ```

---

## Handling SAML Enforcement (403 Error)

If you receive a `403 - Resource protected by organization SAML enforcement` error:

1. **Grant your PAT access to the organization:**

   * Visit: `https://github.com/organizations/<your-organization-name>/settings/saml`
   * Authorize your PAT for organization access.

2. **Generate a new PAT (if needed):**

   * Visit: [GitHub Personal Access Tokens](https://github.com/settings/tokens)
   * Enable `repo` and `read:org` scopes.

3. **Ensure SAML SSO Authorization:**

   * Explicitly authorize your token for SSO access if your organization enforces SAML.

---

## How to Run

```bash
python fetch_pr_comments.py --org <organization_name> --repo <repository_name>
```

Incase it gives error while running like:
```Traceback (most recent call last):
  File "/home/evertz/Desktop/fetch_pr_comments/fetch_pr_comments.py", line 4, in <module>
    import openpyxl
ModuleNotFoundError: No module named 'openpyxl'
```
Try running : `source .venv/bin/activate` 
and then run the above ones

### Optional Flags

* `--reviews-only` – Fetch only review comments.
* `--issues-only` – Fetch only issue comments.
* `--ignore-authors <author1> <author2> ...` – List of authors to exclude.
* `--only-authors <author1> <author2> ...` – List of authors to include exclusively.
* `--days-back <number>` – Days to look back for comments (default: 365).

---

### Some Hardcoded values
* `DAYS_BACK = 365`
* `IGNORE_AUTHORS = [USERNAME,'filebased-rnd-tools']`  # Default authors to ignore
* `DEFAULT_ORG = 'evertz-fbrnd'`  # Default GitHub organization
* `DEFAULT_REPO = 'evertz'`  # Default GitHub repository

## Examples

### 1. Fetch all comments (reviews + issues) for the last 1 year:

```bash
python fetch_pr_comments.py --org my-org --repo my-repo
```

If `org` and `repo` are set to defaults in the script:

```bash
python fetch_pr_comments.py
```

---

### 2. Fetch only review comments:

```bash
python fetch_pr_comments.py --reviews-only --org my-org --repo my-repo
```

Or using defaults:

```bash
python fetch_pr_comments.py --reviews-only
```

---

### 3. Fetch only issue comments:

```bash
python fetch_pr_comments.py --issues-only --org my-org --repo my-repo
```

---

### 4. Fetch comments from the past 90 days:

```bash
python fetch_pr_comments.py --days-back 90
```

---

### 5. Fetch only from specific authors:

```bash
python fetch_pr_comments.py --only-authors author1 author2
```

---

### 6. Exclude comments from specific authors:

```bash
python fetch_pr_comments.py --ignore-authors author3 author4
```

---

### 7. Combine filters for specific authors and recent comments:

```bash
python fetch_pr_comments.py --reviews-only --only-authors author1 author2 --days-back 30
```

---

### 8. Exclude authors with date filter:

```bash
python fetch_pr_comments.py --ignore-authors author3 author4 --days-back 180
```

---

## Output

* `comments.json` – All comment data in JSON format.
* `comments.xlsx` – Same data in Excel spreadsheet format.

## JSON Structure

Each object in the JSON file includes:

* `repo`
* `pr_number`
* `pr_title`
* `pr_url`
* `comment_author`
* `comment_body`
* `comment_url`
* `created_at`

## Rate Limiting

GitHub’s API allows 5000 authenticated requests per hour. The script will pause if this limit is reached.

## Troubleshooting

* **403 Error** – Ensure PAT is SAML-authorized.
* **Missing Comments** – Check for comments with missing user fields.
