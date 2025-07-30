import logging
import requests
import unittest

from billingplatform import BillingPlatform
from utils_for_testing import get_credentials


"""
Tests assume an existing credentials file in the root directory. For more information of the expected format, 
see the utils_for_testing.py file.
"""

class TestBillingPlatformUpsert(unittest.TestCase):
    def test_basic_upsert(self):
        logging.basicConfig(level=logging.DEBUG)

        session_credentials = get_credentials('credentials.json', 'login')
        bp: BillingPlatform = BillingPlatform(**session_credentials)

        self.assertIsInstance(bp, BillingPlatform)
        self.assertIsInstance(bp.session, requests.Session)

        # Single record upsert
        payload: dict = {
            'Id': '12345', # Example ID, replace with a valid one
            'Name': 'Test Account',
            'Status': 'ACTIVE',
            'externalId': 'ext-12345' # Example ID, replace with a valid one
        }
        response: dict = bp.upsert(entity='ACCOUNT', data=payload, externalIDFieldName='externalId')

        # Multiple records upsert
        payload: list[dict] = [
            {
                'Id': '12345', # Example ID, replace with a valid one
                'Name': 'Test Account 1',
                'Status': 'ACTIVE',
                'externalId': 'ext-12345' # Example ID, replace with a valid one
            },
            {
                'Id': '67890', # Example ID, replace with a valid one
                'Name': 'Test Account 2',
                'Status': 'ACTIVE',
                'externalId': 'ext-67890' # Example ID, replace with a valid one
            }
        ]
        response: dict = bp.upsert(entity='ACCOUNT', data=payload, externalIDFieldName='externalId')

        self.assertIsInstance(response, dict)

    def test_brmobject_upsert(self):
        logging.basicConfig(level=logging.DEBUG)

        session_credentials = get_credentials('credentials.json', 'login')
        bp: BillingPlatform = BillingPlatform(**session_credentials)

        self.assertIsInstance(bp, BillingPlatform)
        self.assertIsInstance(bp.session, requests.Session)

        payload: dict = {
            'brmObjects': {
                'Id': '12345', # Example ID, replace with a valid one
                'Name': 'Test Account',
                'Status': 'ACTIVE',
                'externalId': 'ext-12345' # Example ID, replace with a valid one
            }, 
            'externalIDFieldName': 'externalId'
        }

        response: dict = bp.upsert(entity='ACCOUNT', data=payload, externalIDFieldName='externalId')

        self.assertIsInstance(response, dict)


if __name__ == '__main__':
    unittest.main()
