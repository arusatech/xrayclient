"""
Tests for XrayGraphQL class functionality.
"""
import pytest
import base64
from unittest.mock import Mock, patch, MagicMock, mock_open
from xrayclient.xray_client import XrayGraphQL


class TestXrayGraphQL:
    """Test cases for XrayGraphQL class."""
    
    def test_init_success(self, mock_env_vars):
        """Test successful XrayGraphQL initialization."""
        with patch('xrayclient.xray_client.JIRA') as mock_jira:
            mock_jira.return_value = Mock()
            with patch('xrayclient.xray_client.requests.post') as mock_post:
                mock_response = Mock()
                mock_response.text = '"test_auth_token"'
                mock_response.raise_for_status.return_value = None
                mock_post.return_value = mock_response
                
                client = XrayGraphQL()
                
                assert client.client_id == 'test_client_id'
                assert client.client_secret == 'test_client_secret'
                assert client.xray_base_url == 'https://test.xray.cloud.getxray.app'
                assert client.token == 'test_auth_token'
    
    def test_init_missing_client_id(self):
        """Test XrayGraphQL initialization with missing client ID."""
        with patch.dict('os.environ', {'XRAY_CLIENT_SECRET': 'test_secret'}):
            with pytest.raises(ValueError, match="XRAY_CLIENT_ID environment variable is required"):
                XrayGraphQL()
    
    def test_init_missing_client_secret(self):
        """Test XrayGraphQL initialization with missing client secret."""
        with patch.dict('os.environ', {'XRAY_CLIENT_ID': 'test_id'}):
            with pytest.raises(ValueError, match="XRAY_CLIENT_SECRET environment variable is required"):
                XrayGraphQL()
    
    def test_get_auth_token_success(self, mock_env_vars):
        """Test successful authentication token retrieval."""
        with patch('xrayclient.xray_client.JIRA') as mock_jira:
            mock_jira.return_value = Mock()
            with patch('xrayclient.xray_client.requests.post') as mock_post:
                mock_response = Mock()
                mock_response.text = '"test_auth_token"'
                mock_response.raise_for_status.return_value = None
                mock_post.return_value = mock_response
                
                client = XrayGraphQL()
                token = client._get_auth_token()
                
                assert token == 'test_auth_token'
                mock_post.assert_called_once()
    
    def test_get_auth_token_failure(self, mock_env_vars):
        """Test authentication token retrieval failure."""
        with patch('xrayclient.xray_client.JIRA') as mock_jira:
            mock_jira.return_value = Mock()
            with patch('xrayclient.xray_client.requests.post') as mock_post:
                mock_post.side_effect = Exception("Auth failed")
                
                client = XrayGraphQL()
                token = client._get_auth_token()
                
                assert token is None
    
    def test_make_graphql_request_success(self, mock_env_vars):
        """Test successful GraphQL request."""
        with patch('xrayclient.xray_client.JIRA') as mock_jira:
            mock_jira.return_value = Mock()
            with patch('xrayclient.xray_client.requests.post') as mock_post:
                # Auth response
                mock_auth_response = Mock()
                mock_auth_response.text = '"test_auth_token"'
                mock_auth_response.raise_for_status.return_value = None
                
                # GraphQL response
                mock_graphql_response = Mock()
                mock_graphql_response.json.return_value = {
                    'data': {'test': 'success'}
                }
                mock_graphql_response.raise_for_status.return_value = None
                
                mock_post.side_effect = [mock_auth_response, mock_graphql_response]
                
                client = XrayGraphQL()
                result = client._make_graphql_request("query { test }", {})
                
                assert result == {'test': 'success'}
    
    def test_make_graphql_request_with_errors(self, mock_env_vars):
        """Test GraphQL request with errors in response."""
        with patch('xrayclient.xray_client.JIRA') as mock_jira:
            mock_jira.return_value = Mock()
            with patch('xrayclient.xray_client.requests.post') as mock_post:
                # Auth response
                mock_auth_response = Mock()
                mock_auth_response.text = '"test_auth_token"'
                mock_auth_response.raise_for_status.return_value = None
                
                # GraphQL response with errors
                mock_graphql_response = Mock()
                mock_graphql_response.json.return_value = {
                    'data': None,
                    'errors': ['GraphQL error']
                }
                mock_graphql_response.raise_for_status.return_value = None
                
                mock_post.side_effect = [mock_auth_response, mock_graphql_response]
                
                client = XrayGraphQL()
                result = client._make_graphql_request("query { test }", {})
                
                assert result is None
    
    def test_get_issue_id_from_jira_id_success(self, mock_env_vars):
        """Test successful issue ID retrieval from JIRA key."""
        with patch('xrayclient.xray_client.JIRA') as mock_jira:
            mock_jira.return_value = Mock()
            with patch('xrayclient.xray_client.requests.post') as mock_post:
                # Auth response
                mock_auth_response = Mock()
                mock_auth_response.text = '"test_auth_token"'
                mock_auth_response.raise_for_status.return_value = None
                
                # GraphQL response
                mock_graphql_response = Mock()
                mock_graphql_response.json.return_value = {
                    'data': {
                        'getTestPlans': {
                            'results': [
                                {'issueId': '10001', 'jira': {'key': 'XSP1-12345'}}
                            ]
                        }
                    }
                }
                mock_graphql_response.raise_for_status.return_value = None
                
                mock_post.side_effect = [mock_auth_response, mock_graphql_response]
                
                client = XrayGraphQL()
                result = client.get_issue_id_from_jira_id('XSP1-12345', 'plan')
                
                assert result == '10001'
    
    def test_get_issue_id_from_jira_id_not_found(self, mock_env_vars):
        """Test issue ID retrieval when issue not found."""
        with patch('xrayclient.xray_client.JIRA') as mock_jira:
            mock_jira.return_value = Mock()
            with patch('xrayclient.xray_client.requests.post') as mock_post:
                # Auth response
                mock_auth_response = Mock()
                mock_auth_response.text = '"test_auth_token"'
                mock_auth_response.raise_for_status.return_value = None
                
                # GraphQL response
                mock_graphql_response = Mock()
                mock_graphql_response.json.return_value = {
                    'data': {
                        'getTestPlans': {
                            'results': []
                        }
                    }
                }
                mock_graphql_response.raise_for_status.return_value = None
                
                mock_post.side_effect = [mock_auth_response, mock_graphql_response]
                
                client = XrayGraphQL()
                result = client.get_issue_id_from_jira_id('XSP1-99999', 'plan')
                
                assert result is None
    
    def test_get_tests_from_test_plan_success(self, mock_env_vars):
        """Test successful retrieval of tests from test plan."""
        with patch('xrayclient.xray_client.JIRA') as mock_jira:
            mock_jira.return_value = Mock()
            with patch('xrayclient.xray_client.requests.post') as mock_post:
                # Auth response
                mock_auth_response = Mock()
                mock_auth_response.text = '"test_auth_token"'
                mock_auth_response.raise_for_status.return_value = None
                
                # First GraphQL response (get issue ID)
                mock_id_response = Mock()
                mock_id_response.json.return_value = {
                    'data': {
                        'getTestPlans': {
                            'results': [
                                {'issueId': '10001', 'jira': {'key': 'XSP1-12345'}}
                            ]
                        }
                    }
                }
                mock_id_response.raise_for_status.return_value = None
                
                # Second GraphQL response (get tests)
                mock_tests_response = Mock()
                mock_tests_response.json.return_value = {
                    'data': {
                        'getTestPlan': {
                            'tests': {
                                'results': [
                                    {'issueId': '10002', 'jira': {'key': 'XSP1-54321'}},
                                    {'issueId': '10003', 'jira': {'key': 'XSP1-11111'}}
                                ]
                            }
                        }
                    }
                }
                mock_tests_response.raise_for_status.return_value = None
                
                mock_post.side_effect = [mock_auth_response, mock_id_response, mock_tests_response]
                
                client = XrayGraphQL()
                result = client.get_tests_from_test_plan('XSP1-12345')
                
                expected = {
                    'XSP1-54321': '10002',
                    'XSP1-11111': '10003'
                }
                assert result == expected
    
    def test_get_tests_from_test_execution_success(self, mock_env_vars):
        """Test successful retrieval of tests from test execution."""
        with patch('xrayclient.xray_client.JIRA') as mock_jira:
            mock_jira.return_value = Mock()
            with patch('xrayclient.xray_client.requests.post') as mock_post:
                # Auth response
                mock_auth_response = Mock()
                mock_auth_response.text = '"test_auth_token"'
                mock_auth_response.raise_for_status.return_value = None
                
                # First GraphQL response (get issue ID)
                mock_id_response = Mock()
                mock_id_response.json.return_value = {
                    'data': {
                        'getTestExecutions': {
                            'results': [
                                {'issueId': '10001', 'jira': {'key': 'XSP1-22222'}}
                            ]
                        }
                    }
                }
                mock_id_response.raise_for_status.return_value = None
                
                # Second GraphQL response (get tests)
                mock_tests_response = Mock()
                mock_tests_response.json.return_value = {
                    'data': {
                        'getTestExecution': {
                            'tests': {
                                'results': [
                                    {'issueId': '10002', 'jira': {'key': 'XSP1-54321'}},
                                    {'issueId': '10003', 'jira': {'key': 'XSP1-11111'}}
                                ]
                            }
                        }
                    }
                }
                mock_tests_response.raise_for_status.return_value = None
                
                mock_post.side_effect = [mock_auth_response, mock_id_response, mock_tests_response]
                
                client = XrayGraphQL()
                result = client.get_tests_from_test_execution('XSP1-22222')
                
                expected = {
                    'XSP1-54321': '10002',
                    'XSP1-11111': '10003'
                }
                assert result == expected
    
    def test_get_test_runstatus_success(self, mock_env_vars):
        """Test successful retrieval of test run status."""
        with patch('xrayclient.xray_client.JIRA') as mock_jira:
            mock_jira.return_value = Mock()
            with patch('xrayclient.xray_client.requests.post') as mock_post:
                # Auth response
                mock_auth_response = Mock()
                mock_auth_response.text = '"test_auth_token"'
                mock_auth_response.raise_for_status.return_value = None
                
                # First GraphQL response (get test case ID)
                mock_test_id_response = Mock()
                mock_test_id_response.json.return_value = {
                    'data': {
                        'getTests': {
                            'results': [
                                {'issueId': '10002', 'jira': {'key': 'XSP1-54321'}}
                            ]
                        }
                    }
                }
                mock_test_id_response.raise_for_status.return_value = None
                
                # Second GraphQL response (get test execution ID)
                mock_exec_id_response = Mock()
                mock_exec_id_response.json.return_value = {
                    'data': {
                        'getTestExecutions': {
                            'results': [
                                {'issueId': '10001', 'jira': {'key': 'XSP1-22222'}}
                            ]
                        }
                    }
                }
                mock_exec_id_response.raise_for_status.return_value = None
                
                # Third GraphQL response (get test run status)
                mock_status_response = Mock()
                mock_status_response.json.return_value = {
                    'data': {
                        'getTestRun': {
                            'id': 'test_run_12345',
                            'status': {'name': 'PASS'}
                        }
                    }
                }
                mock_status_response.raise_for_status.return_value = None
                
                mock_post.side_effect = [
                    mock_auth_response, 
                    mock_test_id_response, 
                    mock_exec_id_response, 
                    mock_status_response
                ]
                
                client = XrayGraphQL()
                result = client.get_test_runstatus('XSP1-54321', 'XSP1-22222')
                
                assert result == ('test_run_12345', 'PASS')
    
    def test_update_test_run_status_success(self, mock_env_vars):
        """Test successful test run status update."""
        with patch('xrayclient.xray_client.JIRA') as mock_jira:
            mock_jira.return_value = Mock()
            with patch('xrayclient.xray_client.requests.post') as mock_post:
                # Auth response
                mock_auth_response = Mock()
                mock_auth_response.text = '"test_auth_token"'
                mock_auth_response.raise_for_status.return_value = None
                
                # GraphQL response
                mock_graphql_response = Mock()
                mock_graphql_response.json.return_value = {
                    'data': {
                        'updateTestRunStatus': True
                    }
                }
                mock_graphql_response.raise_for_status.return_value = None
                
                mock_post.side_effect = [mock_auth_response, mock_graphql_response]
                
                client = XrayGraphQL()
                result = client.update_test_run_status('test_run_12345', 'PASS')
                
                assert result is True
    
    def test_update_test_run_comment_success(self, mock_env_vars):
        """Test successful test run comment update."""
        with patch('xrayclient.xray_client.JIRA') as mock_jira:
            mock_jira.return_value = Mock()
            with patch('xrayclient.xray_client.requests.post') as mock_post:
                # Auth response
                mock_auth_response = Mock()
                mock_auth_response.text = '"test_auth_token"'
                mock_auth_response.raise_for_status.return_value = None
                
                # GraphQL response
                mock_graphql_response = Mock()
                mock_graphql_response.json.return_value = {
                    'data': {
                        'updateTestRunComment': True
                    }
                }
                mock_graphql_response.raise_for_status.return_value = None
                
                mock_post.side_effect = [mock_auth_response, mock_graphql_response]
                
                client = XrayGraphQL()
                result = client.update_test_run_comment('test_run_12345', 'Test passed successfully')
                
                assert result is True
    
    def test_add_evidence_to_test_run_success(self, mock_env_vars):
        """Test successful evidence addition to test run."""
        with patch('xrayclient.xray_client.JIRA') as mock_jira:
            mock_jira.return_value = Mock()
            with patch('xrayclient.xray_client.requests.post') as mock_post:
                with patch('os.path.exists', return_value=True):
                    with patch('builtins.open', mock_open(read_data=b'test_evidence_data')):
                        with patch('mimetypes.guess_type', return_value=('image/png', None)):
                            # Auth response
                            mock_auth_response = Mock()
                            mock_auth_response.text = '"test_auth_token"'
                            mock_auth_response.raise_for_status.return_value = None
                            
                            # GraphQL response
                            mock_graphql_response = Mock()
                            mock_graphql_response.json.return_value = {
                                'data': {
                                    'addEvidenceToTestRun': {
                                        'addedEvidence': ['evidence_123'],
                                        'warnings': []
                                    }
                                }
                            }
                            mock_graphql_response.raise_for_status.return_value = None
                            
                            mock_post.side_effect = [mock_auth_response, mock_graphql_response]
                            
                            client = XrayGraphQL()
                            result = client.add_evidence_to_test_run('test_run_12345', '/tmp/test_evidence.png')
                            
                            assert result == {
                                'addedEvidence': ['evidence_123'],
                                'warnings': []
                            }
    
    def test_create_test_execution_success(self, mock_env_vars):
        """Test successful test execution creation."""
        with patch('xrayclient.xray_client.JIRA') as mock_jira:
            mock_jira.return_value = Mock()
            with patch('xrayclient.xray_client.requests.post') as mock_post:
                # Auth response
                mock_auth_response = Mock()
                mock_auth_response.text = '"test_auth_token"'
                mock_auth_response.raise_for_status.return_value = None
                
                # First GraphQL response (get test IDs)
                mock_test_ids_response = Mock()
                mock_test_ids_response.json.return_value = {
                    'data': {
                        'getTests': {
                            'results': [
                                {'issueId': '10002', 'jira': {'key': 'XSP1-54321'}},
                                {'issueId': '10003', 'jira': {'key': 'XSP1-11111'}}
                            ]
                        }
                    }
                }
                mock_test_ids_response.raise_for_status.return_value = None
                
                # Second GraphQL response (create test execution)
                mock_create_response = Mock()
                mock_create_response.json.return_value = {
                    'data': {
                        'createTestExecution': {
                            'testExecution': {
                                'issueId': '10005',
                                'jira': {'key': 'XSP1-22222'}
                            }
                        }
                    }
                }
                mock_create_response.raise_for_status.return_value = None
                
                mock_post.side_effect = [mock_auth_response, mock_test_ids_response, mock_create_response]
                
                client = XrayGraphQL()
                result = client.create_test_execution(
                    test_issue_keys=['XSP1-54321', 'XSP1-11111'],
                    project_key='XSP1',
                    summary='Test Execution for XSP1-12345'
                )
                
                assert result == {
                    'issueId': '10005',
                    'jira': {'key': 'XSP1-22222'}
                }
    
    def test_create_test_execution_from_test_plan_success(self, mock_env_vars):
        """Test successful test execution creation from test plan."""
        with patch('xrayclient.xray_client.JIRA') as mock_jira:
            mock_jira.return_value = Mock()
            with patch('xrayclient.xray_client.requests.post') as mock_post:
                # Auth response
                mock_auth_response = Mock()
                mock_auth_response.text = '"test_auth_token"'
                mock_auth_response.raise_for_status.return_value = None
                
                # First GraphQL response (get test plan ID)
                mock_plan_id_response = Mock()
                mock_plan_id_response.json.return_value = {
                    'data': {
                        'getTestPlans': {
                            'results': [
                                {'issueId': '10001', 'jira': {'key': 'XSP1-12345'}}
                            ]
                        }
                    }
                }
                mock_plan_id_response.raise_for_status.return_value = None
                
                # Second GraphQL response (get tests from plan)
                mock_tests_response = Mock()
                mock_tests_response.json.return_value = {
                    'data': {
                        'getTestPlan': {
                            'tests': {
                                'results': [
                                    {'issueId': '10002', 'jira': {'key': 'XSP1-54321'}},
                                    {'issueId': '10003', 'jira': {'key': 'XSP1-11111'}}
                                ]
                            }
                        }
                    }
                }
                mock_tests_response.raise_for_status.return_value = None
                
                # Third GraphQL response (create test execution)
                mock_create_response = Mock()
                mock_create_response.json.return_value = {
                    'data': {
                        'createTestExecution': {
                            'testExecution': {
                                'issueId': '10005',
                                'jira': {'key': 'XSP1-22222'},
                                'testRuns': {
                                    'results': [
                                        {
                                            'id': 'test_run_12345',
                                            'test': {
                                                'issueId': '10002',
                                                'jira': {'key': 'XSP1-54321'}
                                            }
                                        },
                                        {
                                            'id': 'test_run_12346',
                                            'test': {
                                                'issueId': '10003',
                                                'jira': {'key': 'XSP1-11111'}
                                            }
                                        }
                                    ]
                                }
                            }
                        }
                    }
                }
                mock_create_response.raise_for_status.return_value = None
                
                # Fourth GraphQL response (add to test plan)
                mock_add_response = Mock()
                mock_add_response.json.return_value = {
                    'data': {
                        'addTestExecutionsToTestPlan': {
                            'addedTestExecutions': ['10005'],
                            'warning': None
                        }
                    }
                }
                mock_add_response.raise_for_status.return_value = None
                
                mock_post.side_effect = [
                    mock_auth_response, 
                    mock_plan_id_response, 
                    mock_tests_response, 
                    mock_create_response,
                    mock_add_response
                ]
                
                client = XrayGraphQL()
                result = client.create_test_execution_from_test_plan('XSP1-12345')
                
                expected = {
                    'XSP1-54321': {
                        'test_run_id': 'test_run_12345',
                        'test_execution_key': 'XSP1-22222',
                        'test_plan_key': 'XSP1-12345'
                    },
                    'XSP1-11111': {
                        'test_run_id': 'test_run_12346',
                        'test_execution_key': 'XSP1-22222',
                        'test_plan_key': 'XSP1-12345'
                    }
                }
                assert result == expected
    
    def test_parse_table_success(self, mock_env_vars):
        """Test successful table parsing."""
        with patch('xrayclient.xray_client.JIRA') as mock_jira:
            mock_jira.return_value = Mock()
            with patch('xrayclient.xray_client.requests.post') as mock_post:
                mock_response = Mock()
                mock_response.text = '"test_auth_token"'
                mock_response.raise_for_status.return_value = None
                mock_post.return_value = mock_response
                
                client = XrayGraphQL()
                
                table_str = """header1 || header2 || header3
                |temp   |[1, 2, 3]    |42       |
                |value  |[4, 5, 6]    |100      |"""
                
                result = client._parse_table(table_str)
                
                expected = {
                    'temp': [[1, 2, 3], 42],
                    'value': [[4, 5, 6], 100]
                }
                assert result == expected
    
    def test_parse_table_empty(self, mock_env_vars):
        """Test table parsing with empty input."""
        with patch('xrayclient.xray_client.JIRA') as mock_jira:
            mock_jira.return_value = Mock()
            with patch('xrayclient.xray_client.requests.post') as mock_post:
                mock_response = Mock()
                mock_response.text = '"test_auth_token"'
                mock_response.raise_for_status.return_value = None
                mock_post.return_value = mock_response
                
                client = XrayGraphQL()
                result = client._parse_table("")
                
                assert result == {}
    
    def test_get_test_plan_data_success(self, mock_env_vars):
        """Test successful test plan data retrieval."""
        with patch('xrayclient.xray_client.JIRA') as mock_jira:
            mock_jira.return_value = Mock()
            with patch('xrayclient.xray_client.requests.post') as mock_post:
                # Auth response
                mock_auth_response = Mock()
                mock_auth_response.text = '"test_auth_token"'
                mock_auth_response.raise_for_status.return_value = None
                
                # First GraphQL response (get test plan ID)
                mock_plan_id_response = Mock()
                mock_plan_id_response.json.return_value = {
                    'data': {
                        'getTestPlans': {
                            'results': [
                                {'issueId': '10001', 'jira': {'key': 'XSP1-12345'}}
                            ]
                        }
                    }
                }
                mock_plan_id_response.raise_for_status.return_value = None
                
                # Second GraphQL response (get test plan data)
                mock_data_response = Mock()
                mock_data_response.json.return_value = {
                    'data': {
                        'getTestPlan': {
                            'issueId': '10001',
                            'jira': {
                                'key': 'XSP1-12345',
                                'description': """header1 || header2
                                |temp   |[1, 2, 3]|
                                |value  |42       |"""
                            }
                        }
                    }
                }
                mock_data_response.raise_for_status.return_value = None
                
                mock_post.side_effect = [mock_auth_response, mock_plan_id_response, mock_data_response]
                
                client = XrayGraphQL()
                result = client.get_test_plan_data('XSP1-12345')
                
                expected = {
                    'temp': [[1, 2, 3]],
                    'value': [42]
                }
                assert result == expected 