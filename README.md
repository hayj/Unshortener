# Unshortener

This tool unshort urls like `http://bit.ly/XXX` or `http://tinyurl.com/XXX`. It cache all urls you request in a mongo database so the request will be sent one time for each url. The cache is limited so the database will growth with a limit, only old items are removed (in term of get and write).

It use SerializableDict from DatastructureTools.

The structure of the SerializableDict is:

	{
		url1: <data from httpbrowser.HTTPBrowser>,
		...
	}

## Install

	git clone git@github.com:hayj/Unshortener.git
	pip install ./Unshortener/wm-dist/*.tar.gz

Then get the data in the data dir.

## Usage

Call the init:

	uns = Unshortener\
	(
		user=None, password=None, host="localhost", # mongo auth
		shortenersDomainsFilePath="../../data/shorteners.txt", # Set the file path
		useProxy=True, # You can use a proxy
		randomProxyFunct=None, # You can give a random proxy funct
		proxy=None, # Or a proxy
	)

Then use method `uns.isShortener(url)` which answer True if the domain of the url is a shortener.

Use `uns.unshort(url)` to get the unshortened url.

Use `uns.request(url)` to get all the data returned by httpbrowser.HTTPBrowser, it also will cache the data.

## Serialization

By default it use a mongo database, but you can use a pickle file by changing `serializableDictParams` in the init method (set "useMongodb": False). See SerializableDict from DatastructureTools for more informations.

## Proxies

The proxy object must be a dict `{"ip": "xxx.xxx.xxx.xxx", "port": "22", "user": None, "password": None}`