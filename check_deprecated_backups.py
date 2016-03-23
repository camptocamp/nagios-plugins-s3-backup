#!/usr/bin/env python

from datetime import datetime
import argparse
import boto3
import os
import sys
import time

class s3_deprecated:
    def __init__(self, args):

        self.__debug   = args.debug
        self.__profile = args.profile
        self.__region  = args.region
        self.__bucket  = args.bucket
        self.__filters = args.filters.split(',')

        session = boto3.session.Session(
                profile_name = self.__profile,
                region_name  = self.__region
                )

        self.__dirs = []
        self.__instances = []

        self.out_status = 0
        self.out_msg = 'S3 backups: no deprecated directory'

        self.__ec2_client = session.client('ec2')
        self.__s3_client  = session.client('s3')
        self.__get_instances()
        self.__get_dirs()
        self.__check()


    def __print(self, string, level=1):
        '''
        Simple "print" wrapper: sends to stdout if debug is > 0
        '''
        if level <= self.__debug:
            print string

    def __get_instances(self):
        '''
        Get all AWS instances
        '''
        self.__print('Getting instances')
        instances = self.__ec2_client.describe_instances()
        for reservation in instances['Reservations']:
            for instance in reservation['Instances']:
                self.__instances.append(instance['PrivateDnsName'])

    def __get_dirs(self):
        '''
        Get all directories in designated bucket
        '''
        self.__print('Getting all directories in %s' % self.__bucket)
        listing = self.__s3_client.list_objects(
                Bucket=self.__bucket,
                Delimiter='/',
                )
        for i in listing['CommonPrefixes']:
            if os.path.dirname(i['Prefix']) not in self.__filters:
                self.__dirs.append(os.path.dirname(i['Prefix']))

    def __check(self):
        '''
        Ensure no useless directory is present on the bucket
        '''
        deprecated = list(set(self.__dirs) - set(self.__instances))
        if (len(deprecated) != 0):
            self.__print('Found: %s' % ', '.join(deprecated))
            self.out_msg = 'Deprecated directories found'
            self.out_status = 2


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Check useless s3 directories')
    parser.add_argument('--debug',  '-d',   help='Set verbosity level', default=0, type=int)
    parser.add_argument('--profile', '-p', help='Pass AWS profile name', default='default')
    parser.add_argument('--region', '-r',   help='Set AWS region', default='eu-west-1')
    parser.add_argument('--bucket', '-b', help='Bucket name')
    parser.add_argument('--filters', '-F', help='Filter out directories; directory1,directory2,directory3,..', default='')

    args = parser.parse_args()

    worker = s3_deprecated(args)
    print worker.out_msg
    sys.exit(worker.out_status)
