#!/usr/bin/env python3
"""
Test script for presigned URL file upload functionality
"""
import requests
import os
import mimetypes
from pathlib import Path

# Configuration
API_BASE_URL = "http://localhost:8000"  # Adjust if your API runs on different host/port
FILE_PATH = "/Users/minki/Downloads/OneDrive_2025-08-24"
LOGIN_EMAIL = "your_email@example.com"  # Replace with your test user email
LOGIN_PASSWORD = "your_password"        # Replace with your test user password

def login_and_get_token():
    """Login and get access token"""
    login_url = f"{API_BASE_URL}/auth/login"
    login_data = {
        "email": LOGIN_EMAIL,
        "password": LOGIN_PASSWORD
    }
    
    print("🔐 Logging in...")
    response = requests.post(login_url, json=login_data)
    
    if response.status_code != 200:
        print(f"❌ Login failed: {response.status_code} - {response.text}")
        return None
    
    token_data = response.json()
    access_token = token_data.get("access_token")
    print("✅ Login successful!")
    return access_token

def get_presigned_upload_url(access_token, file_path):
    """Get presigned upload URL from API"""
    file_path = Path(file_path)
    
    # Determine content type
    content_type, _ = mimetypes.guess_type(str(file_path))
    if not content_type:
        content_type = "application/octet-stream"
    
    # Get file size
    file_size = file_path.stat().st_size
    
    presigned_url = f"{API_BASE_URL}/files/upload/presigned"
    headers = {"Authorization": f"Bearer {access_token}"}
    data = {
        "filename": file_path.name,
        "content_type": content_type,
        "file_size": file_size
    }
    
    print(f"📋 Requesting presigned URL for: {file_path.name}")
    print(f"   Size: {file_size:,} bytes")
    print(f"   Content-Type: {content_type}")
    
    response = requests.post(presigned_url, json=data, headers=headers)
    
    if response.status_code != 200:
        print(f"❌ Failed to get presigned URL: {response.status_code} - {response.text}")
        return None
    
    result = response.json()
    print("✅ Got presigned upload URL!")
    print(f"   Expires at: {result.get('expires_at')}")
    print(f"   File ID: {result.get('file_id')}")
    
    return result

def upload_file_to_s3(upload_url, file_path, content_type):
    """Upload file directly to S3 using presigned URL"""
    print(f"⬆️  Uploading file to S3...")
    
    with open(file_path, 'rb') as file_data:
        headers = {
            "Content-Type": content_type,
            "Content-Disposition": f'attachment; filename="{Path(file_path).name}"'
        }
        
        response = requests.put(upload_url, data=file_data, headers=headers)
    
    if response.status_code in (200, 204):
        print("✅ File uploaded successfully to S3!")
        return True
    else:
        print(f"❌ S3 upload failed: {response.status_code} - {response.text}")
        return False

def check_file_status(access_token, file_id):
    """Check if file appears in the file list"""
    files_url = f"{API_BASE_URL}/files/"
    headers = {"Authorization": f"Bearer {access_token}"}
    
    print("📂 Checking file list...")
    response = requests.get(files_url, headers=headers)
    
    if response.status_code != 200:
        print(f"❌ Failed to get file list: {response.status_code} - {response.text}")
        return
    
    files_data = response.json()
    files = files_data.get("files", [])
    
    # Look for our uploaded file
    uploaded_file = None
    for file_info in files:
        if file_info.get("id") == file_id:
            uploaded_file = file_info
            break
    
    if uploaded_file:
        print("✅ File found in database!")
        print(f"   Status: {uploaded_file.get('upload_status', 'unknown')}")
        print(f"   Upload date: {uploaded_file.get('upload_date')}")
        return uploaded_file
    else:
        print("⚠️  File not found in database yet (webhook may be processing)")
        return None

def main():
    """Main test function"""
    print("🚀 Starting presigned URL upload test")
    print("=" * 50)
    
    # Check if file exists
    if not os.path.exists(FILE_PATH):
        print(f"❌ File not found: {FILE_PATH}")
        return
    
    # Step 1: Login
    access_token = login_and_get_token()
    if not access_token:
        return
    
    # Step 2: Get presigned upload URL
    upload_info = get_presigned_upload_url(access_token, FILE_PATH)
    if not upload_info:
        return
    
    # Step 3: Upload to S3
    success = upload_file_to_s3(
        upload_info["upload_url"], 
        FILE_PATH, 
        mimetypes.guess_type(FILE_PATH)[0] or "application/octet-stream"
    )
    
    if not success:
        return
    
    # Step 4: Check file status
    file_info = check_file_status(access_token, upload_info["file_id"])
    
    print("=" * 50)
    if file_info:
        print("🎉 Upload test completed successfully!")
    else:
        print("⚠️  Upload completed but file not yet in database")
        print("   This is normal if S3 webhooks are not configured")

if __name__ == "__main__":
    # Update these credentials before running
    if LOGIN_EMAIL == "your_email@example.com":
        print("❌ Please update LOGIN_EMAIL and LOGIN_PASSWORD in the script")
        exit(1)
    
    main()