# Copyright (C) 2022-Present Indoc Systems
#
# Licensed under the GNU AFFERO GENERAL PUBLIC LICENSE,
# Version 3.0 (the "License") available at https://www.gnu.org/licenses/agpl-3.0.en.html.
# You may not use this file except in compliance with the License.


import hashlib

import httpx
from minio import Minio
from minio.helpers import url_replace
from minio.signer import sign_v4_s3

from common.object_storage_adaptor.base_client import BaseClient


class NotFoundError(Exception):
    pass


async def get_minio_policy_client(endpoint: str, access_key: str, secret_key: str, https: bool = False):

    mc = MinioPolicyClient(endpoint, access_key, secret_key, secure=https)

    return mc


class MinioPolicyClient(Minio):
    """
    Summary:
        The inherit class from minio. The main reason is that the python
        minio deosn't support the IAM policy create. And the boto3.s3 cannot
        fulfill the requirement as well.

        The ONLY way to create policy is to use the minio client binary.
        Keeping the binary in common package is not a good idea. Thus, We
        setup the logic by our own.
    """

    client_name = 'MinioPolicyClient'
    base_client = BaseClient(client_name)

    # the flag to turn on class-wide logs
    logger = base_client.logger
    debug_on = base_client.debug_on
    debug_off = base_client.debug_off

    async def create_IAM_policy(self, policy_name: str, content: str, region: str = 'us-east-1'):
        """
        Summary:
            The function will use create the IAM policy in minio server.
            for policy detail, please check the minio document:
            https://docs.min.io/minio/baremetal/security/minio-identity-management/policy-based-access-control.html

        Parameter:
            - policy_name(str): the policy name
            - content(str): the string content of policy
            - region(str): the region of service (default is us-east-1)

        return:
            - None
        """
        self.logger.info('Create policy: %s', policy_name)
        self.logger.info('Policy content: %s', content)

        # fetch the credential to generate headers
        creds = self._provider.retrieve() if self._provider else None

        # use native BaseURL class to follow the pattern
        params = {'name': policy_name}
        url = self._base_url.build('PUT', region, query_params=params)
        url = url_replace(url, path='/minio/admin/v3/add-canned-policy')

        headers = None
        headers, date = self._build_headers(url.netloc, headers, content, creds)
        # make the signiture of request
        content_hash = hashlib.sha256(content.encode()).hexdigest()
        headers = sign_v4_s3('PUT', url, region, headers, creds, content_hash, date)

        # sending to minio server to create IAM policy
        str_endpoint = url.scheme + '://' + url.netloc
        async with httpx.AsyncClient() as client:
            response = await client.put(
                str_endpoint + url.path,
                params=params,
                headers=headers,
                data=content,
            )

            if response.status_code != 200:
                error_msg = 'Fail to create minio policy:' + str(response.text)
                self.logger.error(error_msg)
                raise Exception(error_msg)

        return 'success'

    async def get_IAM_policy(self, policy_name: str, region: str = 'us-east-1'):
        """
        Summary:
            The function will use get the IAM policy in minio server.

        Parameter:
            - policy_name(str): the policy name to get
            - region(str): the region of service (default is us-east-1)

        return:
            - dict
        """
        self.logger.info('Get policy: %s', policy_name)

        # fetch the credential to generate headers
        creds = self._provider.retrieve() if self._provider else None

        # use native BaseURL class to follow the pattern
        params = {'name': policy_name, 'v': '2'}
        url = self._base_url.build('GET', region, query_params=params)
        url = url_replace(url, path='/minio/admin/v3/info-canned-policy')

        headers = None
        headers, date = self._build_headers(url.netloc, headers, '', creds)
        # make the signiture of request
        content_hash = hashlib.sha256(''.encode()).hexdigest()
        headers = sign_v4_s3('GET', url, region, headers, creds, content_hash, date)

        # sending to minio server to get IAM policy
        str_endpoint = url.scheme + '://' + url.netloc
        async with httpx.AsyncClient() as client:
            response = await client.get(
                str_endpoint + url.path,
                params=params,
                headers=headers,
            )

        if response.status_code == 404:
            error_msg = f'Policy {policy_name} does not exist'
            self.logger.error(error_msg)
            raise NotFoundError(error_msg)
        elif response.status_code != 200:
            error_msg = 'Fail to get minio policy:' + str(response.text)
            self.logger.error(error_msg)
            raise Exception(error_msg)

        return response.json()

    async def delete_IAM_policy(self, policy_name: str, region: str = 'us-east-1'):
        """
        Summary:
            The function will remove the IAM policy in minio server.

        Parameter:
            - policy_name(str): the policy name to get
            - region(str): the region of service (default is us-east-1)

        return:
            - string
        """
        self.logger.info('Remove policy: %s', policy_name)

        # fetch the credential to generate headers
        creds = self._provider.retrieve() if self._provider else None

        # use native BaseURL class to follow the pattern
        params = {'name': policy_name}
        url = self._base_url.build('DELETE', region, query_params=params)
        url = url_replace(url, path='/minio/admin/v3/remove-canned-policy')

        headers = None
        headers, date = self._build_headers(url.netloc, headers, '', creds)
        # make the signiture of request
        content_hash = hashlib.sha256(''.encode()).hexdigest()
        headers = sign_v4_s3('DELETE', url, region, headers, creds, content_hash, date)

        # sending to minio server to delete IAM policy
        str_endpoint = url.scheme + '://' + url.netloc
        async with httpx.AsyncClient() as client:
            response = await client.delete(
                str_endpoint + url.path,
                params=params,
                headers=headers,
            )

        if response.status_code == 404:
            error_msg = f'Policy {policy_name} does not exist'
            self.logger.error(error_msg)
            raise NotFoundError(error_msg)
        elif response.status_code != 200:
            error_msg = 'Fail to delete minio policy:' + str(response.text)
            self.logger.error(error_msg)
            raise Exception(error_msg)

        return response.text
