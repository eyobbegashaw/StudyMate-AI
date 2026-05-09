import requests
import logging
from packaging import version

logger = logging.getLogger(__name__)

class UpdateChecker:
    def __init__(self, repo_owner="yourusername", repo_name="studyai"):
        self.repo_owner = repo_owner
        self.repo_name = repo_name
        self.github_api_url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/releases/latest"
        self.current_version = "1.0.0"
        self.enabled = repo_owner != "yourusername"  # Disable if not configured
    
    def check_for_updates(self):
        """Check GitHub for newer version."""
        if not self.enabled:
            return {"update_available": False, "message": "Update checking disabled (not configured)"}
        
        try:
            response = requests.get(self.github_api_url, timeout=5)
            if response.status_code == 200:
                release_data = response.json()
                latest_version = release_data.get("tag_name", "").lstrip("v")
                
                if not latest_version:
                    return {"update_available": False, "message": "No version found"}
                
                if self._is_newer_version(latest_version):
                    return {
                        "update_available": True,
                        "current_version": self.current_version,
                        "latest_version": latest_version,
                        "release_name": release_data.get("name", ""),
                        "release_notes": release_data.get("body", ""),
                        "download_url": self._get_download_url(release_data),
                        "html_url": release_data.get("html_url", "")
                    }
                else:
                    return {
                        "update_available": False,
                        "current_version": self.current_version,
                        "latest_version": latest_version,
                        "message": "You have the latest version"
                    }
            else:
                return {"update_available": False, "error": f"GitHub API error: {response.status_code}"}
        except requests.Timeout:
            logger.warning("Update check timed out")
            return {"update_available": False, "error": "Request timed out"}
        except Exception as e:
            logger.error(f"Error checking for updates: {e}")
            return {"update_available": False, "error": str(e)}
    
    def _is_newer_version(self, latest):
        """Compare versions."""
        try:
            return version.parse(latest) > version.parse(self.current_version)
        except Exception:
            return False
    
    def _get_download_url(self, release_data):
        """Get the best download URL for the platform."""
        assets = release_data.get("assets", [])
        import platform
        system = platform.system().lower()
        
        for asset in assets:
            name = asset.get("name", "").lower()
            if system == "windows" and (".exe" in name or ".msi" in name):
                return asset.get("browser_download_url")
            elif system == "darwin" and (".dmg" in name or ".pkg" in name):
                return asset.get("browser_download_url")
            elif system == "linux" and (".appimage" in name or ".deb" in name or ".tar.gz" in name):
                return asset.get("browser_download_url")
        
        return release_data.get("html_url", "")
    
    def set_repo(self, owner, repo):
        """Update repository information."""
        self.repo_owner = owner
        self.repo_name = repo
        self.github_api_url = f"https://api.github.com/repos/{owner}/{repo}/releases/latest"
        self.enabled = True
