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
def get_test_data_from_test_plan(test_plan_key):
    '''get the test data from the test plan'''
    try:
        xclient = XrayGraphQL()
        response = xclient.get_tests_from_test_plan(test_plan_key)
        return response
    except Exception as e:
        log.error(f"Error getting test data from test plan: {e}")
        return []

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
                    tests = xclient.get_tests_from_test_plan(jira_key)
                    log.info(f"Tests : {tests} - {len(tests)}")
                    for test_key , test_id in tests.items():
                        log.info(f" =============================== Test Key : {test_key} - Test ID : {test_id}")
                        testDetails = xclient.get_test_details(test_key, 'test')
                        testSteps = testDetails.get('steps',[])
                        for step in testSteps:
                            log.info(f"Step : {step}")
                            stepData = step.get('data',{})
                            log.info(f"Step Data : {stepData}")
                            stepAttachments = step.get('attachments',[])
                            for attachment in stepAttachments:
                                mimeType = 'application/json'
                                log.info(f"Attachment : {attachment}")
                                attachmentID = attachment.get('id',{})
                                log.info(f"Attachment ID : {attachmentID}")
                                attachmentFilename = attachment.get('filename',{})
                                log.info(f"Attachment Filename : {attachmentFilename}")
                                attachmentDownloadLink = attachment.get('downloadLink',{})
                                log.info(f"Attachment Download Link : {attachmentDownloadLink}")
                                #Download the attachment using Xray API instead of JIRA API
                                attachmentResponse = xclient.download_xray_attachment_by_id(attachmentID, mimeType)
                                jprint(attachmentResponse['json_content'])
                                # log.info(f"Attachment Response : {attachmentResponse}")
                                # if attachmentResponse and attachmentResponse.get('json_content'):
                                #     attachmentData = attachmentResponse.get('json_content')
                                #     log.info(f"Attachment Data : {attachmentData}")
                                # attachmentFilename = attachmentData.get('filename',{})
                                # log.info(f"Attachment Filename : {attachmentFilename}")
                                # attachmentStoredInJira = attachment.get('storedInJira',{})
                                # log.info(f"Attachment Stored In Jira : {attachmentStoredInJira}")

                        # jprint(testDetails)
                    # jprint(tests)
                case _:
                    log.erro(f"No match found : {issueType}")
                    return []
        jprint(issueType)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    download_jira_attachment("XSP1-12345")
