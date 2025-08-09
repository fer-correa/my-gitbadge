# my-gitbadge v0.1.0

A simple tool to generate a dynamic SVG badge showcasing your contributions to a curated list of GitHub repositories.

## How it works

This project uses a Python script and GitHub Actions to:
1.  Fetch your latest contribution stats (commits, PRs, issues) from the GitHub API for repositories you specify.
2.  Generate an SVG badge with these stats.
3.  Automatically update the badge once a day.

## Setup

1.  **Fork/Clone this repository.**
2.  **Edit `config.yml`:**
    ```yaml
    github_user: "your-github-username"
    repositories:
      - "owner1/repo1"
      - "owner2/repo2"
      # Add more repositories here
    ```
    Replace `"your-github-username"` with your actual GitHub username and list the repositories you want to track.
3.  **Enable GitHub Actions:** Go to the "Actions" tab of your forked repository and enable the workflows. The badge will be generated and updated automatically.
4.  **Provide GitHub Token:** The GitHub Action needs a token to talk to the GitHub API.
    *   Go to `Settings` > `Secrets and variables` > `Actions` in your repository.
    *   Create a new repository secret named `GH_TOKEN`.
    *   The value should be a GitHub Personal Access Token (PAT) with the `public_repo` scope.

## Usage

Once the setup is complete and the Action has run at least once, you can add the following Markdown to your GitHub profile's `README.md` or any other Markdown file:

```markdown
![My GitBadge](https://raw.githubusercontent.com/your-github-username/my-gitbadge/main/badge.svg)
```

Remember to replace `your-github-username` with your actual username.