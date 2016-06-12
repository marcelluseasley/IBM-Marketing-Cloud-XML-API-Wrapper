#
# Filename: RecipientOptions.py
# 6/12/2016 5:06 AM
#
#
__author__ = 'Marcellus Easley'

class Recipient(object):


    def __init__(self, listId=None, columns=None):
        self.listId = listId
        self.columns = columns
        self.createdFrom = None
        self.sendAutoReply = None
        self.updateIfFound = None
        self.allowHTML = False
        self.visitorKey = None
        self.contactLists = None
        self.syncFields = None
        self.oldEmailAddress = None
        self.emailAddress = None
        self.recipientId = None
        self.encodedRecipientId = None
        self.snoozed = None
        self.resumeSendDate = None
        self.daysToSnooze = None
        self.jobId = None
        self.returnContactLists = None



    @property
    def listid(self):
        return self.listid

    @property
    def listid(self, value):
        self.listid = value

    @property
    def allowHTML(self):
        return self.allowHTML

    @property
    def allowHTML(self, value):
        self.allowHTML = value

    @property
    def emailAddress(self):
        return self.emailAddress

    @property
    def emailAddress(self, value):
        self.emailAddress = value