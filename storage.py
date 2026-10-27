"""
The private bucket bound to this service (prefix MW_STORAGE_). Its files are
never public: each link is signed and expires.
"""
import os

import boto3
from botocore.config import Config

BUCKET = os.environ.get('MW_STORAGE_BUCKET', '')

_s3 = boto3.client(
    's3',
    endpoint_url=os.environ.get('MW_STORAGE_ENDPOINT') or None,
    region_name=os.environ.get('MW_STORAGE_REGION') or 'auto',
    aws_access_key_id=os.environ.get('MW_STORAGE_ACCESS_KEY_ID'),
    aws_secret_access_key=os.environ.get('MW_STORAGE_SECRET_ACCESS_KEY'),
    config=Config(
        signature_version='s3v4',
        s3={'addressing_style': 'path' if os.environ.get('MW_STORAGE_FORCE_PATH_STYLE') == 'true' else 'auto'},
    ),
)


def check() -> str:
    if not BUCKET:
        raise RuntimeError('MW_STORAGE_BUCKET is empty: connect a bucket to this service')
    _s3.head_bucket(Bucket=BUCKET)
    return BUCKET


def put(key: str, body: bytes, content_type: str) -> None:
    _s3.put_object(Bucket=BUCKET, Key=key, Body=body, ContentType=content_type)


def signed_link(key: str, name: str) -> str:
    """A link to download the file, good for 15 minutes."""
    return _s3.generate_presigned_url(
        'get_object',
        Params={'Bucket': BUCKET, 'Key': key, 'ResponseContentDisposition': f'attachment; filename="{name.replace(chr(34), "")}"'},
        ExpiresIn=900,
    )
