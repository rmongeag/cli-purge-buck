#!/usr/bin/env python
import requests
from akamai.edgegrid import EdgeGridAuth,EdgeRc
from urllib.parse import urljoin
import json
import sys
from os.path import expanduser
import time
from itertools import islice
import argparse
import logging
from datetime import datetime


class buck_purge(object):

    print (sys.argv[0])
    def __init__(self):
        parser = argparse.ArgumentParser(
            description='Purge or invalidate 50 URLs per request.',
            usage='''akamai buck_purge <command> [<args>]

The commands that can be executed are:
    delete     delete the content from cache
    invalidate      invalidate the content from cache
''')
        parser.add_argument('command', help='Subcommand to run')
        # parse_args defaults to [1:] for args, but you need to
        # exclude the rest of the args too, or validation will fail
        args = parser.parse_args(sys.argv[1:2])
        if not hasattr(self, args.command):
            print ('Unrecognized command')
            parser.print_help()
            exit(1)
        # use dispatch pattern to invoke method with same name
        getattr(self, args.command)()

    def invalidate(self):
        parser = argparse.ArgumentParser(
            description='Invalidate urls from cache in the file provided.')
        # prefixing the argument with -- means it's optional
        parser.add_argument('urls', action='store', help='File name with the urls to purge')
        # now that we're inside a subcommand, ignore the first
        # TWO argvs, ie the command (git) and the subcommand (commit)
        args = parser.parse_args(sys.argv[2:])
        print ('Running invalidate, urls=%s' % args.urls)

    def delete(self):
        parser = argparse.ArgumentParser(
            description='delete urls from cache in the file provided.')
        # NOT prefixing the argument with -- means it's not optional
        parser.add_argument('urls', action='store', help='File name with the urls to purge')
        args = parser.parse_args(sys.argv[2:])
        print ('Running purge, urls=%s' % args.urls)
        

### Adding Logging ###
logger = logging.getLogger('purge-list')
hdlr = logging.FileHandler('./' + datetime.now().strftime('purge_%H_%M_%d_%m_%Y.log'))
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
hdlr.setFormatter(formatter)
logger.setLevel(logging.INFO)


def get_base_url(egsection):
    try:
        homedir = expanduser("~")
        edgerc = EdgeRc(homedir + "/.edgerc")
        section = egsection
        baseurl = 'https://%s' % edgerc.get(section, 'host')
        s = requests.Session()
        s.auth = EdgeGridAuth.from_edgerc(edgerc, section)
    except Exception as inst:
        logger.error(str(inst))
        print (inst)
        exit(1)
    return baseurl, s

####API Calls####
def purge_url(s, burl, purgeurl, netwrk, action):
    try:
        headers = {'content-type': 'application/json'}
        data = {'objects': purgeurl}

        response = s.post(urljoin(burl, '/ccu/v3/' + action + '/url/' + netwrk), data=json.dumps(data), headers=headers)
        print ('\nURLs to purge:')
        print (purgeurl)
        print ('\nResponse:')
        print (response)
        print ('\n')

        logger.info('Purged urls:')
        logger.info(purgeurl)
        logger.info('\n')

        logger.info('Response from the API:')
        logger.info(response.text)
        logger.info('\n')

        response = json.loads(response.text)
        
    except Exception as inst:
        errorm = str(inst) + ' error while attempting call on ' + str (purgeurl)  
        logger.error(errorm)

    return response
    
#def do_purge(cmdargs):

    
#    parser = argparse.ArgumentParser(description='Purge or invalidate 50 URLs per request.')
    
#    parser.add_argument('--section', action='store', required=True, help='.edgerc file section')
#    parser.add_argument('--urls', action='store', required=True, help='File with the urls to purge')
#    parser.add_argument('--network', action='store', required=True, help='Network to execute the purge/invalidate action.')
#    parser.add_argument('--action', action='store', required=True, help='Action to excecute Delete or Invalidate')
    
#   try:
#        args = parser.parse_args(cmdargs)
#        logger.addHandler(hdlr) 
#    except SystemExit:
#        return
    
#    burl, nsession = get_base_url(args.section)
    
#    with open(args.urls) as myfile:
#        line= [x.strip() for x in islice(myfile, 50)]

#        while line:
#            time.sleep(1)
#            if (line !=[]):
#                purge_url(nsession, burl, line, args.network, args.action)
#            line= [x.strip() for x in islice(myfile, 50)]
            
def main():
    buck_purge()
    #do_purge(sys.argv[1:])
    
if __name__ == "__main__":
    main()
    #buck_purge()
