"""Git-based source provider for remote guideline repositories."""

import os
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Optional, AsyncIterator
from datetime import datetime
import asyncio

from .base import SourceProvider
from ..models.types import ArchitectureGuideline
from ..config.models import AuthType
from ..storage.filesystem import FileSystemStorage


class GitSourceProvider(SourceProvider):
    """Source provider for Git repositories containing guidelines."""
    
    def __init__(self, config):
        """Initialize Git source provider."""
        super().__init__(config)
        
        # Create cache directory for cloned repos
        self.cache_dir = Path.home() / ".archguide" / "cache" / "git"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Local path where the repo will be cloned
        repo_name = self._sanitize_repo_name(config.url or config.name)
        self.local_path = self.cache_dir / repo_name
        
        # Set up storage for the cloned repo
        self.storage = None
        self._repo_cloned = False
    
    def _sanitize_repo_name(self, url: str) -> str:
        """Convert repository URL to a safe directory name."""
        # Remove protocol and replace special chars
        clean_name = url.replace('https://', '').replace('http://', '').replace('git@', '')
        clean_name = clean_name.replace('/', '_').replace(':', '_').replace('.', '_')
        return clean_name
    
    async def connect(self) -> bool:
        """Connect to the Git repository and verify access."""
        try:
            # Test if we can access the repository
            if not await self._test_git_access():
                return False
            
            # Clone or update the repository
            if not await self._ensure_repo_cloned():
                return False
            
            # Initialize storage for the cloned repo
            self.storage = FileSystemStorage(str(self.local_path))
            self._repo_cloned = True
            
            return True
            
        except Exception as e:
            self.metadata.error = f"Git connection error: {str(e)}"
            return False
    
    async def _test_git_access(self) -> bool:
        """Test if we can access the Git repository."""
        try:
            cmd = ["git", "ls-remote", "--heads", self.config.url]
            
            # Add authentication if configured
            env = os.environ.copy()
            if self.config.auth:
                env = self._setup_git_auth(env)
            
            # Run in a subprocess with timeout
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                env=env
            )
            
            stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=30)
            
            if process.returncode != 0:
                self.metadata.error = f"Git access failed: {stderr.decode()}"
                return False
            
            return True
            
        except asyncio.TimeoutError:
            self.metadata.error = "Git access timeout"
            return False
        except Exception as e:
            self.metadata.error = f"Git access error: {str(e)}"
            return False
    
    def _setup_git_auth(self, env: dict) -> dict:
        """Set up Git authentication based on configuration."""
        auth = self.config.auth
        
        if auth.type == AuthType.TOKEN:
            # For GitHub/GitLab personal access tokens
            if auth.token:
                env['GIT_ASKPASS'] = 'echo'
                env['GIT_USERNAME'] = auth.token
                env['GIT_PASSWORD'] = ''
        
        elif auth.type == AuthType.BASIC:
            if auth.username and auth.password:
                env['GIT_ASKPASS'] = 'echo'
                env['GIT_USERNAME'] = auth.username
                env['GIT_PASSWORD'] = auth.password
        
        elif auth.type == AuthType.SSH:
            if auth.ssh_key_path:
                env['GIT_SSH_COMMAND'] = f'ssh -i {auth.ssh_key_path} -o StrictHostKeyChecking=no'
        
        return env
    
    async def _ensure_repo_cloned(self) -> bool:
        """Ensure the repository is cloned and up to date."""
        try:
            env = os.environ.copy()
            if self.config.auth:
                env = self._setup_git_auth(env)
            
            if self.local_path.exists():
                # Repository exists, pull latest changes
                return await self._pull_changes(env)
            else:
                # Clone the repository
                return await self._clone_repo(env)
                
        except Exception as e:
            self.metadata.error = f"Repository sync error: {str(e)}"
            return False
    
    async def _clone_repo(self, env: dict) -> bool:
        """Clone the Git repository."""
        try:
            cmd = ["git", "clone"]
            
            # Add branch/tag if specified  
            if self.config.tag:
                cmd.extend(["--branch", self.config.tag])
            elif self.config.branch:
                cmd.extend(["--branch", self.config.branch])
            
            cmd.extend([self.config.url, str(self.local_path)])
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                env=env
            )
            
            stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=300)
            
            if process.returncode != 0:
                self.metadata.error = f"Git clone failed: {stderr.decode()}"
                return False
            
            # Store version info
            await self._update_version_info()
            
            return True
            
        except asyncio.TimeoutError:
            self.metadata.error = "Git clone timeout"
            return False
        except Exception as e:
            self.metadata.error = f"Git clone error: {str(e)}"
            return False
    
    async def _pull_changes(self, env: dict) -> bool:
        """Pull latest changes from the repository."""
        try:
            # Change to repo directory and pull
            cmd = ["git", "-C", str(self.local_path), "pull", "origin"]
            
            if self.config.tag:
                # For tags, we need to fetch and checkout
                fetch_cmd = ["git", "-C", str(self.local_path), "fetch", "--tags"]
                checkout_cmd = ["git", "-C", str(self.local_path), "checkout", self.config.tag]
                
                # Fetch tags
                process = await asyncio.create_subprocess_exec(
                    *fetch_cmd, env=env, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
                )
                await process.communicate()
                
                # Checkout tag
                process = await asyncio.create_subprocess_exec(
                    *checkout_cmd, env=env, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
                )
                stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=60)
                
            else:
                branch = self.config.branch or "main"
                cmd.append(branch)
                
                process = await asyncio.create_subprocess_exec(
                    *cmd,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                    env=env
                )
                
                stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=60)
            
            if process.returncode != 0:
                self.metadata.error = f"Git pull failed: {stderr.decode()}"
                return False
            
            # Update version info
            await self._update_version_info()
            
            return True
            
        except asyncio.TimeoutError:
            self.metadata.error = "Git pull timeout"
            return False
        except Exception as e:
            self.metadata.error = f"Git pull error: {str(e)}"
            return False
    
    async def _update_version_info(self):
        """Update version information from Git."""
        try:
            # Get current commit hash
            cmd = ["git", "-C", str(self.local_path), "rev-parse", "HEAD"]
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                self.metadata.version = stdout.decode().strip()[:8]  # Short hash
            
        except Exception:
            # Not critical if this fails
            pass
    
    async def fetch_guidelines(self) -> AsyncIterator[ArchitectureGuideline]:
        """Fetch guidelines from the cloned Git repository."""
        if not self._repo_cloned:
            if not await self.connect():
                return
        
        try:
            # Load guidelines using filesystem storage
            guidelines = self.storage.load_all_guidelines()
            
            for guideline in guidelines:
                yield guideline
                
        except Exception as e:
            self.metadata.error = f"Error loading guidelines from Git repo: {str(e)}"
            raise
    
    async def get_guideline(self, guideline_id: str) -> Optional[ArchitectureGuideline]:
        """Get a specific guideline by ID."""
        if not self._initialized:
            await self.sync()
        
        return self._guidelines_cache.get(guideline_id)
    
    async def force_refresh(self) -> bool:
        """Force refresh by cleaning local repo and re-cloning."""
        try:
            if self.local_path.exists():
                shutil.rmtree(self.local_path)
            
            self._repo_cloned = False
            self.storage = None
            
            return await self.connect()
            
        except Exception as e:
            self.metadata.error = f"Force refresh error: {str(e)}"
            return False
    
    async def close(self):
        """Clean up resources."""
        # Optionally clean up cloned repository
        # For now, we keep it cached for performance
        pass
    
    def __repr__(self) -> str:
        """String representation."""
        return f"GitSourceProvider(url='{self.config.url}', branch='{self.config.branch}', guidelines={self.metadata.total_guidelines})"