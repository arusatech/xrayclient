import requests
from jsonpath_nz import jprint
from xrayclient.xray_client import XrayGraphQL
import os

# Use environment variables with safe defaults for testing
os.environ['JIRA_SERVER'] = os.getenv('JIRA_SERVER', 'https://test.atlassian.net')
os.environ['JIRA_USER'] = os.getenv('JIRA_USER', 'test@example.com')
os.environ['JIRA_API_KEY'] = os.getenv('JIRA_API_KEY', 'test-api-key')
os.environ['XRAY_CLIENT_ID'] = os.getenv('XRAY_CLIENT_ID', 'test-client-id')
os.environ['XRAY_CLIENT_SECRET'] = os.getenv('XRAY_CLIENT_SECRET', 'test-client-secret')
os.environ['XRAY_BASE_URL'] = os.getenv('XRAY_BASE_URL', 'https://xray.cloud.getxray.app')


def download_jira_attachment(jira_key):
    '''download the jira attachment'''
    try:
        jira_key = "XSP1-12345"
        handler = XrayGraphQL()
        response = handler.download_attachment(jira_key, '.json')
        jprint(response)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    download_jira_attachment("XSP1-12345")
