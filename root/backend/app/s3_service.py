import boto3
import os
import uuid
from typing import List, Tuple
from app.schemas import PresignedUrlPart


class S3Service:
    def __init__(self):
        self.bucket_name = os.getenv("S3_BUCKET_NAME", "datavein-dev")
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
            endpoint_url=os.getenv("S3_ENDPOINT_URL")  # For MinIO
        )
    
    def generate_s3_key(self, user_id: uuid.UUID, upload_id: uuid.UUID, filename: str) -> str:
        return f"users/{user_id}/uploads/{upload_id}/{filename}"
    
    async def generate_presigned_upload_urls(
        self, 
        user_id: uuid.UUID, 
        upload_id: uuid.UUID, 
        filename: str, 
        file_size: int
    ) -> Tuple[str, List[PresignedUrlPart]]:
        s3_key = self.generate_s3_key(user_id, upload_id, filename)
        
        # Single part upload for all files up to 500MB
        # This avoids multipart upload complexity while supporting larger files
        url = self.s3_client.generate_presigned_url(
            'put_object',
            Params={'Bucket': self.bucket_name, 'Key': s3_key},
            ExpiresIn=3600  # 1 hour expiration
        )
        
        presigned_urls = [PresignedUrlPart(part_number=1, upload_url=url)]
        return s3_key, presigned_urls


# Global instance
s3_service = S3Service()
