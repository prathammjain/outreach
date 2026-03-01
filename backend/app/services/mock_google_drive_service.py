import logging
from typing import List, Optional

logger = logging.getLogger(__name__)

class MockGoogleDriveService:
    """Mock service for testing Google Drive permissions locally."""
    
    def __init__(self, *args, **kwargs):
        logger.info("Initialized MOCK Google Drive Service for local testing")
    
    def grant_access(self, file_id: str, email: str) -> Optional[str]:
        logger.info(f"[MOCK] Granted access to {email} for file {file_id}. Permission ID: mock_perm_123")
        return "mock_perm_123"
    
    def revoke_access(self, file_id: str, email: str) -> bool:
        logger.info(f"[MOCK] Revoked access for {email} from file {file_id}")
        return True
    
    def grant_multiple_access(self, file_ids: List[str], email: str) -> List[str]:
        logger.info(f"[MOCK] Granted access to {email} for multiple files: {file_ids}")
        return file_ids
