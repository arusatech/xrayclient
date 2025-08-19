import re
from xrayclient.xray_client import XrayGraphQL
import os
from jsonpath_nz import jprint, log as logger
import conftest

def test_spacy():
    sentence = '''
        Verify the destruction of offer and order assets in the NDC 
        for dev0 enviroment with region us-east-1  and you need to validate 
        against test function check_arn and test data is test_data.json
        '''
    template_schema = {
        "environment": ["dev0", "dev1", "qa0", "qa1"],
        "region": ["us-east-1", "us-east-1", "us-west-1", "us-west-2" ],
        "test_function": "<string>_<string>",
        "test_data": "<string>.json"
    }
    try:
        logger.info("Starting test_spacy")
        xClient = XrayGraphQL()
        result = xClient.generate_json_from_sentence(sentence, template_schema)
        jprint(result)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_spacy()