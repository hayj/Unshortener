class UnshortenerOld():
    """
        Todo option selenium ?
    """
    def __init__(self,
                 logger=None,
                 verbose=True,
                 maxItemCount=100000000,
                 maxDataSizeMo=10000,
                 dataDir=None,
                 seleniumBrowserCount=20,
                 resetBrowsersRate=0.1,
                 useSelenium=False,
                 seleniumBrowsersIsNice=True,
                 storeAll=False,
                 readOnly=False,
                 shortenersDomainsFilePath=None):
        self.readOnly = readOnly
        self.seleniumBrowsersIsNice = seleniumBrowsersIsNice
        self.resetBrowsersRate = resetBrowsersRate
        self.seleniumBrowserCount = seleniumBrowserCount
        self.shortenersDomainsFilePath = shortenersDomainsFilePath
        if self.shortenersDomainsFilePath is None:
            self.shortenersDomainsFilePath = getDataDir() + "/Misc/crawling/shorteners.txt"
        self.useSelenium = useSelenium
        self.storeAll = storeAll
        self.maxDataSizeMo = maxDataSizeMo
        self.maxItemCount = maxItemCount
        self.dataDir = dataDir
        if self.dataDir is None:
            self.dataDir = getDataDir() + "/Misc/crawling/"
        self.fileName = "unshortener-database"
        self.urlParser = URLParser()
        self.requestCounter = 0
        self.verbose = verbose
        self.logger = logger
        self.data = SerializableDict \
        (
            self.dataDir, self.fileName,
            cleanMaxSizeMoReadModifiedOlder=self.maxDataSizeMo,
            limit=self.maxItemCount,
            serializeEachNAction=20,
            verbose=True
        )
        self.shortenersDomains = None
        self.initShortenersDomains()
        self.browsers = None

    def initShortenersDomains(self):
        if self.shortenersDomains is None:
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

    def getUnshortenersDomains(self):
        return self.shortenersDomains

    def close(self):
        self.data.close()

    def isShortener(self, url):
        smartDomain = self.urlParser.getDomain(url)
        return smartDomain in self.shortenersDomains

    def isStatusCodeOk(self, statusCode):
        if isinstance(statusCode, dict) and dictContains(dict, "statusCode"):
            statusCode = statusCode["statusCode"]
        return statusCode == 200

    def generateSeleniumBrowsers(self):
        # We have to reset browsers sometimes because it can take a lot of RAM:
        if self.browsers is None or getRandomFloat() < self.resetBrowsersRate:
            if self.browsers is not None:
                for browser in self.browsers:
                    browser.quit()
            self.browsers = []
            def generateRandomBrowser(proxy):
                self.browsers.append(Browser(driverType=DRIVER_TYPE.phantomjs, proxy=proxy))
            allThreads = []
            for i in range(self.seleniumBrowserCount):
                theThread = Thread(target=generateRandomBrowser, args=(getRandomProxy(),))
                theThread.start()
                allThreads.append(theThread)
            for theThread in allThreads:
                theThread.join()

    def getRandomSeleniumBrowser(self):
        return random.choice(self.browsers)

    def unshort(self, url, force=False, useProxy=True, timeout=20, retryIf407=True):
        """
            force as False will check if the given url have to match with a known shorter service
            force as True will give the last url for the request...
        """
        url = self.urlParser.normalize(url)
        smartDomain = self.urlParser.getDomain(url)
        if not force and smartDomain not in self.shortenersDomains:
            result = \
            {
                "force": force,
                "url": url,
                "message": "The domain is not a shortener service!",
                "status": -1,
            }
            return result
        if self.data.hasKey(url):
            log(url + " was in the Unshortener database!", self)
            return self.data.get(url)
        elif self.readOnly:
            result = \
            {
                "force": force,
                "url": url,
                "message": "The url is not in the database and the unshortener was set as read only.",
                "status": -2,
            }
            return result
        else:
            log("Trying to unshort " + url, self)
            proxy = None
            if useProxy:
                proxy = getRandomProxy()
            seleniumFailed = False
            if self.useSelenium:
                self.generateSeleniumBrowsers()
                browser = self.getRandomSeleniumBrowser()
                result = browser.html(url)
                if result["status"] == REQUEST_STATUS.refused or \
                result["status"] == REQUEST_STATUS.timeout:
                    seleniumFailed = True
                    logError("Selenium failed to get " + url + "\nTrying with a HTTPBrowser...", self)
                else:
                    result = convertBrowserResponse(result, browser, nice=self.seleniumBrowsersIsNice)
            if not self.useSelenium or seleniumFailed:
                httpBrowser = HTTPBrowser(proxy=proxy, logger=self.logger, verbose=self.verbose)
                result = httpBrowser.get(url)
            result["force"] = force

            if self.storeAll or result["status"] == 200 or result["status"] == 404:
                self.data.add(url, result)
            del result["html"]
            log("Unshort of " + result["url"] + " : " + str(result["status"]), self)
            return result