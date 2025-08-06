"""
Workflow example tests demonstrating how to use the Xray client with specific test execution and test cases.
"""
import pytest
from unittest.mock import Mock, patch, mock_open
from xrayclient.xray_client import XrayGraphQL


class TestWorkflowExamples:
    """Workflow examples for using the Xray client."""
    
    @pytest.fixture
    def setup_workflow_test(self, mock_env_vars):
        """Setup for workflow example tests."""
        with patch('xrayclient.xray_client.JIRA') as mock_jira:
            mock_jira.return_value = Mock()
            with patch('xrayclient.xray_client.requests.post') as mock_post:
                # Auth response
                mock_auth_response = Mock()
                mock_auth_response.text = '"test_auth_token"'
                mock_auth_response.raise_for_status.return_value = None
                
                # Various GraphQL responses
                mock_graphql_responses = [
                    # Test execution response
                    Mock(json=lambda: {
                        'data': {
                            'getTestExecutions': {
                                'results': [{'issueId': '10001', 'jira': {'key': 'XSP1-22222'}}]
                            }
                        }
                    }, raise_for_status=lambda: None),
                    # Test cases response
                    Mock(json=lambda: {
                        'data': {
                            'getTests': {
                                'results': [
                                    {'issueId': '10002', 'jira': {'key': 'XSP1-54321'}},
                                    {'issueId': '10003', 'jira': {'key': 'XSP1-11111'}}
                                ]
                            }
                        }
                    }, raise_for_status=lambda: None),
                    # Test plan response
                    Mock(json=lambda: {
                        'data': {
                            'getTestPlans': {
                                'results': [{'issueId': '10004', 'jira': {'key': 'XSP1-12345'}}]
                            }
                        }
                    }, raise_for_status=lambda: None),
                ]
                
                mock_post.side_effect = [mock_auth_response] + mock_graphql_responses
                
                client = XrayGraphQL()
                yield client
    
    def test_example_1_retrieve_test_execution_details(self, setup_workflow_test):
        """
        Example 1: Retrieve details for test execution XSP1-22222.
        
        This example shows how to:
        1. Get test execution details
        2. List all test cases in the execution
        3. Get test run status for each test case
        """
        client = setup_workflow_test
        
        # Mock responses for this workflow
        with patch.object(client, '_make_graphql_request') as mock_request:
            # Mock get test execution
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
            
            # Step 1: Get test execution details
            test_execution = client.get_test_execution('XSP1-22222')
            
            assert test_execution is not None
            assert test_execution['id'] == '10001'
            assert len(test_execution['tests']) == 2
            
            # Step 2: List all test cases
            test_cases = list(test_execution['tests'].keys())
            assert 'XSP1-54321' in test_cases
            assert 'XSP1-11111' in test_cases
            
            # Step 3: Get test run status for each test case
            for test_case in test_cases:
                # Mock test run status response
                mock_request.return_value = {
                    'getTestRun': {
                        'id': f'test_run_{test_case[-5:]}',
                        'status': {'name': 'TODO'}
                    }
                }
                
                run_id, status = client.get_test_runstatus(test_case, 'XSP1-22222')
                assert run_id is not None
                assert status == 'TODO'
    
    def test_example_2_update_test_run_statuses(self, setup_workflow_test):
        """
        Example 2: Update test run statuses for test cases in execution XSP1-22222.
        
        This example shows how to:
        1. Get test cases from test execution
        2. Update each test run status to PASS
        3. Add comments to successful test runs
        """
        client = setup_workflow_test
        
        with patch.object(client, '_make_graphql_request') as mock_request:
            # Mock get tests from test execution
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
            
            # Step 1: Get test cases from test execution
            tests = client.get_tests_from_test_execution('XSP1-22222')
            assert tests is not None
            assert len(tests) == 2
            
            # Step 2: Update each test run status
            for test_case in tests.keys():
                # Mock get test run status
                mock_request.return_value = {
                    'getTestRun': {
                        'id': f'test_run_{test_case[-5:]}',
                        'status': {'name': 'TODO'}
                    }
                }
                
                run_id, _ = client.get_test_runstatus(test_case, 'XSP1-22222')
                
                # Update status to PASS
                mock_request.return_value = {'updateTestRunStatus': True}
                result = client.update_test_run_status(run_id, 'PASS')
                assert result is True
                
                # Add success comment
                mock_request.return_value = {'updateTestRunComment': True}
                comment = f"Test case {test_case} passed successfully"
                result = client.update_test_run_comment(run_id, comment)
                assert result is True
    
    def test_example_3_create_test_execution_from_test_plan(self, setup_workflow_test):
        """
        Example 3: Create test execution from test plan XSP1-12345.
        
        This example shows how to:
        1. Create a test execution from a test plan
        2. Get test run IDs for each test case
        3. Update test run statuses
        """
        client = setup_workflow_test
        
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
            
            # Step 1: Create test execution from test plan
            test_execution = client.create_test_execution_from_test_plan('XSP1-12345')
            
            assert test_execution is not None
            assert len(test_execution) == 2
            
            # Step 2: Get test run IDs and update statuses
            for test_case, details in test_execution.items():
                run_id = details['test_run_id']
                test_exec_key = details['test_execution_key']
                
                assert run_id is not None
                assert test_exec_key == 'XSP1-22222'
                
                # Update test run status
                mock_request.return_value = {'updateTestRunStatus': True}
                result = client.update_test_run_status(run_id, 'PASS')
                assert result is True
    
    def test_example_4_handle_test_failures(self, setup_workflow_test):
        """
        Example 4: Handle test failures and create defects.
        
        This example shows how to:
        1. Update test run status to FAIL
        2. Add failure comments
        3. Create defects from failed test runs
        4. Add evidence to test runs
        """
        client = setup_workflow_test
        
        with patch.object(client, '_make_graphql_request') as mock_request:
            # Mock get test run status
            mock_request.return_value = {
                'getTestRun': {
                    'id': 'test_run_54321',
                    'status': {'name': 'TODO'}
                }
            }
            
            # Step 1: Get test run ID
            run_id, _ = client.get_test_runstatus('XSP1-54321', 'XSP1-22222')
            
            # Step 2: Update status to FAIL
            mock_request.return_value = {'updateTestRunStatus': True}
            result = client.update_test_run_status(run_id, 'FAIL')
            assert result is True
            
            # Step 3: Add failure comment
            mock_request.return_value = {'updateTestRunComment': True}
            failure_comment = "Test failed due to assertion error in step 3"
            result = client.update_test_run_comment(run_id, failure_comment)
            assert result is True
            
            # Step 4: Add evidence (screenshot, logs, etc.)
            with patch('os.path.exists', return_value=True):
                with patch('builtins.open', mock_open(read_data=b'evidence_data')):
                    with patch('mimetypes.guess_type', return_value=('image/png', None)):
                        mock_request.return_value = {
                            'addEvidenceToTestRun': {
                                'addedEvidence': ['evidence_123'],
                                'warnings': []
                            }
                        }
                        
                        result = client.add_evidence_to_test_run(run_id, '/tmp/screenshot.png')
                        assert result is not None
                        assert 'addedEvidence' in result
            
            # Step 5: Create defect from test run
            with patch.object(client, 'create_issue', return_value=('XSP1-99999', '10099')):
                mock_request.return_value = {
                    'addDefectsToTestRun': {
                        'addedDefects': ['XSP1-99999'],
                        'warnings': []
                    }
                }
                
                result = client.create_defect_from_test_run(
                    test_run_id=run_id,
                    project_key='XSP1',
                    parent_issue_key='XSP1-22222',
                    defect_summary='Test failure in XSP1-54321',
                    defect_description='Test case failed during execution'
                )
                assert result is not None
                assert 'addedDefects' in result
    
    def test_example_5_bulk_test_execution_workflow(self, setup_workflow_test):
        """
        Example 5: Bulk test execution workflow.
        
        This example shows how to:
        1. Process multiple test cases in batch
        2. Handle mixed results (pass/fail)
        3. Generate summary report
        """
        client = setup_workflow_test
        
        test_cases = ['XSP1-54321', 'XSP1-11111']
        results = {'passed': [], 'failed': []}
        
        with patch.object(client, '_make_graphql_request') as mock_request:
            for test_case in test_cases:
                # Mock get test run status
                mock_request.return_value = {
                    'getTestRun': {
                        'id': f'test_run_{test_case[-5:]}',
                        'status': {'name': 'TODO'}
                    }
                }
                
                run_id, _ = client.get_test_runstatus(test_case, 'XSP1-22222')
                
                # Simulate test execution (random pass/fail for demo)
                import random
                test_passed = random.choice([True, False])
                
                if test_passed:
                    # Update to PASS
                    mock_request.return_value = {'updateTestRunStatus': True}
                    result = client.update_test_run_status(run_id, 'PASS')
                    assert result is True
                    
                    # Add success comment
                    mock_request.return_value = {'updateTestRunComment': True}
                    comment = f"Test case {test_case} passed"
                    client.update_test_run_comment(run_id, comment)
                    
                    results['passed'].append(test_case)
                else:
                    # Update to FAIL
                    mock_request.return_value = {'updateTestRunStatus': True}
                    result = client.update_test_run_status(run_id, 'FAIL')
                    assert result is True
                    
                    # Add failure comment
                    mock_request.return_value = {'updateTestRunComment': True}
                    comment = f"Test case {test_case} failed"
                    client.update_test_run_comment(run_id, comment)
                    
                    results['failed'].append(test_case)
            
            # Generate summary
            total_tests = len(test_cases)
            passed_tests = len(results['passed'])
            failed_tests = len(results['failed'])
            
            assert total_tests == passed_tests + failed_tests
            assert total_tests == 2  # XSP1-54321 and XSP1-11111
    
    def test_example_6_test_plan_data_analysis(self, setup_workflow_test):
        """
        Example 6: Analyze test plan data.
        
        This example shows how to:
        1. Retrieve test plan data
        2. Parse tabular data from test plan description
        3. Use parsed data for test execution
        """
        client = setup_workflow_test
        
        with patch.object(client, '_make_graphql_request') as mock_request:
            # Mock test plan data response
            mock_request.return_value = {
                'getTestPlan': {
                    'issueId': '10004',
                    'jira': {
                        'key': 'XSP1-12345',
                        'description': """Test Parameters || Values
                        |temperature |[20, 25, 30]|
                        |pressure    |[1.0, 1.5, 2.0]|
                        |timeout     |30            |"""
                    }
                }
            }
            
            # Step 1: Get test plan data
            test_plan_data = client.get_test_plan_data('XSP1-12345')
            
            assert test_plan_data is not None
            assert 'temperature' in test_plan_data
            assert 'pressure' in test_plan_data
            assert 'timeout' in test_plan_data
            
            # Step 2: Use parsed data for test execution
            temperatures = test_plan_data['temperature'][0]  # [20, 25, 30]
            pressures = test_plan_data['pressure'][0]        # [1.0, 1.5, 2.0]
            timeout = test_plan_data['timeout'][0]           # 30
            
            assert len(temperatures) == 3
            assert len(pressures) == 3
            assert timeout == 30
            
            # Step 3: Execute tests with different parameters
            for temp in temperatures:
                for pressure in pressures:
                    # Mock test execution for each parameter combination
                    mock_request.return_value = {
                        'getTestRun': {
                            'id': f'test_run_temp_{temp}_press_{pressure}',
                            'status': {'name': 'TODO'}
                        }
                    }
                    
                    run_id, _ = client.get_test_runstatus('XSP1-54321', 'XSP1-22222')
                    
                    # Update status with parameter-specific comment
                    mock_request.return_value = {'updateTestRunStatus': True}
                    result = client.update_test_run_status(run_id, 'PASS')
                    assert result is True
                    
                    # Add parameter-specific comment
                    mock_request.return_value = {'updateTestRunComment': True}
                    comment = f"Test passed with temperature={temp}°C, pressure={pressure}bar, timeout={timeout}s"
                    result = client.update_test_run_comment(run_id, comment)
                    assert result is True 