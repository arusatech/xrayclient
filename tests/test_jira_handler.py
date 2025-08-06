"""
Tests for JiraHandler class functionality.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from xrayclient.xray_client import JiraHandler


class TestJiraHandler:
    """Test cases for JiraHandler class."""
    
    def test_init_success(self, mock_env_vars):
        """Test successful JiraHandler initialization."""
        with patch('xrayclient.xray_client.JIRA') as mock_jira:
            mock_jira.return_value = Mock()
            handler = JiraHandler()
            
            assert handler.client is not None
            mock_jira.assert_called_once_with(
                server='https://test.atlassian.net',
                basic_auth=('test@example.com', 'test_api_key')
            )
    
    def test_init_missing_api_key(self):
        """Test JiraHandler initialization with missing API key."""
        with patch.dict('os.environ', {}, clear=True):
            with pytest.raises(ValueError, match="JIRA_API_KEY environment variable is required"):
                JiraHandler()
    
    def test_init_invalid_api_key(self):
        """Test JiraHandler initialization with invalid API key."""
        with patch.dict('os.environ', {'JIRA_API_KEY': '<JIRA_API_KEY>'}):
            with pytest.raises(ValueError, match="JIRA_API_KEY environment variable is required"):
                JiraHandler()
    
    def test_create_issue_success(self, mock_env_vars):
        """Test successful issue creation."""
        with patch('xrayclient.xray_client.JIRA') as mock_jira:
            mock_client = Mock()
            mock_issue = Mock(key="TEST-123", id="10001")
            mock_client.create_issue.return_value = mock_issue
            mock_jira.return_value = mock_client
            
            handler = JiraHandler()
            result = handler.create_issue(
                project_key="TEST",
                summary="Test Issue",
                description="Test Description",
                issue_type="Bug",
                priority="High",
                assignee="test@example.com",
                labels=["test", "automation"],
                components=["Test Component"]
            )
            
            assert result == ("TEST-123", "10001")
            mock_client.create_issue.assert_called_once()
    
    def test_create_issue_with_attachments(self, mock_env_vars):
        """Test issue creation with attachments."""
        with patch('xrayclient.xray_client.JIRA') as mock_jira:
            with patch('os.path.exists', return_value=True):
                mock_client = Mock()
                mock_issue = Mock(key="TEST-123", id="10001")
                mock_client.create_issue.return_value = mock_issue
                mock_jira.return_value = mock_client
                
                handler = JiraHandler()
                result = handler.create_issue(
                    project_key="TEST",
                    summary="Test Issue",
                    description="Test Description",
                    attachments=["/tmp/test.png"]
                )
                
                assert result == ("TEST-123", "10001")
                mock_client.add_attachment.assert_called_once_with(
                    issue="TEST-123",
                    attachment="/tmp/test.png"
                )
    
    def test_create_issue_with_linked_issues(self, mock_env_vars):
        """Test issue creation with linked issues."""
        with patch('xrayclient.xray_client.JIRA') as mock_jira:
            mock_client = Mock()
            mock_issue = Mock(key="TEST-123", id="10001")
            mock_client.create_issue.return_value = mock_issue
            mock_jira.return_value = mock_client
            
            handler = JiraHandler()
            result = handler.create_issue(
                project_key="TEST",
                summary="Test Issue",
                description="Test Description",
                linked_issues=[{"key": "TEST-456", "type": "Blocks"}]
            )
            
            assert result == ("TEST-123", "10001")
            mock_client.create_issue_link.assert_called_once_with(
                "Blocks", "TEST-123", "TEST-456"
            )
    
    def test_create_issue_failure(self, mock_env_vars):
        """Test issue creation failure."""
        with patch('xrayclient.xray_client.JIRA') as mock_jira:
            mock_client = Mock()
            mock_client.create_issue.side_effect = Exception("API Error")
            mock_jira.return_value = mock_client
            
            handler = JiraHandler()
            result = handler.create_issue(
                project_key="TEST",
                summary="Test Issue",
                description="Test Description"
            )
            
            assert result == (None, None)
    
    def test_get_issue_success(self, mock_env_vars):
        """Test successful issue retrieval."""
        with patch('xrayclient.xray_client.JIRA') as mock_jira:
            mock_client = Mock()
            mock_issue = Mock(
                key="TEST-123",
                id="10001",
                fields=Mock(
                    summary="Test Issue",
                    description="Test Description",
                    status=Mock(name="Open"),
                    assignee=Mock(name="test@example.com", displayName="Test User"),
                    reporter=Mock(name="reporter@example.com", displayName="Reporter User"),
                    priority=Mock(name="High"),
                    labels=["test", "automation"],
                    components=[Mock(id="10001", name="Test Component")],
                    created="2024-01-01T00:00:00.000Z",
                    updated="2024-01-01T00:00:00.000Z"
                )
            )
            mock_client.issue.return_value = mock_issue
            mock_jira.return_value = mock_client
            
            handler = JiraHandler()
            result = handler.get_issue("TEST-123")
            
            assert result is not None
            assert result['key'] == "TEST-123"
            assert result['id'] == "10001"
            assert result['summary'] == "Test Issue"
            assert result['status']['name'] == "Open"
    
    def test_get_issue_with_specific_fields(self, mock_env_vars):
        """Test issue retrieval with specific fields."""
        with patch('xrayclient.xray_client.JIRA') as mock_jira:
            mock_client = Mock()
            mock_issue = Mock(
                key="TEST-123",
                id="10001",
                fields=Mock(
                    summary="Test Issue",
                    status=Mock(name="Open")
                )
            )
            mock_client.issue.return_value = mock_issue
            mock_jira.return_value = mock_client
            
            handler = JiraHandler()
            result = handler.get_issue("TEST-123", fields=["summary", "status"])
            
            assert result is not None
            assert result['key'] == "TEST-123"
            assert result['summary'] == "Test Issue"
            assert result['status']['name'] == "Open"
            # Should not have other fields
            assert 'description' not in result
    
    def test_get_issue_not_found(self, mock_env_vars):
        """Test issue retrieval when issue not found."""
        with patch('xrayclient.xray_client.JIRA') as mock_jira:
            mock_client = Mock()
            mock_client.issue.return_value = None
            mock_jira.return_value = mock_client
            
            handler = JiraHandler()
            result = handler.get_issue("TEST-999")
            
            assert result is None
    
    def test_get_issue_failure(self, mock_env_vars):
        """Test issue retrieval failure."""
        with patch('xrayclient.xray_client.JIRA') as mock_jira:
            mock_client = Mock()
            mock_client.issue.side_effect = Exception("API Error")
            mock_jira.return_value = mock_client
            
            handler = JiraHandler()
            result = handler.get_issue("TEST-123")
            
            assert result is None
    
    def test_update_issue_summary_success(self, mock_env_vars):
        """Test successful issue summary update."""
        with patch('xrayclient.xray_client.JIRA') as mock_jira:
            mock_client = Mock()
            mock_issue = Mock()
            mock_client.issue.return_value = mock_issue
            mock_jira.return_value = mock_client
            
            handler = JiraHandler()
            result = handler.update_issue_summary("TEST-123", "Updated Summary")
            
            assert result is True
            mock_issue.update.assert_called_once_with(summary="Updated Summary")
    
    def test_update_issue_summary_empty_key(self, mock_env_vars):
        """Test issue summary update with empty key."""
        with patch('xrayclient.xray_client.JIRA') as mock_jira:
            mock_jira.return_value = Mock()
            handler = JiraHandler()
            result = handler.update_issue_summary("", "Updated Summary")
            
            assert result is False
    
    def test_update_issue_summary_empty_summary(self, mock_env_vars):
        """Test issue summary update with empty summary."""
        with patch('xrayclient.xray_client.JIRA') as mock_jira:
            mock_jira.return_value = Mock()
            handler = JiraHandler()
            result = handler.update_issue_summary("TEST-123", "")
            
            assert result is False
    
    def test_update_issue_summary_issue_not_found(self, mock_env_vars):
        """Test issue summary update when issue not found."""
        with patch('xrayclient.xray_client.JIRA') as mock_jira:
            mock_client = Mock()
            mock_client.issue.return_value = None
            mock_jira.return_value = mock_client
            
            handler = JiraHandler()
            result = handler.update_issue_summary("TEST-999", "Updated Summary")
            
            assert result is False
    
    def test_update_issue_summary_failure(self, mock_env_vars):
        """Test issue summary update failure."""
        with patch('xrayclient.xray_client.JIRA') as mock_jira:
            mock_client = Mock()
            mock_issue = Mock()
            mock_issue.update.side_effect = Exception("API Error")
            mock_client.issue.return_value = mock_issue
            mock_jira.return_value = mock_client
            
            handler = JiraHandler()
            result = handler.update_issue_summary("TEST-123", "Updated Summary")
            
            assert result is False 