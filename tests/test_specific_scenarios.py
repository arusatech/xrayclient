"""
Specific test scenarios for test execution XSP1-22222 and test cases XSP1-54321, XSP1-11111.
"""
import pytest
from unittest.mock import Mock, patch
from xrayclient.xray_client import XrayGraphQL


class TestSpecificScenarios:
    """Specific test scenarios for the mentioned test execution and test cases."""
    
    @pytest.fixture
    def setup_specific_test(self, mock_env_vars):
        """Setup for specific test scenarios."""
        with patch('xrayclient.xray_client.JIRA') as mock_jira:
            mock_jira.return_value = Mock()
            with patch('xrayclient.xray_client.requests.post') as mock_post:
                # Auth response
                mock_auth_response = Mock()
                mock_auth_response.text = '"test_auth_token"'
                mock_auth_response.raise_for_status.return_value = None
                
                # Test execution XSP1-22222 response
                mock_exec_response = Mock()
                mock_exec_response.json.return_value = {
                    'data': {
                        'getTestExecutions': {
                            'results': [
                                {'issueId': '10001', 'jira': {'key': 'XSP1-22222'}}
                            ]
                        }
                    }
                }
                mock_exec_response.raise_for_status.return_value = None
                
                # Test cases XSP1-54321 and XSP1-11111 response
                mock_tests_response = Mock()
                mock_tests_response.json.return_value = {
                    'data': {
                        'getTests': {
                            'results': [
                                {'issueId': '10002', 'jira': {'key': 'XSP1-54321'}},
                                {'issueId': '10003', 'jira': {'key': 'XSP1-11111'}}
                            ]
                        }
                    }
                }
                mock_tests_response.raise_for_status.return_value = None
                
                # Test plan XSP1-12345 response
                mock_plan_response = Mock()
                mock_plan_response.json.return_value = {
                    'data': {
                        'getTestPlans': {
                            'results': [
                                {'issueId': '10004', 'jira': {'key': 'XSP1-12345'}}
                            ]
                        }
                    }
                }
                mock_plan_response.raise_for_status.return_value = None
                
                mock_post.side_effect = [
                    mock_auth_response,
                    mock_exec_response,
                    mock_tests_response,
                    mock_plan_response
                ]
                
                client = XrayGraphQL()
                yield client
    
    def test_XSP1_22222_test_execution_retrieval(self, setup_specific_test):
        """Test retrieving test execution XSP1-22222."""
        client = setup_specific_test
        
        # Get test execution details
        result = client.get_test_execution('XSP1-22222')
        
        assert result is not None
        assert result['id'] == '10001'
        assert 'tests' in result
        assert len(result['tests']) == 2
        assert 'XSP1-54321' in result['tests']
        assert 'XSP1-11111' in result['tests']
    
    def test_XSP1_54321_test_case_workflow(self, setup_specific_test):
        """Test complete workflow for test case XSP1-54321."""
        client = setup_specific_test
        
        # Mock test run status response for XSP1-54321
        with patch.object(client, '_make_graphql_request') as mock_request:
            mock_request.return_value = {
                'getTestRun': {
                    'id': 'test_run_54321',
                    'status': {'name': 'TODO'}
                }
            }
            
            # Get test run status
            run_id, status = client.get_test_runstatus('XSP1-54321', 'XSP1-22222')
            
            assert run_id == 'test_run_54321'
            assert status == 'TODO'
            
            # Update status to PASS
            mock_request.return_value = {'updateTestRunStatus': True}
            result = client.update_test_run_status(run_id, 'PASS')
            assert result is True
            
            # Add comment
            mock_request.return_value = {'updateTestRunComment': True}
            comment = "Test case XSP1-54321 executed successfully"
            result = client.update_test_run_comment(run_id, comment)
            assert result is True
    
    def test_XSP1_11111_test_case_workflow(self, setup_specific_test):
        """Test complete workflow for test case XSP1-11111."""
        client = setup_specific_test
        
        # Mock test run status response for XSP1-11111
        with patch.object(client, '_make_graphql_request') as mock_request:
            mock_request.return_value = {
                'getTestRun': {
                    'id': 'test_run_11111',
                    'status': {'name': 'TODO'}
                }
            }
            
            # Get test run status
            run_id, status = client.get_test_runstatus('XSP1-11111', 'XSP1-22222')
            
            assert run_id == 'test_run_11111'
            assert status == 'TODO'
            
            # Update status to PASS
            mock_request.return_value = {'updateTestRunStatus': True}
            result = client.update_test_run_status(run_id, 'PASS')
            assert result is True
            
            # Add comment
            mock_request.return_value = {'updateTestRunComment': True}
            comment = "Test case XSP1-11111 executed successfully"
            result = client.update_test_run_comment(run_id, comment)
            assert result is True
    
    def test_XSP1_12345_test_plan_workflow(self, setup_specific_test):
        """Test workflow for test plan XSP1-12345."""
        client = setup_specific_test
        
        # Mock test plan tests response
        with patch.object(client, '_make_graphql_request') as mock_request:
            mock_request.return_value = {
                'getTestPlan': {
                    'tests': {
                        'results': [
                            {'issueId': '10002', 'jira': {'key': 'XSP1-54321'}},
                            {'issueId': '10003', 'jira': {'key': 'XSP1-11111'}}
                        ]
                    }
                }
            }
            
            # Get tests from test plan
            tests = client.get_tests_from_test_plan('XSP1-12345')
            
            assert tests is not None
            assert len(tests) == 2
            assert tests['XSP1-54321'] == '10002'
            assert tests['XSP1-11111'] == '10003'
    
    def test_both_test_cases_in_execution(self, setup_specific_test):
        """Test that both test cases XSP1-54321 and XSP1-11111 are in execution XSP1-22222."""
        client = setup_specific_test
        
        # Mock test execution tests response
        with patch.object(client, '_make_graphql_request') as mock_request:
            mock_request.return_value = {
                'getTestExecution': {
                    'tests': {
                        'results': [
                            {'issueId': '10002', 'jira': {'key': 'XSP1-54321'}},
                            {'issueId': '10003', 'jira': {'key': 'XSP1-11111'}}
                        ]
                    }
                }
            }
            
            # Get tests from test execution
            tests = client.get_tests_from_test_execution('XSP1-22222')
            
            assert tests is not None
            assert len(tests) == 2
            assert 'XSP1-54321' in tests
            assert 'XSP1-11111' in tests
            assert tests['XSP1-54321'] == '10002'
            assert tests['XSP1-11111'] == '10003'
    
    def test_test_execution_creation_from_test_plan(self, setup_specific_test):
        """Test creating test execution from test plan XSP1-12345."""
        client = setup_specific_test
        
        # Mock responses for creating test execution from test plan
        with patch.object(client, '_make_graphql_request') as mock_request:
            # Mock get tests from test plan
            mock_request.return_value = {
                'getTestPlan': {
                    'tests': {
                        'results': [
                            {'issueId': '10002', 'jira': {'key': 'XSP1-54321'}},
                            {'issueId': '10003', 'jira': {'key': 'XSP1-11111'}}
                        ]
                    }
                }
            }
            
            # Mock create test execution
            mock_request.return_value = {
                'createTestExecution': {
                    'testExecution': {
                        'issueId': '10005',
                        'jira': {'key': 'XSP1-22222'},
                        'testRuns': {
                            'results': [
                                {
                                    'id': 'test_run_54321',
                                    'test': {
                                        'issueId': '10002',
                                        'jira': {'key': 'XSP1-54321'}
                                    }
                                },
                                {
                                    'id': 'test_run_11111',
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
            
            # Mock add to test plan
            mock_request.return_value = {
                'addTestExecutionsToTestPlan': {
                    'addedTestExecutions': ['10005'],
                    'warning': None
                }
            }
            
            result = client.create_test_execution_from_test_plan('XSP1-12345')
            
            assert result is not None
            assert len(result) == 2
            assert 'XSP1-54321' in result
            assert 'XSP1-11111' in result
            
            # Verify test run details
            assert result['XSP1-54321']['test_run_id'] == 'test_run_54321'
            assert result['XSP1-54321']['test_execution_key'] == 'XSP1-22222'
            assert result['XSP1-54321']['test_plan_key'] == 'XSP1-12345'
            
            assert result['XSP1-11111']['test_run_id'] == 'test_run_11111'
            assert result['XSP1-11111']['test_execution_key'] == 'XSP1-22222'
            assert result['XSP1-11111']['test_plan_key'] == 'XSP1-12345'
    
    def test_individual_test_case_status_updates(self, setup_specific_test):
        """Test individual status updates for each test case."""
        client = setup_specific_test
        
        test_cases = ['XSP1-54321', 'XSP1-11111']
        
        for test_case in test_cases:
            with patch.object(client, '_make_graphql_request') as mock_request:
                # Mock get test run status
                mock_request.return_value = {
                    'getTestRun': {
                        'id': f'test_run_{test_case[-5:]}',
                        'status': {'name': 'TODO'}
                    }
                }
                
                # Get initial status
                run_id, status = client.get_test_runstatus(test_case, 'XSP1-22222')
                assert run_id == f'test_run_{test_case[-5:]}'
                assert status == 'TODO'
                
                # Update to EXECUTING
                mock_request.return_value = {'updateTestRunStatus': True}
                result = client.update_test_run_status(run_id, 'EXECUTING')
                assert result is True
                
                # Update to PASS
                result = client.update_test_run_status(run_id, 'PASS')
                assert result is True
                
                # Add success comment
                mock_request.return_value = {'updateTestRunComment': True}
                comment = f"Test case {test_case} completed successfully"
                result = client.update_test_run_comment(run_id, comment)
                assert result is True
    
    def test_test_case_failure_scenarios(self, setup_specific_test):
        """Test failure scenarios for test cases."""
        client = setup_specific_test
        
        test_cases = ['XSP1-54321', 'XSP1-11111']
        
        for test_case in test_cases:
            with patch.object(client, '_make_graphql_request') as mock_request:
                # Mock get test run status
                mock_request.return_value = {
                    'getTestRun': {
                        'id': f'test_run_{test_case[-5:]}',
                        'status': {'name': 'TODO'}
                    }
                }
                
                # Get initial status
                run_id, status = client.get_test_runstatus(test_case, 'XSP1-22222')
                assert run_id == f'test_run_{test_case[-5:]}'
                
                # Update to EXECUTING
                mock_request.return_value = {'updateTestRunStatus': True}
                result = client.update_test_run_status(run_id, 'EXECUTING')
                assert result is True
                
                # Update to FAIL
                result = client.update_test_run_status(run_id, 'FAIL')
                assert result is True
                
                # Add failure comment
                mock_request.return_value = {'updateTestRunComment': True}
                failure_comment = f"Test case {test_case} failed during execution"
                result = client.update_test_run_comment(run_id, failure_comment)
                assert result is True
    
    def test_test_execution_summary_validation(self, setup_specific_test):
        """Test validation of test execution summary."""
        client = setup_specific_test
        
        # Test execution should contain both test cases
        with patch.object(client, '_make_graphql_request') as mock_request:
            mock_request.return_value = {
                'getTestExecution': {
                    'issueId': '10001',
                    'tests': {
                        'results': [
                            {'issueId': '10002', 'jira': {'key': 'XSP1-54321'}},
                            {'issueId': '10003', 'jira': {'key': 'XSP1-11111'}}
                        ]
                    }
                }
            }
            
            result = client.get_test_execution('XSP1-22222')
            
            assert result is not None
            assert result['id'] == '10001'
            assert len(result['tests']) == 2
            
            # Verify both test cases are present
            test_keys = list(result['tests'].keys())
            assert 'XSP1-54321' in test_keys
            assert 'XSP1-11111' in test_keys
    
    def test_test_plan_test_case_validation(self, setup_specific_test):
        """Test validation that test plan contains the expected test cases."""
        client = setup_specific_test
        
        # Test plan should contain both test cases
        with patch.object(client, '_make_graphql_request') as mock_request:
            mock_request.return_value = {
                'getTestPlan': {
                    'tests': {
                        'results': [
                            {'issueId': '10002', 'jira': {'key': 'XSP1-54321'}},
                            {'issueId': '10003', 'jira': {'key': 'XSP1-11111'}}
                        ]
                    }
                }
            }
            
            result = client.get_tests_from_test_plan('XSP1-12345')
            
            assert result is not None
            assert len(result) == 2
            
            # Verify both test cases are present
            test_keys = list(result.keys())
            assert 'XSP1-54321' in test_keys
            assert 'XSP1-11111' in test_keys
            
            # Verify internal IDs
            assert result['XSP1-54321'] == '10002'
            assert result['XSP1-11111'] == '10003'
    
    def test_error_handling_specific_scenarios(self, setup_specific_test):
        """Test error handling for specific scenarios."""
        client = setup_specific_test
        
        # Test with invalid test execution
        with patch.object(client, '_make_graphql_request', return_value=None):
            result = client.get_test_execution('INVALID-123')
            assert result is None
        
        # Test with invalid test case
        with patch.object(client, '_make_graphql_request', return_value=None):
            result = client.get_test_runstatus('INVALID-456', 'XSP1-22222')
            assert result == (None, None)
        
        # Test with invalid test plan
        with patch.object(client, '_make_graphql_request', return_value=None):
            result = client.get_tests_from_test_plan('INVALID-789')
            assert result is None
    
    def test_data_consistency_validation(self, setup_specific_test):
        """Test data consistency between test execution and test plan."""
        client = setup_specific_test
        
        # Mock responses for both test execution and test plan
        with patch.object(client, '_make_graphql_request') as mock_request:
            # Mock test execution response
            mock_request.return_value = {
                'getTestExecution': {
                    'issueId': '10001',
                    'tests': {
                        'results': [
                            {'issueId': '10002', 'jira': {'key': 'XSP1-54321'}},
                            {'issueId': '10003', 'jira': {'key': 'XSP1-11111'}}
                        ]
                    }
                }
            }
            
            exec_tests = client.get_tests_from_test_execution('XSP1-22222')
            
            # Mock test plan response
            mock_request.return_value = {
                'getTestPlan': {
                    'tests': {
                        'results': [
                            {'issueId': '10002', 'jira': {'key': 'XSP1-54321'}},
                            {'issueId': '10003', 'jira': {'key': 'XSP1-11111'}}
                        ]
                    }
                }
            }
            
            plan_tests = client.get_tests_from_test_plan('XSP1-12345')
            
            # Verify consistency
            assert exec_tests is not None
            assert plan_tests is not None
            assert len(exec_tests) == len(plan_tests)
            assert set(exec_tests.keys()) == set(plan_tests.keys())
            assert exec_tests['XSP1-54321'] == plan_tests['XSP1-54321']
            assert exec_tests['XSP1-11111'] == plan_tests['XSP1-11111'] 