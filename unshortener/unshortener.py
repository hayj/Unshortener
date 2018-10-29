# coding: utf-8

# pew in unshortener-venv python ~/wm-dist-tmp/Unshortener/unshortener/unshortener.py

import requests
from datatools.url import *
from urllib.request import urlopen
from systemtools.basics import *
from systemtools.location import *
from systemtools.logger import *
import requests.auth
from datastructuretools.hashmap import *
from hjwebbrowser.httpbrowser import *
from hjwebbrowser.browser import *
from hjwebbrowser.utils import *
from threading import Thread
try:
    from systemtools.hayj import *
except: pass
import random
from unshortener import config as unsConfig


class Unshortener():
    """
        See the README
    """
    def __init__ \
    (
        self,
        logger=None,
        verbose=True,
        serializableDictParams=\
        {
            "limit": 10000000,
            "name": "unshortenedurls",
            "cacheCheckRatio": 0.0,
            "mongoIndex": "url",
        },
        httpBrowserParams=\
        {
            "maxRetryWithoutProxy": 0,
            "maxRetryIfTimeout": 1,
            "maxRetryIf407": 1,
        },
        user=None, password=None, host=None,
        useMongodb=None,
        hostname=None,
        shortenersDomainsFilePath=None,
        retryFailedRatio=0.5,
        useProxy=True,
        randomProxyFunct=None,
        timeout=25,
        maxRetry=2,
        nextTriesTimeoutRatio=0.3,
        readOnly=False,
        proxy=None,
    ):
        self.useMongodb = useMongodb
        if self.useMongodb is None:
            self.useMongodb = unsConfig.useMongodb

        # We store some params:
        self.retryFailedRatio = retryFailedRatio
        self.verbose = verbose
        self.logger = logger
        self.timeout = timeout
        self.maxRetries = maxRetry
        self.nextTriesTimeoutRatio = nextTriesTimeoutRatio
        self.readOnly = readOnly
        self.proxy = proxy

        # We create the url parser:
        self.urlParser = URLParser()

        # We get the default randomProxyFunct:
        self.useProxy = useProxy
        self.randomProxyFunct = randomProxyFunct
        if self.randomProxyFunct is None:
            try:
                self.randomProxyFunct = getRandomProxy
            except: pass
        if self.randomProxyFunct is None:
            self.useProxy = False

        # We init the mongo collection through SerializableDict:
        self.serializableDictParams = serializableDictParams
        if hostname is None: hostname = unsConfig.hostname
        if host is None: host = unsConfig.host
        if user is None: user = unsConfig.user
        if password is None: password = unsConfig.password
        if user == "hayj":
            try:
                (user, password, host) = getMongoAuth(user=user, hostname=hostname)
            except: pass
        self.serializableDictParams["user"] = user
        self.serializableDictParams["password"] = password
        self.serializableDictParams["host"] = host
        self.serializableDictParams["logger"] = self.logger
        self.serializableDictParams["verbose"] = self.verbose
        self.serializableDictParams["useMongodb"] = self.useMongodb
        self.data = SerializableDict(**self.serializableDictParams)

        # We get shorteners domains:
        self.shortenersDomainsFilePath = shortenersDomainsFilePath
        if self.shortenersDomainsFilePath is None:
            self.shortenersDomainsFilePath = getDataDir() + "/Misc/crawling/shorteners.txt"
        self.shortenersDomains = None
        self.initShortenersDomains()

        # We create the http browser:
        self.httpBrowserParams = httpBrowserParams
        self.httpBrowser = HTTPBrowser(logger=self.logger,
                                       verbose=self.verbose,
                                       **self.httpBrowserParams)

    def initShortenersDomains(self):
        if self.shortenersDomains is None:
            if not isFile(self.shortenersDomainsFilePath):
                raise Exception("File " + str(self.shortenersDomainsFilePath) + " not found.")
            shorteners = fileToStrList(self.shortenersDomainsFilePath, removeDuplicates=True)
            newShorteners = []
            for current in shorteners:
                current = current.lower()
                newShorteners.append(current)
            shorteners = newShorteners
            self.shortenersDomains = set()
            for current in shorteners:
                newCurrent = self.urlParser.getDomain(current)
                self.shortenersDomains.add(newCurrent)
            self.shortenersDomains = list(self.shortenersDomains)
            # We filter all by presence of a point:
            newShortenersDomains= []
            for current in self.shortenersDomains:
                if "." in current:
                    newShortenersDomains.append(current)
            self.shortenersDomains = newShortenersDomains

    def reduceIrrelevantUrls(self, isRelevantUrlFunct):
        """
            If some last urls are not enough relevant to keep the html content
            You can delete it by call this method
            You have to give a funct in params
            This method can take a long time and will update all row so you will loose
            old/new read/write sort.
        """
        for theHash, current in self.data.items():
            if isRelevantUrlFunct(current["lastUrl"]):
                if dictContains(current, "relevant") and not current["relevant"]:
                    logError("You previously set this row as irrelevant but now you set it as relevant, so you lost the html data, you can re-set the html data using hjwebbrowser.httpbrowser.HTTPBrowser", self)
                    logError(reduceDictStr(current), self)
                self.data.updateRow(theHash, "relevant", True)
            else:
                self.data.updateRow(theHash, "html", None)
                self.data.updateRow(theHash, "relevant", False)

    def getUnshortenersDomains(self):
        return self.shortenersDomains

    def close(self):
        self.data.close()


    def isShortened(self, *args, **kwargs):
        return self.isShortener(*args, **kwargs)
    def isShortener(self, url):
        """
            Use this method to test if an url come from an unshortener service
        """
        smartDomain = self.urlParser.getDomain(url)
        return smartDomain in self.shortenersDomains

    def has(self, *args, **kwargs):
        return self.hasKey(*args, **kwargs)
    def isAlreadyUnshortened(self, *args, **kwargs):
        return self.hasKey(*args, **kwargs)
    def hasKey(self, url):
        """
            This method test if an url was already unshortened before
        """
        url = self.urlParser.normalize(url)
        return self.data.hasKey(url)


    def unshort\
    (
        self,
        *args,
        **kwargs
    ):
        """
            This method will call request but give the last url (unshortened) instead
            of all data
        """
        result = self.request(*args, **kwargs)
        if result is None:
            return None
        else:
            if dictContains(result, "lastUrl"):
                return result["lastUrl"]
            else:
                return None

    def add(self, result, onlyHttpBrowser=True):
        # We check readOnly:
        if self.readOnly:
            logError("The unshortener is set as read only!", self)
            return False
        # We check None:
        if result is None or not isinstance(result, dict):
            logError("No data found to add in unshortener!", self)
            return False
        resultStr = lts(reduceDictStr(result))
        # We check keys:
        for key in \
        [
            "lastUrl", "browser",
            "lastUrlDomain", "historyCount", "html",
            "title", "status",
        ]:
            if key not in result:
                logError(key + " is not in:\n" + resultStr, self)
                return False
        # We check keys not None:
        for key in ["url", "domain"]:
            if not dictContains(result, key):
                logError(key + " is not in:\n" + resultStr, self)
                return False
        # We check the browser:
        if onlyHttpBrowser and result["browser"] != "http":
            logError("The browser must be an http browser!", self)
            return False
        # We delete and add some elements:
        if "crawlingElement" in result:
            del result["crawlingElement"]
        if "relevant" not in result:
            result["relevant"] = True
        # We check the status:
        if result["httpStatus"] == 200 or result["httpStatus"] == 404:
            # We add the data:
            self.data[result["url"]] = result
            return True
        else:
            logError("Cant't add this data to unshortener because of the http status:\n"\
                      + resultStr, self)
            return False
        return False

    def request\
    (
        self,
        url,
        force=False,
        retriesCount=0,
    ):
        """
            This method will request the given url
            You can read the last url (unshortened) in the field "lastUrl" of the returned dict
            If the request failed, this method return None
            force as True will give the last url for the request, even if it is not a shortener...
        """
        # We set the timeout:
        timeout = self.timeout
        if retriesCount >= 1:
            timeout = int(self.nextTriesTimeoutRatio * timeout)
        # We parse the url:
        url = self.urlParser.normalize(url)
        smartDomain = self.urlParser.getDomain(url)
        # We return None if we don't have to request it:
        thisIsAShortener = smartDomain in self.shortenersDomains
        if not force and not thisIsAShortener:
            return None
        # We check if we already have the url:
        if self.data.hasKey(url):
            # log(url + " was in the Unshortener database!", self)
            return self.data.get(url)
        # If we read only, we don't request the url:
        elif self.readOnly:
#             log(url + " is not in the database and the unshortener was set as read only!", self)
            return None
        # Else we can request it:
        else:
            # We get a random proxy:
            proxy = None
            if self.useProxy:
                proxy = self.proxy
                if proxy is None:
                    proxy = self.randomProxyFunct()
            # We set the proxy and the timeout:
            self.httpBrowser.setProxy(proxy)
            self.httpBrowser.setTimeout(timeout)
            # We request the url:
            result = self.httpBrowser.get(url)
            # We add some params to the result:
            result["url"] = url
#             result["isShortener"] = thisIsAShortener
            result["relevant"] = True
            # And if the request succeded:
#             if result["status"] == REQUEST_STATUS.duplicate or \
#                result["status"] == REQUEST_STATUS.success or \
#                result["status"] == REQUEST_STATUS.error404 or \
#                result["status"] == REQUEST_STATUS.timeoutWithContent:
            if result["httpStatus"] == 200 or \
               result["httpStatus"] == 404:
                # We add the row:
                self.data[url] = result
                # We log it:
                log("Unshort succedded: " + url, self)
                log(getRequestInfos(result), self)
                # And finally we return the result:
                return result
            # Else we retry:
            else:
                # We log the error:
                log("Unshort failed: " + url, self)
                log(getRequestInfos(result), self)
#                 log(listToStr(reduceDictStr(result, replaceNewLine=True)), self)
                # If we can retry:
                if retriesCount < self.maxRetries:
                    # We recursively call the method:
                    log("We retry to unshort: " + url, self)
                    return self.request(url,
                                        force=force,
                                        retriesCount=retriesCount+1)
                # If we failed, we just return None:
                else:
                    return None

def getRequestInfos(result):
    return str(result["proxy"]) + " " + str(result["status"].name) + " (" + str(result["httpStatus"]) + ")"

def test1():
    uns = Unshortener(host="localhost")
    url = "https://api.ipify.org/?format=json"
#     url = "http://httpbin.org/redirect/3"
    printLTS(uns.unshort(url, force=True))

def test2():
    uns = Unshortener(host="localhost")
    printLTS(uns.getUnshortenersDomains())

def test3():
    def getShares(crawlOrScrap):
        if dictContains(crawlOrScrap, "scrap"):
            scrap = crawlOrScrap["scrap"]
        else:
            scrap = crawlOrScrap
        if dictContains(scrap, "tweets"):
            tweets = scrap["tweets"]
            for tweet in tweets:
                if dictContains(tweet, "shares"):
                    for share in tweet["shares"]:
                        yield share

    uns = Unshortener(host="localhost", useProxy=False)
    (user, password, host) = getStudentMongoAuth()
    collection = MongoCollection("twitter", "usercrawl",
                                 user=user, password=password, host=host)
    i = 0
    for current in collection.find():
        urls = list(getShares(current))
        for url in urls:
            url = url["url"]
            if getRandomFloat() > 0.8 and (uns.isShortener(url) or getRandomFloat() > 0.95):
                print(url)
                print("isShortener: " + str(uns.isShortener(url)))
                print(uns.unshort(url, force=True))
                print()
                print()
                print()
                print()
#                 input()
                i += 1
                if i > 100:
                    exit()

def test4():
    urls = \
    [
        "http://ow.ly/DIFx30hfmsE",
        "http://bit.ly/2jBKQoh",
    ]
    uns = Unshortener(host="localhost")
    print()
    print()
    print()
    print()
    for url in urls:
        print(url)
        print("isShortener: " + str(uns.isShortener(url)))
        print(uns.unshort(url, force=True))
        print()
        print()
        print()
        print()

def testAlexis():
    uns = Unshortener\
    (
        shortenersDomainsFilePath="/tmp",
        useProxy=False,
        randomProxyFunct=None,
        proxy=None,
        serializableDictParams=\
        {
            "limit": 10000000,
            "useMongodb": False,
            "name": "unshortenedurls",
            "cacheCheckRatio": 0.0,
            "mongoIndex": "url",
            "serializeEachNAction": 1,
        }
    )
    print(uns.unshort("https://bit.ly/2Hor6PN"))

if __name__ == '__main__':
#     test1()
#     test2()
#     test3()
#     test4()
    testAlexis()





