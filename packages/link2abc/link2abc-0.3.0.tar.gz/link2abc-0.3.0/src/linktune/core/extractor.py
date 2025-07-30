#!/usr/bin/env python3
"""
🔗 LinkTune Content Extractor
Universal content extraction from any web source

Simplified and cleaned version of the G.Music Assembly extractor system.
"""

import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from typing import Dict, Any, Optional
from dataclasses import dataclass
import re

@dataclass
class ExtractedContent:
    """Container for extracted content"""
    title: str
    content: str
    metadata: Dict[str, Any]
    success: bool
    error_message: Optional[str] = None
    platform: str = "unknown"
    url: str = ""

class ContentExtractor:
    """
    🔗 Universal content extractor for LinkTune
    
    Extracts meaningful content from any web URL for music generation.
    Supports ChatGPT shares, blogs, articles, and generic web content.
    
    Automatically uses the best available HTML parser:
    - lxml (fastest, requires installation)
    - html.parser (built-in Python, mobile-friendly)
    """
    
    def __init__(self, timeout: int = 10):
        self.timeout = timeout
        self.session = requests.Session()
        
        # Detect best available parser
        self.parser = self._detect_best_parser()
        
        # User agent to avoid blocking
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        # Advanced platform patterns with metadata extraction capabilities
        # Migrated from SharedSpark system for enhanced platform detection
        self.platform_patterns = {
            # AI Conversation Platforms (Priority 1)
            'chatgpt': {
                'patterns': [
                    r'chatgpt\.com/share/',
                    r'chat\.openai\.com/share/',
                    r'chatgpt\.com/c/',
                    r'chatgpt\.com',
                    r'chat\.openai\.com'
                ],
                'priority': 1,
                'metadata_extractors': [
                    r'/share/([a-zA-Z0-9-]+)',
                    r'/c/([a-zA-Z0-9-]+)'
                ]
            },
            'claude': {
                'patterns': [r'claude\.ai'],
                'priority': 1,
                'metadata_extractors': []
            },
            'poe': {
                'patterns': [
                    r'poe\.com/s/',
                    r'poe\.com/share/',
                    r'poe\.com'
                ],
                'priority': 1,
                'metadata_extractors': [
                    r'/s/([a-zA-Z0-9_-]+)',
                    r'/share/([a-zA-Z0-9_-]+)'
                ]
            },
            
            # Creative Platforms (Priority 1)
            'simplenote': {
                'patterns': [
                    r'app\.simplenote\.com/p/',
                    r'simplenote\.com/p/',
                    r'simplenote\.com'
                ],
                'priority': 1,
                'metadata_extractors': [r'/p/([a-zA-Z0-9]+)']
            },
            'vercel_creative': {
                'patterns': [
                    r'.*fractal-stone-writer.*\.vercel\.app/redstones/',
                    r'miadi\.vercel\.app/c/',
                    r'.*\.vercel\.app/redstones/',
                    r'.*\.vercel\.app/c/'
                ],
                'priority': 1,
                'metadata_extractors': [
                    r'/redstones/([^/?]+)',
                    r'/c/([^/?]+)'
                ]
            },
            'edgehub': {
                'patterns': [
                    r'edgehub\.click/lattices/',
                    r'edgehub\.click/.*'
                ],
                'priority': 1,
                'metadata_extractors': [r'/lattices/([^/?]+)']
            },
            
            # Social Platforms (Priority 2)
            'twitter': {
                'patterns': [
                    r'twitter\.com/\w+/status/',
                    r'x\.com/\w+/status/',
                    r'twitter\.com/\w+/thread/',
                    r'twitter\.com',
                    r'x\.com'
                ],
                'priority': 2,
                'metadata_extractors': [
                    r'twitter\.com/(\w+)/status/(\d+)',
                    r'x\.com/(\w+)/status/(\d+)'
                ]
            },
            'reddit': {
                'patterns': [
                    r'reddit\.com/r/\w+/comments/',
                    r'www\.reddit\.com/r/\w+/comments/',
                    r'reddit\.com'
                ],
                'priority': 2,
                'metadata_extractors': [
                    r'reddit\.com/r/(\w+)/comments/([a-zA-Z0-9]+)'
                ]
            },
            
            # Content Platforms (Priority 2)
            'medium': {
                'patterns': [r'medium\.com'],
                'priority': 2,
                'metadata_extractors': []
            },
            'substack': {
                'patterns': [r'substack\.com'],
                'priority': 2,
                'metadata_extractors': []
            },
            'github': {
                'patterns': [r'github\.com'],
                'priority': 2,
                'metadata_extractors': []
            },
            'hackernews': {
                'patterns': [r'news\.ycombinator\.com'],
                'priority': 2,
                'metadata_extractors': []
            },
        }
    
    def extract(self, url_or_content: str) -> ExtractedContent:
        """
        🎯 Extract content from any URL or process direct content
        
        Args:
            url_or_content: URL to extract from OR direct content (if no URL scheme)
            
        Returns:
            ExtractedContent: Extracted content with metadata
        """
        try:
            # Check if input is direct content (clipboard mode)
            if not self._is_url(url_or_content):
                return self._extract_direct_content(url_or_content)
            
            # Standard URL processing
            url = url_or_content
            
            # Detect platform
            platform = self._detect_platform(url)
            
            # Fetch content
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            
            # Parse HTML with best available parser
            soup = BeautifulSoup(response.content, self.parser)
            
            # Extract using platform-specific logic
            if platform == 'chatgpt':
                return self._extract_chatgpt(soup, url, platform)
            elif platform == 'claude':
                return self._extract_claude(soup, url, platform)
            elif platform == 'poe':
                return self._extract_poe(soup, url, platform)
            elif platform == 'simplenote':
                return self._extract_simplenote(soup, url, platform)
            elif platform == 'vercel_creative':
                return self._extract_vercel_creative(soup, url, platform)
            elif platform == 'edgehub':
                return self._extract_edgehub(soup, url, platform)
            elif platform == 'twitter':
                return self._extract_twitter(soup, url, platform)
            else:
                return self._extract_generic(soup, url, platform)
                
        except requests.RequestException as e:
            return ExtractedContent(
                title="",
                content="",
                metadata={},
                success=False,
                error_message=f"Network error: {str(e)}",
                platform=platform,
                url=url
            )
        except Exception as e:
            return ExtractedContent(
                title="",
                content="",
                metadata={},
                success=False,
                error_message=f"Extraction error: {str(e)}",
                platform=platform,
                url=url_or_content
            )
    
    def _is_url(self, text: str) -> bool:
        """
        🔍 Check if input text is a URL or direct content
        
        Args:
            text: Input text to check
            
        Returns:
            bool: True if text appears to be a URL, False for direct content
        """
        # Simple URL detection - look for URL schemes
        url_schemes = ['http://', 'https://', 'ftp://', 'file://']
        text_lower = text.lower().strip()
        
        # Check for URL schemes
        for scheme in url_schemes:
            if text_lower.startswith(scheme):
                return True
        
        # Check for domain patterns (basic heuristic)
        if '.' in text and len(text.split()) == 1:
            # Looks like a domain (single word with dots)
            if not text.startswith('.') and not text.endswith('.'):
                # Check if it contains common TLDs
                common_tlds = ['.com', '.org', '.net', '.edu', '.gov', '.click', '.ai', '.app']
                for tld in common_tlds:
                    if tld in text_lower:
                        return True
        
        # If none of the above, treat as direct content
        return False
    
    def _extract_direct_content(self, content: str) -> ExtractedContent:
        """
        📝 Process direct content (clipboard mode)
        
        Args:
            content: Raw text content
            
        Returns:
            ExtractedContent: Processed content with metadata
        """
        try:
            # Basic content processing
            content = content.strip()
            
            if not content:
                return ExtractedContent(
                    title="Empty Content",
                    content="",
                    metadata={
                        'platform': 'clipboard',
                        'extraction_method': 'direct_content',
                        'content_length': 0,
                        'parser_info': self.get_parser_info()
                    },
                    success=False,
                    error_message="Content is empty",
                    platform="clipboard",
                    url="clipboard://direct"
                )
            
            # Extract title from first line or use default
            lines = content.split('\n')
            first_line = lines[0].strip()
            
            # Use first line as title if it's short enough, otherwise generate one
            if len(first_line) <= 100 and len(lines) > 1:
                title = first_line
                # Remove title from content to avoid duplication
                content_body = '\n'.join(lines[1:]).strip()
            else:
                title = "Clipboard Content"
                content_body = content
            
            # Detect potential content type
            content_type = self._detect_content_type(content)
            
            return ExtractedContent(
                title=title,
                content=content_body,
                metadata={
                    'platform': 'clipboard',
                    'extraction_method': 'direct_content',
                    'content_length': len(content_body),
                    'content_type': content_type,
                    'line_count': len(content.split('\n')),
                    'word_count': len(content.split()),
                    'parser_info': self.get_parser_info()
                },
                success=True,
                platform="clipboard",
                url="clipboard://direct"
            )
            
        except Exception as e:
            return ExtractedContent(
                title="",
                content="",
                metadata={'platform': 'clipboard'},
                success=False,
                error_message=f"Direct content processing failed: {str(e)}",
                platform="clipboard",
                url="clipboard://direct"
            )
    
    def _detect_content_type(self, content: str) -> str:
        """
        🔍 Detect the type of content for better processing
        
        Args:
            content: Content to analyze
            
        Returns:
            str: Detected content type
        """
        content_lower = content.lower()
        
        # Check for conversation patterns
        conversation_indicators = [
            'user:', 'assistant:', 'human:', 'ai:', 'you:', 'me:',
            'q:', 'a:', 'question:', 'answer:', '##', '**user**', '**assistant**'
        ]
        
        for indicator in conversation_indicators:
            if indicator in content_lower:
                return 'conversation'
        
        # Check for code patterns
        code_indicators = [
            'def ', 'function ', 'class ', 'import ', 'from ',
            '```', '#!/', '{', '}', 'console.log', 'print('
        ]
        
        for indicator in code_indicators:
            if indicator in content_lower:
                return 'code'
        
        # Check for article/blog patterns
        article_indicators = ['title:', 'author:', 'date:', '# ']
        
        for indicator in article_indicators:
            if indicator in content_lower:
                return 'article'
        
        # Default to general text
        if '\n' in content and len(content.split('\n')) > 3:
            return 'text_multiline'
        else:
            return 'text_single'
    
    def _detect_best_parser(self) -> str:
        """
        🔍 Detect the best available HTML parser
        
        Returns:
            str: Parser name ('lxml' or 'html.parser')
        """
        try:
            import lxml
            return 'lxml'  # Fastest parser
        except ImportError:
            return 'html.parser'  # Built-in fallback (mobile-friendly)
    
    def get_parser_info(self) -> Dict[str, Any]:
        """
        📊 Get information about the current parser
        
        Returns:
            dict: Parser information and capabilities
        """
        parser_info = {
            'parser': self.parser,
            'mobile_friendly': self.parser == 'html.parser',
            'performance': 'fast' if self.parser == 'lxml' else 'standard'
        }
        
        if self.parser == 'lxml':
            try:
                import lxml
                parser_info['lxml_version'] = lxml.__version__
                parser_info['features'] = ['fast_parsing', 'xml_support', 'xpath']
            except ImportError:
                pass
        else:
            parser_info['features'] = ['mobile_compatible', 'no_dependencies', 'built_in']
        
        return parser_info
    
    def _detect_platform(self, url: str) -> str:
        """
        🔍 Detect platform from URL with advanced pattern matching
        
        Enhanced with SharedSpark's sophisticated pattern detection logic.
        Supports priority-based matching and confidence scoring.
        """
        full_url = url.lower()
        
        # Sort platforms by priority (lower number = higher priority)
        sorted_platforms = sorted(
            self.platform_patterns.items(),
            key=lambda x: x[1].get('priority', 999)
        )
        
        # Check each platform pattern in priority order
        for platform_name, platform_config in sorted_platforms:
            patterns = platform_config['patterns']
            for pattern in patterns:
                if re.search(pattern, full_url):
                    return platform_name
        
        return "generic"
    
    def get_platform_info(self, url: str) -> Dict[str, Any]:
        """
        🏷️  Get detailed platform information with metadata extraction
        
        Returns platform name, confidence score, and extracted metadata.
        """
        platform = self._detect_platform(url)
        
        if platform == "generic":
            return {
                "platform": platform,
                "confidence": 0.0,
                "metadata": {"url": url}
            }
        
        # Calculate confidence and extract metadata
        platform_config = self.platform_patterns[platform]
        confidence = self._calculate_confidence(url, platform_config)
        metadata = self._extract_metadata(url, platform, platform_config)
        
        return {
            "platform": platform,
            "confidence": confidence,
            "metadata": metadata
        }
    
    def _calculate_confidence(self, url: str, platform_config: dict) -> float:
        """Calculate confidence score for platform detection"""
        matches = 0
        total_patterns = len(platform_config['patterns'])
        
        for pattern in platform_config['patterns']:
            if re.search(pattern, url.lower()):
                matches += 1
        
        return matches / total_patterns if total_patterns > 0 else 0.0
    
    def _extract_metadata(self, url: str, platform: str, platform_config: dict) -> Dict[str, Any]:
        """
        🏷️  Extract platform-specific metadata from URL
        
        Uses platform-specific regex patterns to extract IDs, usernames, etc.
        """
        metadata = {"url": url, "platform": platform}
        
        metadata_extractors = platform_config.get('metadata_extractors', [])
        
        for extractor_pattern in metadata_extractors:
            match = re.search(extractor_pattern, url)
            if match:
                groups = match.groups()
                
                # Platform-specific metadata mapping
                if platform == 'chatgpt':
                    if '/share/' in url:
                        metadata['share_id'] = groups[0] if groups else None
                    elif '/c/' in url:
                        metadata['conversation_id'] = groups[0] if groups else None
                        
                elif platform == 'poe':
                    if '/s/' in url:
                        metadata['conversation_id'] = groups[0] if groups else None
                    elif '/share/' in url:
                        metadata['share_id'] = groups[0] if groups else None
                        
                elif platform == 'simplenote':
                    metadata['note_id'] = groups[0] if groups else None
                    
                elif platform == 'vercel_creative':
                    if '/redstones/' in url:
                        metadata['redstone_id'] = groups[0] if groups else None
                        if 'fractal-stone-writer' in url:
                            metadata['app_type'] = 'fractal_stone_writer'
                    elif '/c/' in url:
                        metadata['conversation_id'] = groups[0] if groups else None
                        if 'miadi.vercel.app' in url:
                            metadata['app_type'] = 'miadi'
                            
                elif platform == 'edgehub':
                    metadata['lattice_id'] = groups[0] if groups else None
                    
                elif platform == 'twitter':
                    if len(groups) >= 2:
                        metadata['username'] = groups[0]
                        metadata['tweet_id'] = groups[1]
                        
                elif platform == 'reddit':
                    if len(groups) >= 2:
                        metadata['subreddit'] = groups[0]
                        metadata['post_id'] = groups[1]
                
                break  # Use first matching extractor
        
        return metadata
    
    def _extract_chatgpt(self, soup: BeautifulSoup, url: str, platform: str) -> ExtractedContent:
        """Extract content from ChatGPT share links"""
        try:
            # Try to find conversation content
            messages = []
            
            # Look for message containers
            message_selectors = [
                'div[data-message-author-role]',
                '.message',
                '[class*="message"]',
                'div.group',
                'div[role="group"]'
            ]
            
            for selector in message_selectors:
                elements = soup.select(selector)
                if elements:
                    for element in elements:
                        text = element.get_text(strip=True)
                        if text and len(text) > 20:  # Filter out short/empty messages
                            messages.append(text)
                    break
            
            # Fallback to general text extraction
            if not messages:
                content = self._extract_text_content(soup)
            else:
                content = '\n\n'.join(messages)
            
            # Extract title
            title = self._extract_title(soup) or "ChatGPT Conversation"
            
            # Get platform metadata with extracted IDs
            platform_info = self.get_platform_info(url)
            
            return ExtractedContent(
                title=title,
                content=content,
                metadata={
                    **platform_info['metadata'],
                    'message_count': len(messages),
                    'extraction_method': 'chatgpt_specific',
                    'confidence': platform_info['confidence'],
                    'parser_info': self.get_parser_info()
                },
                success=bool(content),
                platform=platform,
                url=url
            )
            
        except Exception as e:
            return self._extract_generic(soup, url, platform)
    
    def _extract_claude(self, soup: BeautifulSoup, url: str, platform: str) -> ExtractedContent:
        """Extract content from Claude.ai conversations"""
        try:
            # Look for Claude conversation elements
            content_selectors = [
                '[data-testid="conversation"]',
                '.conversation',
                '[class*="message"]',
                'main',
                'article'
            ]
            
            content = ""
            for selector in content_selectors:
                element = soup.select_one(selector)
                if element:
                    content = element.get_text(strip=True)
                    if content:
                        break
            
            if not content:
                content = self._extract_text_content(soup)
            
            title = self._extract_title(soup) or "Claude Conversation"
            
            # Get platform metadata
            platform_info = self.get_platform_info(url)
            
            return ExtractedContent(
                title=title,
                content=content,
                metadata={
                    **platform_info['metadata'],
                    'extraction_method': 'claude_specific',
                    'confidence': platform_info['confidence'],
                    'parser_info': self.get_parser_info()
                },
                success=bool(content),
                platform=platform,
                url=url
            )
            
        except Exception as e:
            return self._extract_generic(soup, url, platform)
    
    def _extract_simplenote(self, soup: BeautifulSoup, url: str, platform: str) -> ExtractedContent:
        """Extract content from Simplenote public links"""
        try:
            # Look for Simplenote content
            content_selectors = [
                '.note-content',
                '.simplenote-content',
                '.content',
                'pre',
                'main'
            ]
            
            content = ""
            for selector in content_selectors:
                element = soup.select_one(selector)
                if element:
                    content = element.get_text(strip=True)
                    if content:
                        break
            
            if not content:
                content = self._extract_text_content(soup)
            
            title = self._extract_title(soup) or "Simplenote"
            
            # Get platform metadata with note ID
            platform_info = self.get_platform_info(url)
            
            return ExtractedContent(
                title=title,
                content=content,
                metadata={
                    **platform_info['metadata'],
                    'extraction_method': 'simplenote_specific',
                    'confidence': platform_info['confidence'],
                    'parser_info': self.get_parser_info()
                },
                success=bool(content),
                platform=platform,
                url=url
            )
            
        except Exception as e:
            return self._extract_generic(soup, url, platform)
    
    def _extract_poe(self, soup: BeautifulSoup, url: str, platform: str) -> ExtractedContent:
        """Extract content from Poe.com conversations"""
        try:
            # Look for Poe conversation elements
            content_selectors = [
                '[data-testid="conversation"]',
                '.conversation',
                '[class*="message"]',
                '.chat-message',
                'main',
                'article'
            ]
            
            content = ""
            for selector in content_selectors:
                element = soup.select_one(selector)
                if element:
                    content = element.get_text(strip=True)
                    if content:
                        break
            
            if not content:
                content = self._extract_text_content(soup)
            
            title = self._extract_title(soup) or "Poe Conversation"
            
            # Get platform metadata
            platform_info = self.get_platform_info(url)
            
            return ExtractedContent(
                title=title,
                content=content,
                metadata={
                    **platform_info['metadata'],
                    'extraction_method': 'poe_specific',
                    'confidence': platform_info['confidence'],
                    'parser_info': self.get_parser_info()
                },
                success=bool(content),
                platform=platform,
                url=url
            )
            
        except Exception as e:
            return self._extract_generic(soup, url, platform)
    
    def _extract_vercel_creative(self, soup: BeautifulSoup, url: str, platform: str) -> ExtractedContent:
        """Extract content from Vercel creative platforms (Fractal Stone Writer, Miadi)"""
        try:
            # Look for creative platform content
            content_selectors = [
                '.redstone-content',
                '.fractal-content',
                '.miadi-content',
                '.content',
                'main',
                'article',
                '[role="main"]'
            ]
            
            content = ""
            for selector in content_selectors:
                element = soup.select_one(selector)
                if element:
                    content = element.get_text(strip=True)
                    if content:
                        break
            
            if not content:
                content = self._extract_text_content(soup)
            
            title = self._extract_title(soup) or "Creative Content"
            
            # Get platform metadata
            platform_info = self.get_platform_info(url)
            
            return ExtractedContent(
                title=title,
                content=content,
                metadata={
                    **platform_info['metadata'],
                    'extraction_method': 'vercel_creative_specific',
                    'confidence': platform_info['confidence'],
                    'parser_info': self.get_parser_info()
                },
                success=bool(content),
                platform=platform,
                url=url
            )
            
        except Exception as e:
            return self._extract_generic(soup, url, platform)
    
    def _extract_edgehub(self, soup: BeautifulSoup, url: str, platform: str) -> ExtractedContent:
        """Extract content from EdgeHub lattices"""
        try:
            # Look for EdgeHub lattice content
            content_selectors = [
                '.lattice-content',
                '.edgehub-content',
                '.content',
                'main',
                'article',
                '[role="main"]'
            ]
            
            content = ""
            for selector in content_selectors:
                element = soup.select_one(selector)
                if element:
                    content = element.get_text(strip=True)
                    if content:
                        break
            
            if not content:
                content = self._extract_text_content(soup)
            
            title = self._extract_title(soup) or "EdgeHub Lattice"
            
            # Get platform metadata
            platform_info = self.get_platform_info(url)
            
            return ExtractedContent(
                title=title,
                content=content,
                metadata={
                    **platform_info['metadata'],
                    'extraction_method': 'edgehub_specific',
                    'confidence': platform_info['confidence'],
                    'parser_info': self.get_parser_info()
                },
                success=bool(content),
                platform=platform,
                url=url
            )
            
        except Exception as e:
            return self._extract_generic(soup, url, platform)
    
    def _extract_twitter(self, soup: BeautifulSoup, url: str, platform: str) -> ExtractedContent:
        """Extract content from Twitter/X posts"""
        try:
            # Look for Twitter content
            content_selectors = [
                '[data-testid="tweet"]',
                '[data-testid="tweetText"]',
                '.tweet-text',
                '[role="article"]',
                'article',
                'main'
            ]
            
            content = ""
            for selector in content_selectors:
                element = soup.select_one(selector)
                if element:
                    content = element.get_text(strip=True)
                    if content:
                        break
            
            if not content:
                content = self._extract_text_content(soup)
            
            title = self._extract_title(soup) or "Twitter Post"
            
            # Get platform metadata
            platform_info = self.get_platform_info(url)
            
            return ExtractedContent(
                title=title,
                content=content,
                metadata={
                    **platform_info['metadata'],
                    'extraction_method': 'twitter_specific',
                    'confidence': platform_info['confidence'],
                    'parser_info': self.get_parser_info()
                },
                success=bool(content),
                platform=platform,
                url=url
            )
            
        except Exception as e:
            return self._extract_generic(soup, url, platform)
    
    def _extract_generic(self, soup: BeautifulSoup, url: str, platform: str) -> ExtractedContent:
        """Generic content extraction for any website"""
        try:
            # Extract title
            title = self._extract_title(soup)
            
            # Extract main content
            content = self._extract_text_content(soup)
            
            # Get platform metadata (may include confidence scoring for generic platforms)
            platform_info = self.get_platform_info(url)
            
            return ExtractedContent(
                title=title or "Web Content",
                content=content,
                metadata={
                    **platform_info['metadata'],
                    'extraction_method': 'generic',
                    'content_length': len(content),
                    'confidence': platform_info['confidence'],
                    'parser_info': self.get_parser_info()
                },
                success=bool(content),
                platform=platform,
                url=url
            )
            
        except Exception as e:
            return ExtractedContent(
                title="",
                content="",
                metadata={'platform': platform},
                success=False,
                error_message=f"Generic extraction failed: {str(e)}",
                platform=platform,
                url=url
            )
    
    def _extract_title(self, soup: BeautifulSoup) -> str:
        """Extract page title"""
        # Try multiple title sources
        title_selectors = [
            'h1',
            'title', 
            '[property="og:title"]',
            '[name="twitter:title"]',
            '.title',
            '#title'
        ]
        
        for selector in title_selectors:
            element = soup.select_one(selector)
            if element:
                if element.name == 'meta':
                    title = element.get('content', '').strip()
                else:
                    title = element.get_text(strip=True)
                
                if title:
                    return title[:200]  # Limit title length
        
        return ""
    
    def _extract_text_content(self, soup: BeautifulSoup) -> str:
        """Extract main text content from page"""
        # Remove unwanted elements
        for element in soup(['script', 'style', 'nav', 'header', 'footer', 'aside']):
            element.decompose()
        
        # Try main content selectors
        content_selectors = [
            'main',
            'article', 
            '[role="main"]',
            '.content',
            '.post-content',
            '.entry-content',
            '.article-content',
            '#content',
            'body'
        ]
        
        for selector in content_selectors:
            element = soup.select_one(selector)
            if element:
                text = element.get_text(separator=' ', strip=True)
                if text and len(text) > 100:  # Ensure meaningful content
                    return text
        
        # Fallback: extract all text
        return soup.get_text(separator=' ', strip=True)
    
    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - close session"""
        self.session.close()