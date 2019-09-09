# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

import zipfile
import os, logging

from six.moves import urllib

import requests
from requests.packages import urllib3

REQUESTS_TIMEOUT = 2000

#DEFAULT_HEADERS = { 
#    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/534.30 (KHTML, like Gecko) Ubuntu/11.04 Chromium/12.0.742.112 Chrome/12.0.742.112 Safari/534.30', 
#                  }

DEFAULT_HEADERS = {}

log = logging.getLogger('library.downloader')

#suppress those unfortunate SSL-cert warnings from journal websites.
urllib3.disable_warnings()


def get_filetype(filepath):
    '''Read file's "magic number" string and return it.

    Args:
        filepath (str): path to file

    Returns:
        string containing magicNumber (e.g. "%PDF")
    '''
    with open(filepath, 'rb') as infile:
        magicNumber = infile.read(4)
        return magicNumber
    return None

def is_pdf_file(filepath):
    '''Use file's "magic number" string to check whether the file is a PDF.

    Args:
        filepath (str): path to file

    Returns:
        True if PDF, False if not (or filepath invalid)
    '''
    filetype = get_filetype(filepath)
    if filetype:
        return filetype=='%PDF'
    return False

def has_nonzero_filesize(filepath, min_size=1):
    '''Call get_filesize on specified filepath to determine bytesize of file,
    and compares this to min_size (default 1).  Return True if filesize > min_size
    and False if otherwise (or if filepath not extant on filesystem).

    Args:
        filepath (str): path to file
        min_size (int): minimum byte size to be considered "nonzero" (optional)

    Returns:
        True if file meets above conditions, False otherwise.
    '''
    size = get_filesize(filepath)
    if size and size > min_size:
        return True
    return False

def get_filesize(filepath):
    '''Return filesize of specified filepath.

    Args:
        filepath (str): path to file

    Returns:
        int or None: size of file in bytes or None if filepath invalid
    '''
    if os.path.exists(filepath):
        # check that it has a nonzero filesize
        filestat = os.stat(filepath)
        return filestat.st_size
    return None


class DownloadResult(object):
    '''Encapsulates the result conditions of an action the Downloader took.'''

    def __init__(self, **kwargs):
        self.filepath = kwargs.get('filepath', None)
        self.url = kwargs.get('url', None)
        self.source = kwargs.get('source', None)
        self.status_code = kwargs.get('status_code', None)
        self.content_type = kwargs.get('content_type', None)
        self.filetype = kwargs.get('filetype', None)
        self.filesize = kwargs.get('filesize', None)
        self.method = kwargs.get('method', 'GET')
        self.params = kwargs.get('params', None)

    def inspect_file(self):
        '''if file exists on filesystem, mutate this object's `filesize` and
        `filetype` attributes to describe the file.'''
        self.filesize = get_filesize(self.filepath)
        self.filetype = get_filetype(self.filepath)

    @property
    def ok(self):
        '''magic attribute to check whether file downloaded is "OK" -- i.e. it is
        present on the filesystem and has a filesize greater than 1 bytes.'''
        self.inspect_file()
        if self.filesize > 1:
            return True
        return False

    def __str__(self):
        ok = '(OK)' if self.ok else ''
        return '{dlrs.url} --> {dlrs.filepath} {ok}'.format(dlrs=self, ok=ok)

class Downloader(object):
    '''handles downloading of PDFs to a temporary location.

    In the not too distant future, it should do nice things that keep us from losing access
    privileges to PMC and the like, such as batch-timing.'''

    TMPDIR = '/tmp'
    TMPFILE_TMPL = '{pmid}.pdf'
    
    def get_tmppath_for_pmid(self, pmid):
        return os.path.join(self.TMPDIR, self.TMPFILE_TMPL.format(pmid=pmid))

    def get_tmppath(self, filename):
        return os.path.join(self.TMPDIR, filename)

    def unzip(self, zipfilepath, destdir=None, remove_zip=False):
        '''unzip zipfilepath into specified destdir (if specified), or into its own 
        directory if destdir not specified.
    
        If remove_zip param True (default: False), remove the source zip file
        after successful extraction.

        Args:
            zipfilepath (str): absolute path to zipfile
            destdir (str): optional, default None
            remove_zip (bool): optional, default False
        
        Returns:
            :param: zipfilepath (string) - absolute path to zipfile
            :param: destdir (string) [default: None] 
            :param: remove_zip (bool) [default: False] 
            :return: list of absolute paths to the extracted files.
        '''
        if not destdir:
            destdir = os.path.split(zipfilepath)[0]

        with zipfile.ZipFile(zipfilepath, "r") as the_zip:
            the_zip.extractall(destdir)

        results = []
        for fname in os.listdir(destdir):
            if fname != os.path.split(zipfilepath)[1]:
                results.append(os.path.join(destdir, fname))

        if remove_zip:
            os.remove(zipfilepath)

        return results


    def article_from_sources(self, pmid, sources):
        '''takes pmid and list of ranked ArticleSources, iterates over each source.url 
        until it successfully downloads the desired file.

        If PDF successfully downloaded, return the DownloadResult object containing
        the url and name of the source used to download the file.

        If all sources become exhausted, return None.

        Args:
            pmid (str)
            sources (list) - list of ArticleSource objects

        Returns:
            DownloadResult object or None
        '''
        filepath = self.get_tmppath_for_pmid(pmid)
        for source in sources:
            # try downloading from explicit URLs
            if source.url and source.source != 'filesystem':
                dlrs = self.request_write_file(source.url, filepath, 'pdf')
                if dlrs.ok:
                    dlrs.source = source.source
                    return dlrs
        return None

    def request_write_file(self, url, filepath, expected_filetype=None, post_args=None,
                           headers=DEFAULT_HEADERS, timeout=REQUESTS_TIMEOUT):
        '''
        Args:
            url (str): target url pointing to content for download via HTTP
            filepath (str): output filepath
            post_args (dict): arguments to submit as POST request [default: None]
            headers (dict): HTTP headers to submit with query [default: downloader.DEFAULT_HEADERS]
            timeout (int): milliseconds to wait for a response [default: downloader.REQUESTS_TIMEOUT] 

        Returns:
            DownloadResult object
        '''
        # create a DownloadResult object to represent the outcome of this operation.
        dlrs = DownloadResult(url=url, filepath=filepath)

        check_if_pdf = False
        if expected_filetype:
            check_if_pdf = True if expected_filetype.lower()=='pdf' else False

        # verify=False means it ignores bad SSL certs
        if post_args:
            response = requests.post(url, stream=True, verify=False, data=post_args,
                                        timeout=timeout, headers=headers)
        else:
            response = requests.get(url, stream=True, verify=False, 
                                        timeout=timeout, headers=headers)

        drsp.status_code = response.status_code
        drsp.content_type = response.headers['content-type']

        if response.status_code == 200:
            # If it's sending us something we're not expecting, cut it off right away:
            if expected_filetype and expected_filetype.lower() not in response.headers.get('content-type'):
                drsp.status_code = 200
                drsp.content_type = response.headers['content-type']
                drsp.filepath = None
                return drsp

            # If we don't care what it is, or we do care and our filetype expectations are met:
            else:
                with open(filepath, 'wb') as handle:
                    for block in response.iter_content(1024):
                        if not block:
                            break
                        handle.write(block)

        # update DownloadResult's filetype and filesize characteristics
        drsp.inspect_file()
        return drsp

    def ftp(self, url, filepath):
        '''Uses FTP to download file from designated url to designated filepath.

        Args:
            url (str): link to ftp resource (must include "ftp://")
            filepath (str): output filepath

        Returns:
            DownloadResult object
        '''
        dlrs = DownloadResult(url=url, filepath=filepath)
        result = urllib.request.urlretrieve(url, filepath)
        dlrs.status_code = result[0]
        return dlrs

    def ftp_get_remote_filesize(self, url):
        '''Uses FTP to check and return integer 'content-length' value of remote file 
            at provided url.'''
        req = urllib.request.urlopen(url)
        return int(req.headers.get('content-length'))

    def http_get_remote_filesize(self, url):
        '''Checks and returns integer 'Content-Length' header sent from remote url.''' 
        req = urllib.request.urlopen(url)
        return int(req.headers['Content-Length'])

    def mirror(self, url, filepath, post_args=None, expected_filetype=None):
        '''Downloads specified url into specified filepath, doing a Content-Length
        comparison of remote and local files to avoid re-downloading identical 
        files.

        url protocol may be FTP or HTTP.

        If post_args is set and protocol is HTTP, uses POST method rather than GET,
        HOWEVER -- WARNING -- no filesize comparison can be done, only a check to 
        see whether the target filepath already exists.

        Args:
            url (str): url to mirror (HTTP or FTP)
            filepath (str): path to place new/updated file
            post_args (dict): if set, switches to POST method [default: None]
            expected_filetype (str): optional (currently only 'pdf' supported)

        Returns:
            DownloadResult object
        '''

        protocol = urllib.parse.urlparse(url).scheme
        method = 'GET' if not post_args else 'POST'

        # if file isn't there, filesize will be None. 
        local_filesize = get_filesize(filepath)

        # only do the more complex "mirror" operation if local_filesize > 0
        if local_filesize and method=='GET':

            remote_filesize = self.ftp_get_remote_filesize(url) if protocol=='ftp' else self.http_get_remote_filesize(url)

            log.debug('[MIRROR] %s: Content-Length = %i, %s: Filesize = %i', url, 
                        remote_filesize, filepath, local_filesize)
        
            if remote_filesize == local_filesize:
                log.info('[MIRROR] %s: Not downloading since local file %s is identical', url, filepath)
                return DownloadResult(url=url, status_code=200, source='filesystem', filepath=filepath)
            else:
                log.info('[MIRROR] %s: Starting download since local file %s needs an update.', url, filepath)

        # Should we avoid redownloading via POST if we already have the file?
        # Commented out Nov 14, 2015 --nthmost
        #elif os.path.exists(filepath) and method=='POST':
        #    log.info('[MIRROR] %s: Not downloading since local file exists and HTTP method is POST.', url, filepath)
        #    return DownloadResult(url=url, status_code=200, source='filesystem', filepath=filepath, 
        #            method='POST', params=post_args)

        else:
            log.info('[MIRROR] %s: Starting download since no copy exists at %s.', url, filepath)

        if protocol=='ftp':
            log.debug('[MIRROR] %s: downloading via FTP')
            return self.ftp(url, filepath)
        else:
            log.debug('[MIRROR] %s: downloading via HTTP')
            return self.request_write_file(url, filepath, post_args=post_args, 
                                           expected_filetype=expected_filetype)

