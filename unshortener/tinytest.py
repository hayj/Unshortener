

from systemtools.basics import *
from systemtools.duration import *
from systemtools.file import *
from systemtools.logger import *
from systemtools.location import *
from systemtools.system import *

from hjwebbrowser.httpbrowser import *


# On a 10% des user twitter qui utilisent des tinyurl.com
# erreur 403, tinyurl.com renvoie vers une page captcha, mais heuresement pas de status 200
# Le success ratio tourne autour de 0.5 que ce soit pour les liens preview que pour les liens normaux,
# donc ça ne sert à rien d'utiliser les liens previews


def testSuccess():
    successCount = 0
    doneCount = 0
    for url in urls:
        proxy = getRandomProxy()
        b = HTTPBrowser(proxy=proxy)
        result = b.html(url)
#         strToTmpFile(result["html"])
        if result["httpStatus"] == 200:
            successCount += 1
        doneCount += 1
        print("succes ratio: " + str(successCount / doneCount))


def tinyUrlToPreview(urls):
    def privateTinyUrlToPreview(url):
        if url is None:
            return None
        elif url.startswith("https"):
            return "http://preview." + url[8:]
        elif url.startswith("http"):
            return "http://preview." + url[7:]
        else:
            return None
    if isinstance(urls, list):
        newUrls = []
        for url in urls:
            newUrls.append(privateTinyUrlToPreview(url))
        return newUrls
    else:
        return privateTinyUrlToPreview(urls)




urls = fileToStrList(execDir(__file__) + "/datatest/tinyurls.txt")
random.shuffle(urls)

# urls = tinyUrlToPreview(urls)
#
# # printLTS(tinyUrlToPreview(urls))
# # exit()
#
#
# proxy = getRandomProxy()
# b = HTTPBrowser(proxy=proxy)
# result = b.html(urls[0])
# strToTmpFile(result["html"], "tinytest.html")


# import requests
#
# cookie = {'preview': '1'}
#
#
# r = requests.post('http://wikipedia.org', cookies=cookie)


testSuccess()
