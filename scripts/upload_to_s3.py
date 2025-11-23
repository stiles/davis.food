#!/usr/bin/env python3
"""
Upload data files to S3 for public access.

Usage:
    python scripts/upload_to_s3.py
"""

import os
import json
from pathlib import Path
import boto3
from botocore.exceptions import ClientError

# S3 configuration
BUCKET_NAME = 'stilesdata.com'
S3_PREFIX = 'davis.food/'

# Files to upload
FILES_TO_UPLOAD = [
    'data/dashboard_stats.json',
    'data/davis_big_dawg/davis_big_dawg_reviews.json',
    'data/davis_big_dawg/davis_big_dawg_posts.json',
    'data/davis_big_dawg/transcripts/davis_big_dawg_transcripts.json'
]


def get_s3_client():
    """Create S3 client using environment credentials."""
    # Use MY_ prefixed environment variables
    aws_access_key = os.environ.get('MY_AWS_ACCESS_KEY_ID')
    aws_secret_key = os.environ.get('MY_AWS_SECRET_ACCESS_KEY')
    region = os.environ.get('MY_DEFAULT_REGION', 'us-east-1')
    
    if not aws_access_key or not aws_secret_key:
        raise ValueError("AWS credentials not found. Set MY_AWS_ACCESS_KEY_ID and MY_AWS_SECRET_ACCESS_KEY")
    
    return boto3.client(
        's3',
        aws_access_key_id=aws_access_key,
        aws_secret_access_key=aws_secret_key,
        region_name=region
    )


def upload_file_to_s3(s3_client, local_path: Path, s3_key: str):
    """
    Upload a file to S3 with public read access.
    
    Args:
        s3_client: boto3 S3 client
        local_path: Path to local file
        s3_key: S3 key (path in bucket)
    """
    try:
        print(f"Uploading {local_path} to s3://{BUCKET_NAME}/{s3_key}...")
        
        # Upload with proper content type and cache control
        extra_args = {
            'ContentType': 'application/json',
            'CacheControl': 'max-age=3600'
        }
        
        s3_client.upload_file(
            str(local_path),
            BUCKET_NAME,
            s3_key,
            ExtraArgs=extra_args
        )
        
        # Generate public URL
        url = f"https://{BUCKET_NAME}/{s3_key}"
        print(f"  ✓ Uploaded: {url}")
        return url
        
    except ClientError as e:
        print(f"  ✗ Error uploading {local_path}: {e}")
        return None


def main():
    """Upload all data files to S3."""
    print("=" * 80)
    print("Uploading davis.food data to S3")
    print("=" * 80)
    print()
    
    # Check if running from project root
    if not Path('data').exists():
        print("Error: Must run from project root directory")
        return 1
    
    # Create S3 client
    try:
        s3_client = get_s3_client()
    except ValueError as e:
        print(f"Error: {e}")
        return 1
    
    # Upload each file
    uploaded_urls = {}
    for file_path in FILES_TO_UPLOAD:
        local_path = Path(file_path)
        
        if not local_path.exists():
            print(f"Warning: {file_path} not found, skipping...")
            continue
        
        # Create S3 key preserving directory structure
        s3_key = S3_PREFIX + file_path
        url = upload_file_to_s3(s3_client, local_path, s3_key)
        
        if url:
            uploaded_urls[file_path] = url
    
    # Summary
    print()
    print("=" * 80)
    print(f"Upload complete! {len(uploaded_urls)} files uploaded.")
    print()
    print("Public URLs:")
    for file_path, url in uploaded_urls.items():
        print(f"  {file_path}")
        print(f"    → {url}")
    print("=" * 80)
    
    return 0


if __name__ == "__main__":
    exit(main())

