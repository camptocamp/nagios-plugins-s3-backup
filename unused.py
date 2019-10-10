#!/usr/bin/env python

from datetime import datetime
from prometheus_client import start_http_server, Summary
from prometheus_client import Gauge
import argparse
import boto3
import sys
import time



class unused_stacks:
    def __init__(self, args):

        self.__debug   = args.debug
        self.__profile = args.profile
        self.__region  = args.region
        self.__clean   = args.clean

        session = boto3.session.Session(
                profile_name = self.__profile,
                region_name  = self.__region
                )

        self.__stacks = {}

        self.out_status = 0
        self.out_msg = 'CFN: no unused stack'

        self.__cfn_client = session.client('cloudformation')

        self.__get_stacks()
        if self.__clean:
            self.__clean_stacks()
        else:
            self.__check()


    def __print(self, string, level=1):
        '''
        Simple "print" wrapper: sends to stdout if debug is > 0
        '''
        if level <= self.__debug:
            print (string)

    def __get_stacks(self):
        '''
        Get all stacks
        '''
        self.__print('Getting cloudformation stacks')
        stacks = self.__cfn_client.list_stacks(
                StackStatusFilter=[
                    'CREATE_FAILED',
                    'ROLLBACK_FAILED',
                    'DELETE_FAILED',
                    'UPDATE_ROLLBACK_FAILED',
                    ],
                )
        for stack in stacks['StackSummaries']:
            self.__stacks[stack['StackName']] = {
                    'status': stack['StackStatus'],
                    'reason': stack['StackStatusReason'],
                    }

    def __check(self):
        '''
        Ensure no unused stack is present
        '''
        g = Gauge('unused_stacks', 'Count of unused cloud formation stacks')
        g.set(len(self.__stacks.keys()))
        if len(self.__stacks.keys()) > 0:
            self.out_msg = '%i stacks in a bad state' % len(self.__stacks.keys())
            self.out_status = 2
            self.__print('%s'% ",\n".join([ '%s %s %s'%(i, self.__stacks[i]['status'], self.__stacks[i]['reason']) for i in self.__stacks]))


    def __clean_stacks(self):
        '''
        Clean all stacks
        '''
        self.__print('Deleting stacks')
        for stack in self.__stacks.keys():
            self.__print('Deleting stack %s' % stack)
            self.__cfn_client.delete_stack(
                    StackName=stack
                    )

    REQUEST_TIME = Summary('request_processing_seconds', 'Time spent processing request')
    # Decorate function with metric.
    @REQUEST_TIME.time()
    def process_request(self, t):
        """A dummy function that takes some time."""
        time.sleep(t)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Check if there are opened security groups')
    parser.add_argument('--debug',  '-d',   help='Set verbosity level.', default=0, type=int)
    parser.add_argument('--profile', '-p', help='Pass AWS profile name.', default='default')
    parser.add_argument('--region', '-r',   help='Set AWS region.', default='eu-west-1')
    parser.add_argument('--clean',  help='Clean unused cloudformation stacks', action='store_const', const=True)
    parser.add_argument('--exporter',  help='run as prometheus exporter on default port 8080 ', action='store_const', const=True)
    parser.add_argument('--exporter_port',  help='if run as prometheus exporter on default port 8080, change port here ', default=8080, type=int)

    args = parser.parse_args()
    print (args.exporter)
    worker = unused_stacks(args)
    if args.exporter:
        print("exporter mode on port %i"% args.exporter_port)
        start_http_server(args.exporter_port)
        while True:
            worker.process_request(4)

    else:
        print (worker.out_msg)
        sys.exit(worker.out_status)
