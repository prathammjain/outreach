import os
import json
import base64
from typing import List, Optional
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import logging

logger = logging.getLogger(__name__)

# Google Drive API scopes
SCOPES = ['https://www.googleapis.com/auth/drive']


class GoogleDriveService:
    """Service for managing Google Drive permissions."""
    
    def __init__(self, service_account_file: str):
        """
        Initialize Google Drive service with service account credentials.
        
        Supports two methods:
        1. File path (local development)
        2. Base64-encoded JSON from env var (production deployment)
        
        Args:
            service_account_file: Path to service account JSON file
        """
        # Check if Base64-encoded credentials are in environment
        base64_creds = os.getenv('GOOGLE_SERVICE_ACCOUNT_JSON_BASE64')
        
        if base64_creds:
            # Decode Base64 credentials (for production deployment)
            logger.info("Using Base64-encoded service account credentials from environment")
            try:
                json_content = base64.b64decode(base64_creds)
                credentials_info = json.loads(json_content)
                self.credentials = service_account.Credentials.from_service_account_info(
                    credentials_info,
                    scopes=SCOPES
                )
            except Exception as e:
                logger.error(f"Failed to decode Base64 credentials: {e}")
                raise
        else:
            # Use file path (for local development)
            logger.info(f"Using service account file: {service_account_file}")
            self.credentials = service_account.Credentials.from_service_account_file(
                service_account_file,
                scopes=SCOPES
            )
        
        self.service = build('drive', 'v3', credentials=self.credentials)
    
    def grant_access(self, file_id: str, email: str) -> Optional[str]:
        """
        Grant viewer access to a Google Sheet for a specific email.
        
        Args:
            file_id: Google Sheet ID
            email: User's email address
            
        Returns:
            Permission ID if successful, None otherwise
        """
        try:
            permission = {
                'type': 'user',
                'role': 'reader',  # viewer access
                'emailAddress': email
            }
            
            result = self.service.permissions().create(
                fileId=file_id,
                body=permission,
                sendNotificationEmail=True,  # Google sends native access email
                emailMessage=f'You now have access to this resource. Please log in with {email} to view.'
            ).execute()
            
            permission_id = result.get('id')
            logger.info(f"Granted access to {email} for file {file_id}. Permission ID: {permission_id}")
            return permission_id
            
        except HttpError as error:
            logger.error(f"Failed to grant access to {email} for file {file_id}: {error}")
            return None
    
    def revoke_access(self, file_id: str, email: str) -> bool:
        """
        Revoke access to a Google Sheet for a specific email.
        
        Args:
            file_id: Google Sheet ID
            email: User's email address
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # First, find the permission ID for this email
            permissions = self.service.permissions().list(
                fileId=file_id,
                fields='permissions(id,emailAddress)'
            ).execute()
            
            permission_id = None
            for perm in permissions.get('permissions', []):
                if perm.get('emailAddress') == email:
                    permission_id = perm.get('id')
                    break
            
            if not permission_id:
                logger.warning(f"No permission found for {email} on file {file_id}")
                return False
            
            # Delete the permission
            self.service.permissions().delete(
                fileId=file_id,
                permissionId=permission_id
            ).execute()
            
            logger.info(f"Revoked access for {email} from file {file_id}")
            return True
            
        except HttpError as error:
            logger.error(f"Failed to revoke access for {email} from file {file_id}: {error}")
            return False
    
    def grant_multiple_access(self, file_ids: List[str], email: str) -> List[str]:
        """
        Grant access to multiple files for a user.
        
        Args:
            file_ids: List of Google Sheet IDs
            email: User's email address
            
        Returns:
            List of successfully granted file IDs
        """
        granted = []
        for file_id in file_ids:
            if self.grant_access(file_id, email):
                granted.append(file_id)
        return granted
