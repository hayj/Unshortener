# coding: utf-8
# cd ~/wm-dist-tmp/Unshortener/unshortener && pew in unshortener-venv python ./test/unshortenertest.py

import os
import sys
sys.path.append('../')

import unittest
import doctest
from unshortener.unshortener import *
import unshortener
from systemtools.basics import *
from systemtools.location import *
from systemtools.file import *

# The level allow the unit test execution to choose only the top level test
min = 0
max = 2
assert min <= max

print("==============\nStarting unit tests...")

if min <= 0 <= max:
    class DocTest(unittest.TestCase):
        def testDoctests(self):
            """Run doctests"""
            doctest.testmod(unshortener)

# if min <= 1 <= max:
#     class Test1(unittest.TestCase):
#         def checkUrl(self, result, expectedLastUrl, expectedStatusCode):
#             self.assertTrue(expectedLastUrl == result["lastUrl"])
#             self.assertTrue(expectedStatusCode == result["status"])
#         def test1(self):
#             for useSelenium in [True, False]:
#                 for storeAll in [True, False]:
#                     uns = Unshortener(dataDir=tmpDir(), storeAll=storeAll, useSelenium=useSelenium, resetBrowsersRate=0.4)
#                     useProxy = not isHostname("datas")
#
#                     url = "http://bit.ly/2AGvbIz"
#                     force = False
#                     expectedLastUrl = "https://stackoverflow.com/questions/24689592/using-python-to-expand-a-bit-ly-link"
#                     expectedStatusCode = 200
#                     result = uns.unshort(url, useProxy=useProxy, force=force)
#                     printLTS(result)
#                     self.checkUrl(result, expectedLastUrl, expectedStatusCode)
#                     self.assertTrue(uns.data.size() == 1)
#
#                     url = "http://httpbin.org/redirect/3"
#                     force = False
#                     result = uns.unshort(url, useProxy=useProxy, force=force)
#                     printLTS(result)
#                     self.assertTrue("domain" in result["message"])
#                     self.assertTrue(uns.data.size() == 1)
#
#                     url = "http://httpbin.org/redirect/3"
#                     force = True
#                     expectedLastUrl = "http://httpbin.org/get"
#                     expectedStatusCode = 200
#                     result = uns.unshort(url, useProxy=useProxy, force=force)
#                     printLTS(result)
#                     self.checkUrl(result, expectedLastUrl, expectedStatusCode)
#                     self.assertTrue(uns.data.size() == 2)
#
#                     url = "https://api.ipify.org/?format=json"
#                     force = True
#                     expectedLastUrl = "https://api.ipify.org/?format=json"
#                     expectedStatusCode = 200
#                     result = uns.unshort(url, useProxy=useProxy, force=force)
#                     printLTS(result)
#                     self.checkUrl(result, expectedLastUrl, expectedStatusCode)
#                     self.assertTrue(uns.data.size() == 3)
#
#                     if isHostname("datas"):
#                         url = "https://www.linkedin.com/?originalSubdomain=fr"
#                         force = True
#                         expectedLastUrl = "https://www.linkedin.com/?originalSubdomain=fr"
#                         expectedStatusCode = 200
#                         result = uns.unshort(url, useProxy=useProxy, force=force)
#                         printLTS(result)
#                         self.checkUrl(result, expectedLastUrl, expectedStatusCode)
#                         self.assertTrue(uns.data.size() == 4)
#
#                         url = "https://www.linkedin.com/?originalSubdomain=fr"
#                         force = False
#                         result = uns.unshort(url, useProxy=useProxy, force=force)
#                         printLTS(result)
#                         self.assertTrue("domain" in result["message"])
#                         self.assertTrue(uns.data.size() == 4)
#
#                     url = "http://bit.ly/21vCb1P"
#                     force = False
#                     expectedLastUrl = "https://api.ipify.org/?format=json"
#                     expectedStatusCode = 200
#                     result = uns.unshort(url, useProxy=useProxy, force=force)
#                     printLTS(result)
#                     self.checkUrl(result, expectedLastUrl, expectedStatusCode)
#                     self.assertTrue(uns.data.size() == 5)
#
#                     url = "http://apprendre-python.com/page-apprendre-variables-debutant-python"
#                     self.assertTrue(not uns.isShortener(url))
#                     self.assertTrue(uns.isShortener("http://bit.ly/21vCb1P"))
#
#                     # Here a javascript redirection is not handled by Unshortener
#                     url = "www.mon-ip.com/dsfdsgdrfg"
#                     force = True
#                     expectedLastUrl = "http://www.mon-ip.com/dsfdsgdrfg"
#                     if useSelenium:
#                         expectedLastUrl = "http://www.mon-ip.com/page404.php"
#                     expectedStatusCode = 403
#                     if useSelenium:
#                         expectedStatusCode = 404
#                     result = uns.unshort(url, useProxy=useProxy, force=force)
#                     printLTS(result)
#                     self.checkUrl(result, expectedLastUrl, expectedStatusCode)
#                     if storeAll or useSelenium:
#                         self.assertTrue(uns.data.size() == 6)
#                     else:
#                         self.assertTrue(uns.data.size() == 5)
#
#                     uns.close()
#                     self.assertTrue(fileExists(tmpDir() + "/unshortener-database.pickle.zip"))
#                     uns.data.reset()
#                     self.assertTrue(not fileExists(tmpDir() + "/unshortener-database.pickle.zip"))

urls = \
[
    "https://stackoverflow.com/questions/4014621/a-python-class-that-acts-like-dict",
    "https://www.koreus.com/videos/nouveau/",
    "https://github.com",
]

if min <= 2 <= max:
    class Test2(unittest.TestCase):
        def isNews(self, url):
            if "stackoverflow" in url:
                return True
            return False
        def isNews2(self, url):
            if "koreus" in url:
                return True
            return False
        def test1(self):
            for serializableDictParams in \
            [
                {
                    "limit": 5,
                    "useMongodb": True,
                    "name": "unshortenedurls-test",
                    "cacheCheckRatio": 0.0,
                    "mongoIndex": "url",
                },
                {
                    "limit": 5,
                    "useMongodb": False,
                    "name": "unshortenedurls-test",
                    "cacheCheckRatio": 0.0,
                    "mongoIndex": "url",
                },
            ]:
                uns = Unshortener(user=None, password=None, host="localhost",
                                  serializableDictParams=serializableDictParams)
                urlParser = URLParser()
                for url in urls:
                    domain = urlParser.getDomain(url)
                    uns.shortenersDomains.append(domain)
                uns.data.reset()
                self.assertTrue(uns.data.size() == 0)
                for url in urls:
                    uns.unshort(url)
                self.assertTrue(uns.data.size() == 3)
                for key, current in uns.data.items():
                    self.assertTrue(current["html"] is not None)
                uns.reduceIrrelevantUrls(self.isNews)
                countNone = 0
                countRelevant = 0
                for key, current in uns.data.items():
                    if current["html"] is None:
                        countNone += 1
                    if current["relevant"]:
                        countRelevant += 1
                self.assertTrue(countNone == 2)
                self.assertTrue(countRelevant == 1)
                # Here we have an error logged
                uns.reduceIrrelevantUrls(self.isNews2)
                # Now we don't have any html:
                countNone = 0
                for key, current in uns.data.items():
                    if current["html"] is None:
                        countNone += 1
                self.assertTrue(countNone == 3)
                uns.data.reset()



if __name__ == '__main__':
    unittest.main() # Or execute as Python unit-test in eclipse


print("Unit tests done.\n==============")