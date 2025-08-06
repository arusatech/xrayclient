"""
Integration tests for XrayGraphQL workflow with specific test execution and test cases.
"""
import pytest
import tempfile
import os
from unittest.mock import Mock, patch, mock_open
from xrayclient.xray_client import XrayGraphQL


class TestXrayIntegration:
    """Integration tests for XrayGraphQL workflow."""
    
    @pytest.fixture
    def setup_integration_test(self, mock_env_vars):
        """Setup for integration tests with mocked responses."""
        with patch('xrayclient.xray_client.JIRA') as mock_jira:
            mock_jira.return_value = Mock()
            with patch('xrayclient.xray_client.requests.post') as mock_post:
                # Auth response
                mock_auth_response = Mock()
                mock_auth_response.text = '"test_auth_token"'
                mock_auth_response.raise_for_status.return_value = None
                
                # Test plan ID response
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
                
                # Test execution ID response
                mock_exec_id_response = Mock()
                mock_exec_id_response.json.return_value = {
                    'data': {
                        'getTestExecutions': {
                            'results': [
                                {'issueId': '10002', 'jira': {'key': 'XSP1-22222'}}
                            ]
                        }
                    }
                }
                mock_exec_id_response.raise_for_status.return_value = None
                
                # Test case IDs response
                mock_test_ids_response = Mock()
                mock_test_ids_response.json.return_value = {
                    'data': {
                        'getTests': {
                            'results': [
                                {'issueId': '10003', 'jira': {'key': 'XSP1-54321'}},
                                {'issueId': '10004', 'jira': {'key': 'XSP1-11111'}}
                            ]
                        }
                    }
                }
                mock_test_ids_response.raise_for_status.return_value = None
                
                # Test run status response
                mock_run_status_response = Mock()
                mock_run_status_response.json.return_value = {
                    'data': {
                        'getTestRun': {
                            'id': 'test_run_12345',
                            'status': {'name': 'TODO'}
                        }
                    }
                }
                mock_run_status_response.raise_for_status.return_value = None
                
                # Update test run status response
                mock_update_status_response = Mock()
                mock_update_status_response.json.return_value = {
                    'data': {
                        'updateTestRunStatus': True
                    }
                }
                mock_update_status_response.raise_for_status.return_value = None
                
                # Update test run comment response
                mock_update_comment_response = Mock()
                mock_update_comment_response.json.return_value = {
                    'data': {
                        'updateTestRunComment': True
                    }
                }
                mock_update_comment_response.raise_for_status.return_value = None
                
                # Add evidence response
                mock_evidence_response = Mock()
                mock_evidence_response.json.return_value = {
                    'data': {
                        'addEvidenceToTestRun': {
                            'addedEvidence': ['evidence_123'],
                            'warnings': []
                        }
                    }
                }
                mock_evidence_response.raise_for_status.return_value = None
                
                # Create defect response
                mock_defect_response = Mock()
                mock_defect_response.json.return_value = {
                    'data': {
                        'addDefectsToTestRun': {
                            'addedDefects': ['XSP1-99999'],
                            'warnings': []
                        }
                    }
                }
                mock_defect_response.raise_for_status.return_value = None
                
                mock_post.side_effect = [
                    mock_auth_response,
                    mock_plan_id_response,
                    mock_exec_id_response,
                    mock_test_ids_response,
                    mock_run_status_response,
                    mock_update_status_response,
                    mock_update_comment_response,
                    mock_evidence_response,
                    mock_defect_response
                ]
                
                client = XrayGraphQL()
                yield client
    
    def test_complete_test_execution_workflow(self, setup_integration_test):
        """Test complete workflow for test execution XSP1-22222 with test cases XSP1-54321 and XSP1-11111."""
        client = setup_integration_test
        
        # Step 1: Get tests from test execution
        tests = client.get_tests_from_test_execution('XSP1-22222')
        assert tests is not None
        assert 'XSP1-54321' in tests
        assert 'XSP1-11111' in tests
        assert tests['XSP1-54321'] == '10003'
        assert tests['XSP1-11111'] == '10004'
        
        # Step 2: Get test run status for each test case
        for test_case in ['XSP1-54321', 'XSP1-11111']:
            run_id, status = client.get_test_runstatus(test_case, 'XSP1-22222')
            assert run_id == 'test_run_12345'
            assert status == 'TODO'
        
        # Step 3: Update test run status to PASS
        for test_case in ['XSP1-54321', 'XSP1-11111']:
            run_id, _ = client.get_test_runstatus(test_case, 'XSP1-22222')
            result = client.update_test_run_status(run_id, 'PASS')
            assert result is True
        
        # Step 4: Add comments to test runs
        for test_case in ['XSP1-54321', 'XSP1-11111']:
            run_id, _ = client.get_test_runstatus(test_case, 'XSP1-22222')
            comment = f"Test {test_case} passed successfully in execution XSP1-22222"
            result = client.update_test_run_comment(run_id, comment)
            assert result is True
    
    def test_test_plan_workflow(self, setup_integration_test):
        """Test workflow for test plan XSP1-12345."""
        client = setup_integration_test
        
        # Step 1: Get tests from test plan
        tests = client.get_tests_from_test_plan('XSP1-12345')
        assert tests is not None
        assert 'XSP1-54321' in tests
        assert 'XSP1-11111' in tests
        
        # Step 2: Create test execution from test plan
        test_execution = client.create_test_execution_from_test_plan('XSP1-12345')
        assert test_execution is not None
        assert 'XSP1-54321' in test_execution
        assert 'XSP1-11111' in test_execution
        
        # Verify test execution details
        for test_case in ['XSP1-54321', 'XSP1-11111']:
            assert test_execution[test_case]['test_plan_key'] == 'XSP1-12345'
            assert 'test_run_id' in test_execution[test_case]
            assert 'test_execution_key' in test_execution[test_case]
    
    def test_evidence_and_defect_workflow(self, setup_integration_test):
        """Test evidence and defect creation workflow."""
        client = setup_integration_test
        
        # Create temporary evidence file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("Test evidence content")
            evidence_path = f.name
        
        try:
            # Step 1: Get test run ID
            run_id, _ = client.get_test_runstatus('XSP1-54321', 'XSP1-22222')
            
            # Step 2: Add evidence to test run
            with patch('os.path.exists', return_value=True):
                with patch('builtins.open', mock_open(read_data=b'test_evidence_data')):
                    with patch('mimetypes.guess_type', return_value=('text/plain', None)):
                        result = client.add_evidence_to_test_run(run_id, evidence_path)
                        assert result is not None
                        assert 'addedEvidence' in result
            
            # Step 3: Create defect from test run
            with patch.object(client, 'create_issue', return_value=('XSP1-99999', '10099')):
                result = client.create_defect_from_test_run(
                    test_run_id=run_id,
                    project_key='XSP1',
                    parent_issue_key='XSP1-22222',
                    defect_summary='Test defect from automated test',
                    defect_description='This defect was created automatically from test run'
                )
                assert result is not None
                assert 'addedDefects' in result
                assert 'XSP1-99999' in result['addedDefects']
        
        finally:
            # Clean up temporary file
            if os.path.exists(evidence_path):
                os.unlink(evidence_path)
    
    def test_test_execution_creation_with_specific_tests(self, setup_integration_test):
        """Test creating test execution with specific test cases."""
        client = setup_integration_test
        
        # Create test execution with specific test cases
        test_issue_keys = ['XSP1-54321', 'XSP1-11111']
        result = client.create_test_execution(
            test_issue_keys=test_issue_keys,
            project_key='XSP1',
            summary='Test Execution for XSP1-12345 Test Plan',
            description='Automated test execution for test cases XSP1-54321 and XSP1-11111'
        )
        
        assert result is not None
        assert 'issueId' in result
        assert 'jira' in result
        assert result['jira']['key'] == 'XSP1-22222'
    
    def test_test_run_status_transitions(self, setup_integration_test):
        """Test various test run status transitions."""
        client = setup_integration_test
        
        test_case = 'XSP1-54321'
        test_execution = 'XSP1-22222'
        
        # Get initial status
        run_id, initial_status = client.get_test_runstatus(test_case, test_execution)
        assert run_id is not None
        assert initial_status == 'TODO'
        
        # Transition to EXECUTING
        result = client.update_test_run_status(run_id, 'EXECUTING')
        assert result is True
        
        # Transition to PASS
        result = client.update_test_run_status(run_id, 'PASS')
        assert result is True
        
        # Add comment for passed test
        comment = f"Test {test_case} executed successfully and passed all validations"
        result = client.update_test_run_comment(run_id, comment)
        assert result is True
    
    def test_test_run_status_transitions_failure_scenario(self, setup_integration_test):
        """Test test run status transitions for failure scenario."""
        client = setup_integration_test
        
        test_case = 'XSP1-11111'
        test_execution = 'XSP1-22222'
        
        # Get initial status
        run_id, initial_status = client.get_test_runstatus(test_case, test_execution)
        assert run_id is not None
        
        # Transition to EXECUTING
        result = client.update_test_run_status(run_id, 'EXECUTING')
        assert result is True
        
        # Transition to FAIL
        result = client.update_test_run_status(run_id, 'FAIL')
        assert result is True
        
        # Add failure comment
        failure_comment = f"Test {test_case} failed due to assertion error in step 3"
        result = client.update_test_run_comment(run_id, failure_comment)
        assert result is True
    
    def test_bulk_test_execution_operations(self, setup_integration_test):
        """Test bulk operations on multiple test cases."""
        client = setup_integration_test
        
        test_cases = ['XSP1-54321', 'XSP1-11111']
        test_execution = 'XSP1-22222'
        
        # Bulk status update
        for test_case in test_cases:
            run_id, _ = client.get_test_runstatus(test_case, test_execution)
            result = client.update_test_run_status(run_id, 'PASS')
            assert result is True
        
        # Bulk comment update
        for test_case in test_cases:
            run_id, _ = client.get_test_runstatus(test_case, test_execution)
            comment = f"Bulk update: Test {test_case} completed successfully"
            result = client.update_test_run_comment(run_id, comment)
            assert result is True
    
    def test_test_plan_data_retrieval(self, setup_integration_test):
        """Test retrieving and parsing data from test plan."""
        client = setup_integration_test
        
        # Mock test plan data response
        with patch.object(client, '_make_graphql_request') as mock_request:
            mock_request.return_value = {
                'getTestPlan': {
                    'issueId': '10001',
                    'jira': {
                        'key': 'XSP1-12345',
                        'description': """Test Data || Values
                        |temperature |[20, 25, 30]|
                        |pressure    |[1.0, 1.5, 2.0]|
                        |threshold   |42            |"""
                    }
                }
            }
            
            result = client.get_test_plan_data('XSP1-12345')
            
            assert result is not None
            assert 'temperature' in result
            assert 'pressure' in result
            assert 'threshold' in result
            assert result['temperature'] == [[20, 25, 30]]
            assert result['pressure'] == [[1.0, 1.5, 2.0]]
            assert result['threshold'] == [42]
    
    def test_error_handling_integration(self, setup_integration_test):
        """Test error handling in integration scenarios."""
        client = setup_integration_test
        
        # Test with invalid test execution
        result = client.get_tests_from_test_execution('INVALID-123')
        assert result is None
        
        # Test with invalid test case
        result = client.get_test_runstatus('INVALID-456', 'XSP1-22222')
        assert result == (None, None)
        
        # Test with invalid test plan
        result = client.get_tests_from_test_plan('INVALID-789')
        assert result is None
    
    def test_environment_variable_validation(self):
        """Test environment variable validation in integration context."""
        # Test with missing environment variables
        with patch.dict('os.environ', {}, clear=True):
            with pytest.raises(ValueError):
                XrayGraphQL()
        
        # Test with partial environment variables
        with patch.dict('os.environ', {'XRAY_CLIENT_ID': 'test_id'}):
            with pytest.raises(ValueError, match="XRAY_CLIENT_SECRET environment variable is required"):
                XrayGraphQL()
        
        with patch.dict('os.environ', {'XRAY_CLIENT_SECRET': 'test_secret'}):
            with pytest.raises(ValueError, match="XRAY_CLIENT_ID environment variable is required"):
                XrayGraphQL() 