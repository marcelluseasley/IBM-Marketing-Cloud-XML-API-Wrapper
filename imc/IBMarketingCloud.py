#
# Filename: IBMarketingCloud.py
# 6/12/2016 1:56 AM
#
#
__author__ = 'measley'

import ConfigParser
import json

import requests

from lxml import etree
from lxml import objectify
from lxml.etree import Element
from lxml.etree import SubElement




class IBMarketingCloud(object):

    # constants
    AUTH_LEGACY = 1
    AUTH_OAUTH = 2


    # variables will be set
    # - pod
    # - access_token
    # - auth_method
    # - jsessionid
    # - URL

    def __init__(self):
        self.pod = None
        self.access_token = None
        self.auth_method = None
        self.jsessionid = None
        self.URL = None


    def authenticate(self,auth_method=AUTH_LEGACY, config_file=None):

        self.auth_method=auth_method

        config = ConfigParser.ConfigParser()
        config.read(config_file)

        if self.auth_method is self.AUTH_LEGACY:
            pod = config.get('MARKETING_CLOUD_LEGACY', 'Pod')
            self.pod = pod
            self.URL = r"https://api{}.silverpop.com/XMLAPI".format(pod)

            envelope = Element("Envelope")
            body = SubElement(envelope, "Body")
            login = SubElement(body, "Login")

            username = SubElement(login, "USERNAME")
            username.text = config.get('MARKETING_CLOUD_LEGACY', 'Username')
            password = SubElement(login, "PASSWORD")
            password.text = config.get('MARKETING_CLOUD_LEGACY', 'Password')

            loginXML = etree.tostring(envelope, encoding="UTF-8")

            #construct paramstring
            paramstring = {'xml': loginXML}
            r = requests.post(self.URL, params=paramstring)
            if r.status_code is 200:
                root = objectify.fromstring(r.text)
                self.jsessionid = root.Body.RESULT.SESSIONID.text

                return self.jsessionid
            else:
                return False




        elif self.auth_method is self.AUTH_OAUTH:
            client_id = config.get('MARKETING_CLOUD_OAUTH2', 'ClientID')
            client_secret = config.get('MARKETING_CLOUD_OAUTH2', 'ClientSecret')
            refresh_token = config.get('MARKETING_CLOUD_OAUTH2', 'RefreshToken')
            grant_type = "refresh_token"
            pod = config.get('MARKETING_CLOUD_OAUTH2', 'Pod')

            if None in (client_id, client_secret, refresh_token, pod):
                print("Check config file.")

            oauth_url = "https://api" +pod+ ".silverpop.com/oauth/token"

            data = { "grant_type": grant_type,
                 "client_id" : client_id,
                 "client_secret" : client_secret,
                 "refresh_token" : refresh_token}

            r = requests.post(oauth_url,data)
            if r.status_code is 200:
                d = json.loads(r.text)
                self.access_token = d['access_token']
                self.pod = pod
                self.URL = r"https://api{}.silverpop.com/XMLAPI".format(pod)
                self.auth_method = self.AUTH_OAUTH
                return d['expires_in']
            else:
                return False




inst = IBMarketingCloud()
print(inst.authenticate(IBMarketingCloud.AUTH_OAUTH, r"c:\code\ibmapi_config_test.ini"))
print(inst.URL)

