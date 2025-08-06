"""
Pytest configuration and fixtures for xrayclient tests.
"""
import os
import pytest
from unittest.mock import Mock, patch
from xrayclient.xray_client import XrayGraphQL, JiraHandler

#JIRA_AND_XRAYSERVER_DETAILS
os.environ['JIRA_SERVER'] = 'https://arusa.atlassian.net'
os.environ['JIRA_USER'] = 'yakub@arusatech.com'
os.environ['JIRA_API_KEY'] = '<API_KEY>'
os.environ['XRAY_CLIENT_ID'] = '<CLIENT_ID>'
os.environ['XRAY_CLIENT_SECRET'] = '<CLIENT_SECRET>'
os.environ['XRAY_BASE_URL'] = 'https://xray.cloud.getxray.app'

@pytest.fixture
def mock_env_vars():
    """Mock environment variables for testing."""
    env_vars = {
        'JIRA_SERVER': 'https://arusa.atlassian.net/',
        'JIRA_USER': 'yakub@arusatech.com',
        'JIRA_API_KEY': '<API_KEY>',
        'XRAY_CLIENT_ID': '<CLIENT_ID>',
        'XRAY_CLIENT_SECRET': '<CLIENT_SECRET>',
        'XRAY_BASE_URL': 'https://xray.cloud.getxray.app'
    }
    
    with patch.dict(os.environ, env_vars):
        yield env_vars


@pytest.fixture
def mock_jira_client():
    """Mock JIRA client for testing."""
    mock_client = Mock()
    mock_client.create_issue.return_value = Mock(key="TEST-123", id="10001")
    mock_client.issue.return_value = Mock(
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
    return mock_client


@pytest.fixture
def mock_xray_client(mock_env_vars):
    """Mock XrayGraphQL client for testing."""
    with patch('xrayclient.xray_client.JIRA') as mock_jira:
        mock_jira.return_value = Mock()
        with patch('xrayclient.xray_client.requests.post') as mock_post:
            # Mock authentication response
            mock_auth_response = Mock()
            mock_auth_response.text = '"test_auth_token"'
            mock_auth_response.raise_for_status.return_value = None
            
            # Mock GraphQL response
            mock_graphql_response = Mock()
            mock_graphql_response.json.return_value = {
                'data': {
                    'getTestPlan': {
                        'issueId': '10001',
                        'tests': {
                            'results': [
                                {'issueId': '10002', 'jira': {'key': 'XSP1-54321'}},
                                {'issueId': '10003', 'jira': {'key': 'XSP1-11111'}}
                            ]
                        }
                    }
                }
            }
            mock_graphql_response.raise_for_status.return_value = None
            
            mock_post.side_effect = [mock_auth_response, mock_graphql_response]
            
            client = XrayGraphQL()
            yield client


@pytest.fixture
def test_data():
    """Test data for various test scenarios."""
    return {
        'test_execution': 'XSP1-22222',
        'test_cases': ['XSP1-54321', 'XSP1-11111'],
        'test_plan': 'XSP1-12345',
        'project_key': 'XSP1',
        'test_run_id': 'test_run_12345',
        'evidence_path': '/tmp/test_evidence.png'
    }


@pytest.fixture
def mock_graphql_responses():
    """Mock GraphQL responses for different operations."""
    return {
        'get_issue_id': {
            'getTestPlans': {
                'results': [
                    {'issueId': '10001', 'jira': {'key': 'XSP1-12345'}}
                ]
            }
        },
        'get_test_execution': {
            'getTestExecution': {
                'issueId': '10002',
                'tests': {
                    'results': [
                        {'issueId': '10003', 'jira': {'key': 'XSP1-54321'}},
                        {'issueId': '10004', 'jira': {'key': 'XSP1-11111'}}
                    ]
                }
            }
        },
        'get_test_run_status': {
            'getTestRun': {
                'id': 'test_run_12345',
                'status': {'name': 'PASS'}
            }
        },
        'create_test_execution': {
            'createTestExecution': {
                'testExecution': {
                    'issueId': '10005',
                    'jira': {'key': 'XSP1-22222'},
                    'testRuns': {
                        'results': [
                            {
                                'id': 'test_run_12345',
                                'test': {
                                    'issueId': '10003',
                                    'jira': {'key': 'XSP1-54321'}
                                }
                            },
                            {
                                'id': 'test_run_12346',
                                'test': {
                                    'issueId': '10004',
                                    'jira': {'key': 'XSP1-11111'}
                                }
                            }
                        ]
                    }
                }
            }
        }
    } 