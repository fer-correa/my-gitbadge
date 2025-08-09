import yaml
import os
import requests

def get_version():
    """Reads the version from the VERSION file."""
    with open("VERSION", "r") as f:
        return f.read().strip()

def load_config():
    """Loads the configuration from config.yml."""
    print("Loading configuration...")
    with open("config.yml", "r") as f:
        config = yaml.safe_load(f)
    print("Configuration loaded successfully.")
    return config

def get_repos_from_org(organization, token):
    """Fetches all public repository names for a given organization."""
    print(f"Fetching repositories for organization: {organization}...")
    repos = []
    url = f"https://api.github.com/orgs/{organization}/repos?type=public&per_page=100"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    while url:
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            raise Exception(f"Failed to fetch repos for {organization}. Status: {response.status_code}, Body: {response.text}")
        
        repos.extend([repo["full_name"] for repo in response.json()])
        
        # Handle pagination
        if 'next' in response.links:
            url = response.links['next']['url']
        else:
            url = None
            
    print(f"Found {len(repos)} public repositories for {organization}.")
    return repos

def fetch_contributions(github_user, repositories, token):
    """Fetches contribution data from the GitHub API."""
    print("Fetching contributions...")
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    stats = {
        "commits": 0,
        "prs": 0,
        "issues": 0
    }

    for repo in repositories:
        print(f"Fetching data for repository: {repo}")
        
        # Fetch commits
        url = f"https://api.github.com/repos/{repo}/commits?author={github_user}"
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            stats["commits"] += len(response.json())
        else:
            print(f"Warning: Could not fetch commits for {repo}. Status: {response.status_code}")

        # Fetch pull requests
        url = f"https://api.github.com/search/issues?q=is:pr+author:{github_user}+repo:{repo}"
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            stats["prs"] += response.json().get("total_count", 0)
        else:
            print(f"Warning: Could not fetch PRs for {repo}. Status: {response.status_code}")

        # Fetch issues
        url = f"https://api.github.com/search/issues?q=is:issue+author:{github_user}+repo:{repo}"
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            stats["issues"] += response.json().get("total_count", 0)
        else:
            print(f"Warning: Could not fetch issues for {repo}. Status: {response.status_code}")

    print("Finished fetching contributions.")
    return stats

def generate_badge(stats, label="contributions"):
    """Generates an SVG badge from the contribution stats."""
    print("Generating SVG badge...")
    value = f"{stats['commits']} commits | {stats['prs']} PRs | {stats['issues']} issues"

    # Simple width calculation (approximate)
    label_width = len(label) * 7
    value_width = len(value) * 6
    total_width = label_width + value_width

    svg_template = f'''
    <svg xmlns="http://www.w3.org/2000/svg" width="{total_width}" height="20" role="img" aria-label="{label}: {value}">
        <title>{label}: {value}</title>
        <linearGradient id="s" x2="0" y2="100%">
            <stop offset="0" stop-color="#bbb" stop-opacity=".1"/>
            <stop offset="1" stop-opacity=".1"/>
        </linearGradient>
        <clipPath id="r">
            <rect width="{total_width}" height="20" rx="3" fill="#fff"/>
        </clipPath>
        <g clip-path="url(#r)">
            <rect width="{label_width}" height="20" fill="#555"/>
            <rect x="{label_width}" width="{value_width}" height="20" fill="#007ec6"/>
            <rect width="{total_width}" height="20" fill="url(#s)"/>
        </g>
        <g fill="#fff" text-anchor="middle" font-family="Verdana,Geneva,DejaVu Sans,sans-serif" text-rendering="geometricPrecision" font-size="110">
            <text aria-hidden="true" x="{label_width * 5}" y="150" fill="#010101" fill-opacity=".3" transform="scale(.1)" textLength="{label_width * 9}">{label}</text>
            <text x="{label_width * 5}" y="140" transform="scale(.1)" fill="#fff" textLength="{label_width * 9}">{label}</text>
            <text aria-hidden="true" x="{(label_width + value_width / 2) * 10}" y="150" fill="#010101" fill-opacity=".3" transform="scale(.1)" textLength="{value_width * 9}">{value}</text>
            <text x="{(label_width + value_width / 2) * 10}" y="140" transform="scale(.1)" fill="#fff" textLength="{value_width * 9}">{value}</text>
        </g>
    </svg>
    '''

    with open("badge.svg", "w") as f:
        f.write(svg_template)
    print("SVG badge 'badge.svg' created successfully.")

def main():
    """Main function to run the badge generation logic."""
    version = get_version()
    print(f"my-gitbadge v{version} starting...")
    
    config = load_config()
    github_user = config.get("github_user")
    organization = config.get("organization")
    repositories = config.get("repositories")
    token = os.getenv("GH_TOKEN")

    if not github_user:
        raise ValueError("Missing 'github_user' in config.yml")
    if not token:
        raise ValueError("GitHub token not found. Please set the GH_TOKEN environment variable.")

    badge_label = "contributions"
    
    if organization:
        print(f"Organization mode enabled for: {organization}")
        repositories = get_repos_from_org(organization, token)
        badge_label = f"contributions in {organization}"
    elif not repositories:
        raise ValueError("Missing 'repositories' or 'organization' in config.yml")

    print(f"GitHub User: {github_user}")
    print(f"Processing {len(repositories)} repositories...")

    contribution_stats = fetch_contributions(github_user, repositories, token)

    print("\n--- Contribution Stats ---")
    print(f"Commits: {contribution_stats['commits']}")
    print(f"Pull Requests: {contribution_stats['prs']}")
    print(f"Issues: {contribution_stats['issues']}")
    print("--------------------------\n")

    generate_badge(contribution_stats, label=badge_label)

    print("Badge generation script finished.")

if __name__ == "__main__":
    main()
