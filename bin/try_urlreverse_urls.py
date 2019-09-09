from metapub.urlreverse.urlreverse import *
urllist = open('tests/urlreverse_test_urls.txt').read().split('\n')

for url in [item for item in urllist if item.strip() != '']:
    print(url)
    try:
        urlrev = UrlReverse(url)
        print('doi:', urlrev.doi)
        print('pmid:', urlrev.pmid)

        for step in urlrev.steps:
            print('     * %s' % step)

        print()
        print(urlrev.info)
    except Exception as error:
        print(error)

    print()

