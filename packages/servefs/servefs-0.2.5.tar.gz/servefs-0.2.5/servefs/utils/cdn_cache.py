import hashlib
import os
import urllib.parse
from pathlib import Path
from typing import Optional, Tuple

import aiofiles
import aiohttp
from fastapi import Request
from fastapi.responses import Response


class CDNCacheManager:
    """Manager for caching CDN resources locally"""
    
    def __init__(self, cache_dir: Optional[Path] = None):
        self.cache_dir = cache_dir or Path("static/cdn_cache")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Supported CDN domains
        self.supported_domains = {
            "unpkg.com",
            "cdnjs.cloudflare.com"
        }
    
    def _get_cache_path(self, url: str) -> Path:
        """Generate cache file path from URL"""
        # Create a safe filename from URL
        url_hash = hashlib.md5(url.encode()).hexdigest()
        parsed = urllib.parse.urlparse(url)
        
        # Extract file extension
        path_parts = Path(parsed.path).parts
        filename = path_parts[-1] if path_parts else "index"
        
        # Get extension
        ext = Path(filename).suffix or ".js"  # Default to .js for JS libraries
        
        return self.cache_dir / f"{url_hash}{ext}"
    
    def is_supported_url(self, url: str) -> bool:
        """Check if URL is from a supported CDN"""
        try:
            parsed = urllib.parse.urlparse(url)
            domain = parsed.netloc.lower()
            
            # Remove 'www.' prefix if present
            if domain.startswith('www.'):
                domain = domain[4:]
                
            return domain in self.supported_domains
        except Exception:
            return False
    
    async def get_cached_file(self, url: str) -> Optional[Path]:
        """Get cached file if it exists"""
        cache_path = self._get_cache_path(url)
        return cache_path if cache_path.exists() else None
    
    async def cache_resource(self, url: str) -> Tuple[bool, Optional[str]]:
        """Download and cache a resource from CDN
        
        Returns:
            Tuple[bool, Optional[str]]: (success, error_message)
        """
        try:
            cache_path = self._get_cache_path(url)
            # Skip if already cached
            if cache_path.exists():
                return True, None
            
            # Download the resource
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        content = await response.read()
                        # Write to cache
                        async with aiofiles.open(cache_path, 'wb') as f:
                            await f.write(content)
                        
                        return True, None
                    else:
                        return False, f"HTTP {response.status}"
        
        except Exception as e:
            return False, str(e)
    
    async def serve_cached_resource(self, url: str, request: Request) -> Optional[Response]:
        """Serve a cached resource or cache it first"""
        if not self.is_supported_url(url):
            return None
        
        # Check if cached
        cached_file = await self.get_cached_file(url)
        
        if not cached_file:
            # Try to cache it
            success, error = await self.cache_resource(url)
            if not success:
                return None
            cached_file = await self.get_cached_file(url)
        
        if cached_file and cached_file.exists():
            # Determine content type
            content_type = self._get_content_type(url)
            
            # Read and serve the file
            async with aiofiles.open(cached_file, 'rb') as f:
                content = await f.read()
            
            return Response(
                content=content,
                media_type=content_type,
                headers={
                    "Cache-Control": "public, max-age=31536000",  # 1 year cache
                    "Access-Control-Allow-Origin": "*",
                }
            )
        
        return None
    
    def _get_content_type(self, url: str) -> str:
        """Determine content type from URL"""
        parsed = urllib.parse.urlparse(url)
        path = parsed.path.lower()
        
        if path.endswith('.js'):
            return "application/javascript"
        elif path.endswith('.css'):
            return "text/css"
        elif path.endswith('.woff') or path.endswith('.woff2'):
            return "font/woff2"
        elif path.endswith('.ttf'):
            return "font/ttf"
        elif path.endswith('.svg'):
            return "image/svg+xml"
        else:
            return "application/octet-stream"
