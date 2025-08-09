import os
import yaml
import pytest
from unittest.mock import patch, mock_open, MagicMock

# Add the root of the project to the Python path
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from generate_badge import main, get_version, load_config, generate_badge, get_repos_from_org, fetch_contributions


def test_get_version(tmp_path):
    """Tests that the get_version function reads from a VERSION file."""
    version_file = tmp_path / "VERSION"
    version_file.write_text("0.2.0")
    with patch('builtins.open', mock_open(read_data="0.2.0")) as mock_file:
        assert get_version() == "0.2.0"
        mock_file.assert_called_with("VERSION", "r")

def test_load_config(tmp_path):
    """Tests that the load_config function reads from a config.yml file."""
    config_data = {
        'github_user': 'testuser',
        'organization': 'testorg',
        'repositories': ['test/repo1']
    }
    config_file = tmp_path / "config.yml"
    config_file.write_text(yaml.dump(config_data))

    with patch('builtins.open', mock_open(read_data=yaml.dump(config_data))) as mock_file:
        config = load_config()
        assert config['github_user'] == 'testuser'
        assert config['organization'] == 'testorg'
        mock_file.assert_called_with("config.yml", "r")

def test_generate_badge(tmp_path):
    """Tests that the generate_badge function creates an SVG file with the correct content."""
    stats = {'commits': 10, 'prs': 5, 'issues': 3}
    label = "test contributions"
    
    # Use tmp_path to avoid creating files in the project directory during tests
    output_path = tmp_path / "badge.svg"
    
    with patch('builtins.open', mock_open()) as mocked_file:
        generate_badge(stats, label=label)
        
        # Check that the file was opened for writing at the correct path
        mocked_file.assert_called_once_with('badge.svg', 'w')
        
        # Check the content that was written to the file
        handle = mocked_file()
        written_content = handle.write.call_args[0][0]
        assert '<svg' in written_content
        assert '>test contributions</text>' in written_content
        assert '>10 commits | 5 PRs | 3 issues</text>' in written_content

@patch('requests.get')
def test_get_repos_from_org_single_page(mock_get):
    """Tests fetching repos from an org with a single page of results."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = [
        {'full_name': 'org/repo1'},
        {'full_name': 'org/repo2'}
    ]
    mock_response.links = {}
    mock_get.return_value = mock_response

    repos = get_repos_from_org('testorg', 'faketoken')
    assert repos == ['org/repo1', 'org/repo2']
    mock_get.assert_called_once_with(
        'https://api.github.com/orgs/testorg/repos?type=public&per_page=100',
        headers={"Authorization": "token faketoken", "Accept": "application/vnd.github.v3+json"}
    )

@patch('requests.get')
def test_get_repos_from_org_multiple_pages(mock_get):
    """Tests fetching repos from an org with multiple pages of results."""
    # First response with a 'next' link
    mock_response1 = MagicMock()
    mock_response1.status_code = 200
    mock_response1.json.return_value = [{'full_name': 'org/repo1'}]
    mock_response1.links = {'next': {'url': 'https://api.github.com/page2'}}

    # Second response with no 'next' link
    mock_response2 = MagicMock()
    mock_response2.status_code = 200
    mock_response2.json.return_value = [{'full_name': 'org/repo2'}]
    mock_response2.links = {}

    mock_get.side_effect = [mock_response1, mock_response2]

    repos = get_repos_from_org('testorg', 'faketoken')
    assert repos == ['org/repo1', 'org/repo2']
    assert mock_get.call_count == 2

@patch('requests.get')
def test_fetch_contributions_happy_path(mock_get):
    """Tests the happy path for fetch_contributions where all API calls succeed."""
    # Mock responses for commits, PRs, and issues
    mock_commit_response = MagicMock()
    mock_commit_response.status_code = 200
    mock_commit_response.json.return_value = [{'sha': '123'}, {'sha': '456'}] # 2 commits

    mock_pr_response = MagicMock()
    mock_pr_response.status_code = 200
    mock_pr_response.json.return_value = {'total_count': 3} # 3 PRs

    mock_issue_response = MagicMock()
    mock_issue_response.status_code = 200
    mock_issue_response.json.return_value = {'total_count': 4} # 4 issues

    mock_get.side_effect = [mock_commit_response, mock_pr_response, mock_issue_response]

    stats = fetch_contributions('testuser', ['org/repo1'], 'faketoken')

    assert stats['commits'] == 2
    assert stats['prs'] == 3
    assert stats['issues'] == 4
    assert mock_get.call_count == 3

@patch('requests.get')
def test_get_repos_from_org_api_error(mock_get):
    """Tests that an exception is raised when the API call fails."""
    mock_response = MagicMock()
    mock_response.status_code = 404
    mock_get.return_value = mock_response

    with pytest.raises(Exception, match="Failed to fetch repos for testorg"):
        get_repos_from_org('testorg', 'faketoken')

@patch('requests.get')
def test_fetch_contributions_api_warning(mock_get, capsys):
    """Tests that a warning is printed if one of the API calls fails."""
    mock_commit_response = MagicMock()
    mock_commit_response.status_code = 500  # This call will fail

    mock_pr_response = MagicMock()
    mock_pr_response.status_code = 200
    mock_pr_response.json.return_value = {'total_count': 3}

    mock_issue_response = MagicMock()
    mock_issue_response.status_code = 200
    mock_issue_response.json.return_value = {'total_count': 4}

    mock_get.side_effect = [mock_commit_response, mock_pr_response, mock_issue_response]

    stats = fetch_contributions('testuser', ['org/repo1'], 'faketoken')

    # Assert that the function doesn't crash and returns the stats from the successful calls
    assert stats['commits'] == 0
    assert stats['prs'] == 3
    assert stats['issues'] == 4

    # Assert that a warning was printed to stderr or stdout
    captured = capsys.readouterr()
    assert "Warning: Could not fetch commits" in captured.out

@patch('generate_badge.generate_badge')
@patch('generate_badge.fetch_contributions')
@patch('generate_badge.get_repos_from_org')
@patch('generate_badge.load_config')
@patch('generate_badge.os.getenv')
@patch('generate_badge.get_version')
def test_main_organization_mode(mock_get_version, mock_getenv, mock_load_config, mock_get_repos, mock_fetch, mock_generate):
    """Tests the main function in organization mode."""
    mock_get_version.return_value = "0.2.0"
    mock_getenv.return_value = "faketoken"
    mock_load_config.return_value = {'github_user': 'testuser', 'organization': 'testorg'}
    mock_get_repos.return_value = ['org/repo1', 'org/repo2']
    mock_fetch.return_value = {'commits': 1, 'prs': 2, 'issues': 3}

    main()

    mock_get_repos.assert_called_once_with('testorg', 'faketoken')
    mock_fetch.assert_called_once_with('testuser', ['org/repo1', 'org/repo2'], 'faketoken')
    mock_generate.assert_called_once_with({'commits': 1, 'prs': 2, 'issues': 3}, label='contributions in testorg')

@patch('generate_badge.generate_badge')
@patch('generate_badge.fetch_contributions')
@patch('generate_badge.get_repos_from_org')
@patch('generate_badge.load_config')
@patch('generate_badge.os.getenv')
@patch('generate_badge.get_version')
def test_main_repository_mode(mock_get_version, mock_getenv, mock_load_config, mock_get_repos, mock_fetch, mock_generate):
    """Tests the main function in repository mode."""
    mock_get_version.return_value = "0.2.0"
    mock_getenv.return_value = "faketoken"
    mock_load_config.return_value = {'github_user': 'testuser', 'repositories': ['user/repo']}
    mock_fetch.return_value = {'commits': 1, 'prs': 2, 'issues': 3}

    main()

    mock_get_repos.assert_not_called()
    mock_fetch.assert_called_once_with('testuser', ['user/repo'], 'faketoken')
    mock_generate.assert_called_once_with({'commits': 1, 'prs': 2, 'issues': 3}, label='contributions')

@patch('generate_badge.load_config')
@patch('generate_badge.os.getenv')
@patch('generate_badge.get_version')
def test_main_config_error(mock_get_version, mock_getenv, mock_load_config):
    """Tests that main raises a ValueError if config is missing repos and org."""
    mock_get_version.return_value = "0.2.0"
    mock_getenv.return_value = "faketoken"
    mock_load_config.return_value = {'github_user': 'testuser'} # No org or repos

    with pytest.raises(ValueError, match="Missing 'repositories' or 'organization' in config.yml"):
        main()