#
# Filename: program.py
# 6/14/2016 12:43 AM
#
#
__author__ = 'measley'

from imc.IBMarketingCloud import IBMCloud
from imc.IBMarketingCloud import ApiResult


if __name__ == "__main__":
    inst = IBMCloud()

    apiresult = inst.login(IBMCloud.AUTH_LEGACY, r"c:\code\ibmapi_config_test.ini")

    print(apiresult.status)
    print(apiresult.message)


    apir = inst.addRecipient(739357, 0, columns={'Email': 'tester{}@gmail2.com'.format(8329)}, updateiffound=True)

    print(apir.status)
    print(apir.message)

    apir2 = inst.logout()

    print(apir2.status)
    print(apir2.message)