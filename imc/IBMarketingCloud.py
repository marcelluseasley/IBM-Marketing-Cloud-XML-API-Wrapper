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


class IBMCloud(object):

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
        self.authenticated = False

    def login(self, auth_method=AUTH_LEGACY, config_file=None):

        self.auth_method = auth_method

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
                ar = ApiResult(r)
                root = objectify.fromstring(ar.message)
                print(etree.tostring(root, pretty_print=True))

                if root.Body.RESULT.SUCCESS.text == "false":
                    return ar
                elif root.Body.RESULT.SUCCESS.text == "true":
                    self.jsessionid = root.Body.RESULT.SESSIONID
                    self.authenticated = True
                    return ar
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

            oauth_url = "https://api" + pod + ".silverpop.com/oauth/token"

            data = {"grant_type": grant_type,
                    "client_id": client_id,
                    "client_secret": client_secret,
                    "refresh_token": refresh_token}

            r = requests.post(oauth_url, data)
            if r.status_code is 200:
                d = json.loads(r.text)
                self.access_token = d['access_token']
                self.pod = pod
                self.URL = r"https://api{}.silverpop.com/XMLAPI".format(pod)
                self.auth_method = self.AUTH_OAUTH
                self.authenticated = True
                return d['expires_in']
            else:
                return False

    def _runapi(self, xml=None):
        if self.authenticated:
            xml = xml.replace('&lt;', '<').replace('&gt;', '>')
            if self.auth_method is self.AUTH_LEGACY:
                #set legacy URL and jsession
                paramstring = {"jsessionid": self.jsessionid, "xml": xml}
                r = requests.post(self.URL, paramstring)
                return ApiResult(r)


            elif self.auth_method is self.AUTH_OAUTH:
                #set oauth URL
                headers = {'Authorization': "Bearer " + self.access_token}
                data = {'xml': xml}
                r = requests.post(self.URL, headers=headers, data=data)
                return ApiResult(r)

        else:
            return False


    def addRecipient(self, listid=None, createdfrom=None, sendautoreply=False,
                     updateiffound=False, allowhtml=False, visitorkey=None,
                     contactlists=None, syncfields=None, columns=None):



        if None in (listid, createdfrom, columns):
            return False

        envelopeNode = Element("Envelope")
        bodyNode = SubElement(envelopeNode, "Body")
        addRecipientNode = SubElement(bodyNode, "AddRecipient")

        listIdNode = SubElement(addRecipientNode, "LIST_ID")
        listIdNode.text = str(listid)
        createdfromNode = SubElement(addRecipientNode, "CREATED_FROM")
        createdfromNode.text = str(createdfrom)

        if sendautoreply:
            sendautoreplyNode = SubElement(addRecipientNode, "SEND_AUTOREPLY")
            sendautoreplyNode.text = str(sendautoreply)

        if updateiffound:
            updateiffoundNode = SubElement(addRecipientNode, "UPDATE_IF_FOUND")
            updateiffoundNode.text = str(updateiffound)

        if allowhtml:
            allowhtmlNode = SubElement(addRecipientNode, "ALLOW_HTML")
            allowhtmlNode.text = str(allowhtml)

        if visitorkey:
            visitorkeyNode = SubElement(addRecipientNode, "VISITOR_KEY")
            visitorkeyNode.text = str(visitorkey)

        if contactlists:
            if isinstance(contactlists, list) or isinstance(contactlists, tuple):
                contactlistsNode = SubElement(addRecipientNode, "CONTACT_LISTS")
                clists=""
                for i in len(contactlists):
                    clists += "<CONTACT_LIST_ID>{}</CONTACT_LIST_ID>".format(i)

                contactlistsNode.text = clists

        if syncfields:
            if isinstance(syncfields, dict):
                syncfieldsNode = SubElement(addRecipientNode, "SYNC_FIELDS")
                sfields = ""
                for name, value in syncfields.items():
                    sfields += """<SYNC_FIELD>
                                <NAME>{}</NAME>
                                <VALUE>{}</VALUE>
                                </SYNC_FIELD>""".format(name,value)
                syncfieldsNode.text = sfields

        if columns:
            if isinstance(columns, dict):
                columnsNode = SubElement(addRecipientNode,"COLUMN")
                scolumns = ""
                for name, value in columns.items():
                    scolumns += """<NAME>{}</NAME>
                                    <VALUE>{}</VALUE>""".format(name, value)
                columnsNode.text = scolumns

        addrecipientxml = etree.tostring(envelopeNode)
        return self._runapi(addrecipientxml)

    def logout(self):
        envelope = Element("Envelope")
        body = SubElement(envelope, "Body")
        login = SubElement(body, "Logout")
        logoutXML = etree.tostring(envelope, encoding="UTF-8")

        return self._runapi(logoutXML)


    def rawRecipientDataExport(self, mailingid=None, reportid=None, campaignid=None,
                               listid=None, includechildren=False, eventdatestart=None,
                               eventdateend=None, senddatestart=None, senddateend=None,
                               exportformat=None, fileencoding=None, exportfilename=None,
                               email=None, movetoftp=False, private=False, shared=False,
                               sentmailings=False, sending=False, optinconfirmation=False,
                               profileconfirmation=False, automated=False, campaignactive=False,
                               campaigncompleted=False, campaigncancelled=False,
                               campaignscrapetemplate=False, includetestmailings=False,
                               alleventtypes=False, sent=False, suppressed=False, opens=False,
                               clicks=False, optins=False, optouts=False, forwards=False,
                               attachments=False, conversions=False, clickstreams=False,
                               hardbounces=False, softbounces=False, replyabuse=False,
                               replycoa=False, replyother=False, mailblocks=False,
                               mailingrestrictions=False, includeseeds=False,
                               includeforwards=False, includeinboxmonitoring=False,
                               codedtypefields=False, excludedeleted=False, forwardsonly=False,
                               returnmailingname=False, returnsubject=False,
                               returncrmcampaignid=False, returnprogramid=False, columns=None):
        """Raw Recipient Data Export """

        envelopeNode = Element("Envelope")
        bodyNode = SubElement(envelopeNode, "Body")
        addRecipientNode = SubElement(bodyNode, "RawRecipientDataExport")

        if mailingid:
            mailingidNode = SubElement(addRecipientNode, "MAILING_ID")
            mailingidNode.text = str(mailingid)

        if reportid:
            reportidNode = SubElement(addRecipientNode, "REPORT_ID")
            reportidNode.text = str(reportid)

        if campaignid:
            campaignidNode = SubElement(addRecipientNode, "CAMPAIGN_ID")
            campaignidNode.text = str(campaignid)

        if listid:
            listidNode = SubElement(addRecipientNode, "LIST_ID")
            listidNode.text = str(listid)

        if includechildren:
            includechildrenNode = SubElement(addRecipientNode, "INCLUDE_CHILDREN")
            includechildrenNode.text = str(includechildren)





class ApiResult(object):

    def __init__(self, response):
        self._status = response.status_code
        self._message = response.text

    def __str__(self):
        return self._status


    @property
    def status(self):
        return self._status

    @status.setter
    def status(self, value):
        self._status = value

    @property
    def message(self):
        return self._message

    @message.setter
    def message(self, value):
        self._message = value













