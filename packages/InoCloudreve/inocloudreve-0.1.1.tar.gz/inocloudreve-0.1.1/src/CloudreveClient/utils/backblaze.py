import httpx
import aiobotocore.session

import aiobotocore.session

async def b2_list_folders(
    self,
    prefix: str = "",
    delimiter: str = "/",
    access_key_id: str | None = None,
    access_key_secret: str | None = None,
    region: str | None = None,
    bucket_name: str | None = None,
) -> dict:
    """
    List “folders” (common prefixes) in a Backblaze B2 bucket using the S3-compatible API.

    Args:
        self: CloudreveClient instance
        prefix: key prefix to list under (e.g. "" for root)
        delimiter: character to group keys by ("/" for folder behavior)
        access_key_id: your b2 access id
        access_key_secret: your b2 access secret
        region: B2 bucket region (defaults to self.b2_region)
        bucket_name: B2 bucket name (defaults to self.b2_bucket_name)

    Returns:
        {
            "success": bool,
            "status_code": int | None,
            "msg": str,
            "folders": list[str]
        }
    """
    if access_key_id is None:
        access_key_id = self.b2_access_key_id

    if access_key_secret is None:
        access_key_secret = self.b2_access_key_secret

    if region is None:
        region = self.b2_region

    if bucket_name is None:
        bucket_name = self.b2_bucket_name

    endpoint_url = f"https://s3.{region}.backblazeb2.com"

    session = aiobotocore.session.get_session()
    async with session.create_client(
        "s3",
        region_name=region,
        endpoint_url=endpoint_url,
        aws_access_key_id=access_key_id,
        aws_secret_access_key=access_key_secret,
    ) as s3:
        try:
            response = await s3.list_objects_v2(
                Bucket=bucket_name,
                Prefix=prefix,
                Delimiter=delimiter
            )
            # Extract folder prefixes
            common = response.get("CommonPrefixes", [])
            folders = [entry["Prefix"] for entry in common]
            return {
                "success": True,
                "status_code": 200,
                "msg": "",
                "folders": folders
            }
        except Exception as exc:
            return {
                "success": False,
                "status_code": None,
                "msg": f"Error listing folders: {exc}",
                "folders": []
            }

async def b2_list_multipart_uploads(
    self,
    prefix: str | None = None,
    access_key_id: str | None = None,
    access_key_secret: str | None = None,
    region: str | None = None,
    bucket_name: str | None = None,
) -> dict:
    """
    List active multipart uploads in your B2 bucket.

    Args:
      self: CloudreveClient instance
      prefix: only list uploads whose key starts with this (optional)
      access_key_id: your b2 access id
      access_key_secret: your b2 access secret
      region: B2 region (uses self.b2_region if None)
      bucket_name: B2 bucket name (uses self.b2_bucket_name if None)

    Returns:
      {
        "success": bool,
        "status_code": int | None,
        "msg": str,
        "uploads": [  # list of dicts with UploadId, Key, Initiator, etc.
          {
            "UploadId": str,
            "Key": str,
            "Initiated": datetime,
            ...
          }, …
        ]
      }
    """
    if access_key_id is None:
        access_key_id = self.b2_access_key_id

    if access_key_secret is None:
        access_key_secret = self.b2_access_key_secret

    if region is None:
        region = self.b2_region

    if bucket_name is None:
        bucket_name = self.b2_bucket_name

    endpoint    = f"https://s3.{region}.backblazeb2.com"

    session     = aiobotocore.session.get_session()

    async with session.create_client(
        "s3",
        region_name=region,
        endpoint_url=endpoint,
        aws_access_key_id=access_key_id,
        aws_secret_access_key=access_key_secret,
    ) as s3:
        try:
            resp = await s3.list_multipart_uploads(
                Bucket=bucket_name,
                Prefix=prefix or ""
            )
            uploads = resp.get("Uploads", [])
            return {
                "success": True,
                "status_code": 200,
                "msg": "",
                "uploads": uploads
            }
        except Exception as exc:
            return {
                "success": False,
                "status_code": None,
                "msg": f"Error listing multipart uploads: {exc}",
                "uploads": []
            }



async def b2_upload_part(
    self,
    object_key: str,
    upload_id: str,
    part_number: int,
    part_data: bytes,
    access_key_id: str | None = None,
    access_key_secret: str | None = None,
    region: str | None = None,
    bucket_name: str | None = None,
) -> dict:
    """
    Upload one part of a multipart upload to Backblaze B2 via the S3-compatible API.

    Args:
        self: CloudreveClient instance
        object_key: the object’s key/path in the bucket (e.g. "Spark/test/test36.zip")
        upload_id: the multipart UploadId from create_upload_session
        part_number: which part index this is (starting at 0 or 1, per your B2 config)
        part_data: the raw bytes of this part
        access_key_id: your b2 access id
        access_key_secret: your b2 access secret
        region: your B2 bucket’s region (e.g. "us-west-001")
        bucket_name: the name of your B2 bucket

    Returns:
        {
            "success": bool,
            "status_code": int | None,
            "msg": str
        }
    """
    if access_key_id is None:
        access_key_id = self.b2_access_key_id

    if access_key_secret is None:
        access_key_secret = self.b2_access_key_secret

    if region is None:
        region = self.b2_region

    if bucket_name is None:
        bucket_name = self.b2_bucket_name

    session = aiobotocore.session.get_session()

    url = f'https://s3.{region}.backblazeb2.com'

    async with session.create_client(
            's3',
            region_name=region,
            endpoint_url=url,
            aws_access_key_id=access_key_id,
            aws_secret_access_key=access_key_secret,
    ) as s3:
        try:
            await s3.upload_part(
                Bucket=bucket_name,
                Key=object_key,
                UploadId=upload_id,
                PartNumber=part_number,
                Body=part_data
            )
            return {"success": True, "status_code": 200, "msg": f"Part {part_number} uploaded"}
        except Exception as e:
            return {"success": False, "status_code": None, "msg": str(e)}
