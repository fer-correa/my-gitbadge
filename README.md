# my-gitbadge v0.2.0

A simple tool to generate a dynamic SVG badge showcasing your contributions to a curated list of GitHub repositories.

## How it works

This project uses a Python script and GitHub Actions to:
1.  Fetch your latest contribution stats (commits, PRs, issues) from the GitHub API for repositories you specify.
2.  Generate an SVG badge with these stats.
3.  Automatically update the badge once a day.

## Setup

1.  **Fork/Clone this repository.**
2.  **Edit `config.yml`:**
    The `config.yml` file allows you to specify whose contributions to track and where to track them. You can operate in one of two modes:

    **Mode 1: Track contributions in specific repositories**
    To track contributions in a specific list of repositories, fill out the `github_user` and `repositories` keys. Leave the `organization` key empty or remove it.

    ```yaml
    github_user: "your-github-username"
    organization: "" # Leave empty or remove
    repositories:
      - "owner1/repo1"
      - "owner2/repo2"
      # Add more repositories here
    ```

    **Mode 2: Track contributions in an entire organization**
    To track contributions across all public repositories of an organization, fill out the `github_user` and `organization` keys. The `repositories` list will be ignored.

    ```yaml
    github_user: "your-github-username"
    organization: "kubernetes" # Example: tracks contributions in all public Kubernetes repos
    repositories:
      # This list is ignored when 'organization' is set
      - "owner1/repo1"
    ```
3.  **Enable GitHub Actions:** Go to the "Actions" tab of your forked repository and enable the workflows. The badge will be generated and updated automatically.
4.  **Provide GitHub Token:** The GitHub Action needs a token to talk to the GitHub API.
    *   Go to `Settings` > `Secrets and variables` > `Actions` in your repository.
    *   Create a new repository secret named `GH_TOKEN`.
    *   The value should be a GitHub Personal Access Token (PAT) with the `public_repo` scope.

## Running Tests

To run the tests locally, first install the development dependencies:

```bash
pip install -r requirements-dev.txt
```

Then, run pytest with the coverage report:

```bash
pytest --cov=generate_badge
```

## Usage

Once the setup is complete and the Action has run at least once, you can add the following Markdown to your GitHub profile's `README.md` or any other Markdown file:

```markdown
![My GitBadge](https://raw.githubusercontent.com/your-github-username/my-gitbadge/main/badge.svg)
```

Remember to replace `your-github-username` with your actual username.

## LICENSE

This project is licensed under the MIT License - see the [LICENSE](./LICENSE) file for details.
