# Copyright (C) 2022-Present Indoc Systems
#
# Licensed under the GNU AFFERO GENERAL PUBLIC LICENSE,
# Version 3.0 (the "License") available at https://www.gnu.org/licenses/agpl-3.0.en.html.
# You may not use this file except in compliance with the License.


import aioboto3
from botocore.client import Config

from common.object_storage_adaptor.base_client import BaseClient

_SIGNATURE_VERSTION = 's3v4'


async def get_boto3_admin_client(endpoint: str, access_key: str, secret_key: str, https: bool = False):

    mc = Boto3AdminClient(endpoint, access_key, secret_key, https)

    return mc


class Boto3AdminClient(BaseClient):
    """
    Summary:
        The object client for minio admin operation. The class is based on
        the admin credentials to make the operations including:
            - create bucket in minio
            - create IAM role in minio
    """

    def __init__(self, endpoint: str, access_key: str, secret_key: str, https: bool = False) -> None:
        """
        Parameter:
            - endpoint(string): the endpoint of minio(no http schema)
            - access_key(str): the access key of minio
            - secret_key(str): the secret key of minio
            - https(bool): the bool to indicate if it is https connection
        """
        client_name = 'Boto3AdminClient'
        super().__init__(client_name)

        http_prefix = 'https://' if https else 'http://'
        self.endpoint = http_prefix + endpoint
        self.access_key = access_key
        self.secret_key = secret_key

        self._config = Config(signature_version=_SIGNATURE_VERSTION)
        self._session = aioboto3.Session(aws_access_key_id=self.access_key, aws_secret_access_key=self.secret_key)

    async def create_bucket(self, bucket: str):
        """
        Summary:
            The function will create new bucket in minio. The name contraint is following:
            - Bucket names must be between 3 and 63 characters long.
            - Bucket names can consist only of lowercase letters, numbers, dots (.), and hyphens (-).
            - Bucket names must begin and end with a letter or number.
            - Bucket names must not be formatted as an IP address (for example, 192.168.5.4).
            - Bucket names can't begin with xn-- (for buckets created after February 2020).
            - Bucket names must be unique within a partition.
            - Buckets used with Amazon S3 Transfer Acceleration can't have dots (.)
                in their names. For more information about transfer acceleration,
                see Amazon S3 Transfer Acceleration.

        Parameter:
            - bucket(str): the unique bucket name

        return:
            - dict
        """

        async with self._session.client('s3', endpoint_url=self.endpoint, config=self._config) as s3:
            res = await s3.create_bucket(Bucket=bucket)

        return res

    async def delete_bucket(self, bucket: str):
        """
        Summary:
            the function will remove the bucket in the object storage

        Parameter:
            - bucket(str): the unique bucket name

        return:
            - dict
        """
        self.logger.info(f'Delete bucket {bucket}')

        async with self._session.client('s3', endpoint_url=self.endpoint, config=self._config) as s3:
            res = await s3.delete_bucket(Bucket=bucket)

        return res

    async def create_bucket_encryption(self, bucket: str, algorithm: str = 'AES256') -> dict:
        """
        Summary:
            The function will create the bucket encryption rule. The rule will using
            AES256 to make encrytion.

        Parameter:
            - bucket(str): the unique bucket name
            - algorithm(str): the algorithm by default is AES256. please refer to boto3
                documentation for other options:
                https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.Client.put_bucket_encryption

        return:
            - dict
        """
        self.logger.info('Create encryption for bucket: %s(Algorithm %s)', bucket, algorithm)

        async with self._session.client('s3', endpoint_url=self.endpoint, config=self._config) as s3:
            res = await s3.put_bucket_encryption(
                Bucket=bucket,
                ServerSideEncryptionConfiguration={
                    'Rules': [
                        {
                            'ApplyServerSideEncryptionByDefault': {
                                'SSEAlgorithm': algorithm,
                            },
                        },
                    ]
                },
            )

            return res

    async def set_bucket_versioning(self, bucket: str, status: str = 'Enabled') -> dict:
        """
        Summary:
            The function will set the bucket versioning based on input.

        Parameter:
            - bucket(str): the unique bucket name
            - status(str): the status of versioning

        return:
            - dict
        """
        self.logger.info('Set versioning for bucket: %s(Status %s)', bucket, status)

        async with self._session.client('s3', endpoint_url=self.endpoint, config=self._config) as s3:
            res = await s3.put_bucket_versioning(
                Bucket=bucket,
                VersioningConfiguration={
                    'MFADelete': 'Disabled',
                    'Status': status,
                },
            )

            return res
