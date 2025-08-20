import requests
from jsonpath_nz import jprint, log
from xrayclient.xray_client import XrayGraphQL
from dotenv import load_dotenv


# Load environment variables from .env file
load_dotenv()
# Test Plan : 
# IDFCCXP-64788

# Test Case:
# IDFCCXP-63476
# IDFCCXP-63477
def download_jira_attachment(jira_key):
    '''download the jira attachment'''
    try:
        jira_key = "IDFCCXP-64788"
        xclient = XrayGraphQL()
        response = xclient.get_issue(jira_key)
        issueType = response.get("issuetype",{}).get('name','')
        if issueType:
            match issueType:
                case "Test Plan":
                    testPlan = xclient.get_tests_from_test_plan(jira_key)
                    jprint(testPlan)
                case _:
                    log.erro(f"No match found : {issueType}")
                    return []
        jprint(issueType)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    download_jira_attachment("XSP1-12345")
