import uuid
from typing import BinaryIO
from boto3 import client
from botocore.exceptions import ClientError, NoCredentialsError
from litestar.exceptions import InternalServerException

from app.config import settings


class S3Service:
    def __init__(self):
        self.bucket_name = settings.s3.bucket_name
        self.aws_region = settings.aws.region
        self.presigned_url_expiry = settings.s3.presigned_url_expiry

        try:
            self.s3_client = client(
                "s3",
                region_name=self.aws_region,
                aws_access_key_id=settings.aws.access_key_id,
                aws_secret_access_key=settings.aws.secret_access_key,
            )
        except NoCredentialsError:
            raise InternalServerException("AWS credentials not configured")

    def _generate_s3_key(self, user_id: str, original_filename: str) -> str:
        file_uuid = str(uuid.uuid4())
        file_extension = ""
        if "." in original_filename:
            file_extension = original_filename.rsplit(".", 1)[1]
            return f"users/{user_id}/{file_uuid}.{file_extension}"
        return f"users/{user_id}/{file_uuid}"

    async def upload_file(
        self,
        file_content: BinaryIO,
        user_id: str,
        original_filename: str,
        content_type: str,
    ) -> tuple[str, str]:
        s3_key = self._generate_s3_key(user_id, original_filename)

        try:
            self.s3_client.upload_fileobj(
                file_content,
                self.bucket_name,
                s3_key,
                ExtraArgs={
                    "ContentType": content_type,
                    "ServerSideEncryption": "AES256",
                },
            )
            return s3_key, self.bucket_name
        except ClientError as e:
            raise InternalServerException(f"Failed to upload file to S3: {str(e)}")

    def generate_presigned_url(self, s3_key: str, expires_in: int | None = None) -> str:
        if expires_in is None:
            expires_in = self.presigned_url_expiry

        try:
            url = self.s3_client.generate_presigned_url(
                "get_object",
                Params={"Bucket": self.bucket_name, "Key": s3_key},
                ExpiresIn=expires_in,
            )
            return url
        except ClientError as e:
            raise InternalServerException(f"Failed to generate presigned URL: {str(e)}")

    def delete_file(self, s3_key: str) -> bool:
        try:
            self.s3_client.delete_object(Bucket=self.bucket_name, Key=s3_key)
            return True
        except ClientError:
            return False


s3_service = S3Service()
