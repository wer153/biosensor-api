#!/usr/bin/env python3
"""
Quick test script - just provide your access token directly
"""

import httpx
import os
import mimetypes
from pathlib import Path

# Configuration
API_BASE_URL = "http://biosensor-alb-1554833055.ap-northeast-2.elb.amazonaws.com"
FILE_PATH = "/Users/minki/Downloads/OneDrive_2025-08-24/health_data_large.csv"

# Login credentials
LOGIN_EMAIL = "user@example.com"
LOGIN_PASSWORD = "string"


def login():
    """Login and get access token"""
    print("🔐 Logging in...")
    login_data = {"email": LOGIN_EMAIL, "password": LOGIN_PASSWORD}
    response = httpx.post(f"{API_BASE_URL}/auth/login", json=login_data)

    if response.status_code not in (200, 201):
        print(f"❌ Login failed: {response.status_code} - {response.text}")
        return None

    token_data = response.json()
    access_token = token_data.get("access_token")
    print("✅ Login successful!")
    return access_token


def main():
    # Login first
    access_token = login()
    if not access_token:
        return

    if not os.path.exists(FILE_PATH):
        print(f"❌ File not found: {FILE_PATH}")
        return

    file_path = Path(FILE_PATH)
    content_type, _ = mimetypes.guess_type(str(file_path))
    if not content_type:
        content_type = "application/octet-stream"

    file_size = file_path.stat().st_size

    print(f"📋 File: {file_path.name}")
    print(f"   Size: {file_size:,} bytes")
    print(f"   Type: {content_type}")

    # Get presigned URL
    headers = {"Authorization": f"Bearer {access_token}"}
    data = {"filename": file_path.name, "content_type": content_type}

    print("\n⬇️  Getting presigned URL...")
    response = httpx.post(
        f"{API_BASE_URL}/files/upload/presigned", json=data, headers=headers
    )

    if response.status_code not in (200, 201):
        print(f"❌ Failed: {response.status_code} - {response.text}")
        return

    result = response.json()
    print("✅ Got presigned URL!")
    print(f"   URL domain: {result['upload_url'][:80]}...")

    # Upload to S3
    print("⬆️  Uploading to S3...")
    upload_url = result["upload_url"]

    print(f"   Uploading {file_size:,} bytes to S3...")

    # Try upload with curl first (sometimes works better than httpx for S3)
    import subprocess
    import tempfile

    # Write curl command to a temp script
    curl_cmd = [
        "curl",
        "-X",
        "PUT",
        "-H",
        f"Content-Type: {content_type}",
        "-H",
        f'Content-Disposition: attachment; filename="{file_path.name}"',
        "--data-binary",
        f"@{file_path}",
        "--connect-timeout",
        "30",
        "--max-time",
        "300",
        "-w",
        "HTTP_STATUS:%{http_code}\\n",
        upload_url,
    ]

    try:
        result_curl = subprocess.run(
            curl_cmd, capture_output=True, text=True, timeout=300
        )
        print(f"   curl exit code: {result_curl.returncode}")
        print(f"   curl output: {result_curl.stdout}")
        if result_curl.stderr:
            print(f"   curl stderr: {result_curl.stderr}")

        # Check if curl succeeded
        if (
            "HTTP_STATUS:200" in result_curl.stdout
            or "HTTP_STATUS:204" in result_curl.stdout
        ):
            s3_success = True
            print("✅ Upload successful via curl!")
        else:
            s3_success = False
            print("❌ Upload failed via curl")

    except subprocess.TimeoutExpired:
        print("❌ Upload timeout with curl")
        s3_success = False

    if s3_success:
        print("✅ Upload successful!")
        print(f"File ID: {result['file_id']}")

        # Test download
        print("\n⬇️  Testing download...")
        download_response = httpx.get(
            f"{API_BASE_URL}/files/{result['file_id']}/download",
            headers=headers,
            timeout=30.0,
        )

        if download_response.status_code == 200:
            download_data = download_response.json()
            print("✅ Got download URL!")
            print(f"   Expires at: {download_data['expires_at']}")
            print(f"   Filename: {download_data['filename']}")

            # Test accessing the download URL with curl
            print("\n🌐 Testing download URL access...")
            download_curl_cmd = [
                "curl",
                "-I",  # HEAD request
                "--connect-timeout",
                "30",
                "--max-time",
                "60",
                "-w",
                "HTTP_STATUS:%{http_code}\\n",
                download_data["download_url"],
            ]

            try:
                download_result = subprocess.run(
                    download_curl_cmd, capture_output=True, text=True, timeout=60
                )
                print(f"   curl download test output: {download_result.stdout}")

                if "HTTP_STATUS:200" in download_result.stdout:
                    print("✅ Download URL is accessible!")
                    # Extract content-length from headers
                    for line in download_result.stdout.split("\n"):
                        if "content-length:" in line.lower():
                            print(f"   File size from S3: {line.split(':')[1].strip()}")
                            break
                else:
                    print(f"❌ Download URL failed via curl")
            except subprocess.TimeoutExpired:
                print("❌ Download URL test timeout")
        else:
            print(
                f"❌ Download failed: {download_response.status_code} - {download_response.text}"
            )

    else:
        print("❌ Upload failed")


if __name__ == "__main__":
    main()
