#!/usr/bin/env python3
"""
🤖 ChatMusician Block - The Star AI Composer
Professional AI-powered music generation for LinkTune

Based on the G.Music Assembly ChatMusician integration but simplified for packaging.
"""

import os
import json
import time
import requests
from typing import Dict, Any, Optional
from dataclasses import dataclass

from ...core.analyzer import ContentAnalysis

@dataclass
class ChatMusicianConfig:
    """Configuration for ChatMusician HuggingFace Integration"""
    hf_model_id: str = "m-a-p/ChatMusician"
    hf_space_url: str = "https://huggingface.co/spaces/m-a-p/ChatMusician"
    api_endpoint: str = "https://api-inference.huggingface.co/models/m-a-p/ChatMusician"
    api_key: str = ""  # HuggingFace API token
    timeout: int = 60
    max_retries: int = 3
    use_local: bool = False  # Whether to use local model vs HF API
    
    @classmethod
    def from_env(cls) -> 'ChatMusicianConfig':
        """Create config from environment variables"""
        return cls(
            hf_model_id=os.getenv('CHATMUSICIAN_MODEL_ID', cls.hf_model_id),
            hf_space_url=os.getenv('CHATMUSICIAN_SPACE_URL', cls.hf_space_url),
            api_endpoint=os.getenv('CHATMUSICIAN_ENDPOINT', cls.api_endpoint),
            api_key=os.getenv('HUGGINGFACE_API_TOKEN', cls.api_key),
            timeout=int(os.getenv('CHATMUSICIAN_TIMEOUT', str(cls.timeout))),
            max_retries=int(os.getenv('CHATMUSICIAN_RETRIES', str(cls.max_retries))),
            use_local=os.getenv('CHATMUSICIAN_USE_LOCAL', 'false').lower() == 'true'
        )

class ChatMusicianBlock:
    """
    🤖 ChatMusician AI Music Generation Block
    
    Professional AI composer that generates sophisticated ABC notation
    with advanced harmonies, style awareness, and ornamental expressions.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        
        # Initialize ChatMusician configuration
        self.chatmusician_config = ChatMusicianConfig.from_env()
        
        # Override with provided config
        if 'chatmusician' in self.config:
            cm_config = self.config['chatmusician']
            for key, value in cm_config.items():
                if hasattr(self.chatmusician_config, key):
                    setattr(self.chatmusician_config, key, value)
        
        # Session for API calls
        self.session = requests.Session()
        headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'LinkTune-ChatMusician-Client/1.0'
        }
        
        # Add HuggingFace API token if available
        if self.chatmusician_config.api_key:
            headers['Authorization'] = f'Bearer {self.chatmusician_config.api_key}'
        
        self.session.headers.update(headers)
        
        self.capabilities = [
            'professional_composition',
            'advanced_harmonies', 
            'style_transfer',
            'ornamental_expressions',
            'genre_awareness',
            'emotional_intelligence'
        ]
    
    def generate_abc(self, analysis: ContentAnalysis, config: Dict[str, Any]) -> str:
        """
        🎵 Generate professional ABC notation using ChatMusician AI
        
        Args:
            analysis: Content analysis with emotional and thematic data
            config: Generation configuration
            
        Returns:
            str: Professional ABC notation
        """
        try:
            # Check if we can connect to ChatMusician
            if not self._test_connection():
                # Fallback to rule-based generation
                return self._fallback_generation(analysis, config)
            
            # Build musical prompt from analysis
            prompt = self._build_musical_prompt(analysis)
            
            # Get style preferences
            style = self._determine_style(analysis, config)
            
            # Calculate emotional parameters
            emotional_weight = analysis.emotional_profile.intensity
            complexity = self._determine_complexity(analysis)
            
            # Generate with ChatMusician
            abc_result = self._call_chatmusician_api(
                prompt=prompt,
                style=style,
                emotional_weight=emotional_weight,
                complexity=complexity,
                config=config
            )
            
            # Enhance and validate result
            enhanced_abc = self._enhance_abc_notation(abc_result, analysis)
            
            return enhanced_abc
            
        except Exception as e:
            # Fallback to rule-based generation
            print(f"ChatMusician generation failed: {e}")
            return self._fallback_generation(analysis, config)
    
    def _test_connection(self) -> bool:
        """Test connection to ChatMusician HuggingFace API"""
        try:
            # Test with a simple inference request
            test_payload = {
                "inputs": "Generate a simple C major scale in ABC notation:",
                "parameters": {
                    "max_new_tokens": 50,
                    "temperature": 0.7
                }
            }
            
            response = self.session.post(
                self.chatmusician_config.api_endpoint,
                json=test_payload,
                timeout=10
            )
            
            # HuggingFace API returns 200 for successful requests
            return response.status_code == 200
        except:
            return False
    
    def _build_musical_prompt(self, analysis: ContentAnalysis) -> str:
        """Build musical generation prompt from content analysis"""
        emotion = analysis.emotional_profile.primary_emotion.value
        intensity = analysis.emotional_profile.intensity
        themes = [t.name for t in analysis.themes[:3]]
        
        # Check for custom prompts
        custom_prompts = self.config.get('prompts', {})
        if 'chatmusician_composition' in custom_prompts:
            # Use custom prompt template
            prompt_template = custom_prompts['chatmusician_composition']
            return prompt_template.format(
                emotion=emotion,
                intensity=intensity,
                themes=', '.join(themes)
            )
        
        # Default prompt
        prompt = f"""Generate professional ABC notation for a musical composition with the following characteristics:

Primary Emotion: {emotion.title()}
Emotional Intensity: {intensity:.2f} (0.0 = subtle, 1.0 = intense)
Themes: {', '.join(themes) if themes else 'general content'}

Musical Requirements:
- Professional quality composition with sophisticated harmonies
- Emotionally resonant melody that reflects the {emotion} feeling
- Appropriate chord progressions for the emotional content
- Clear musical structure with logical phrasing
- Standard ABC notation format with proper headers
- Include ornamental expressions where appropriate
- Maintain musical coherence throughout

Style Guidelines:
- Use the emotional intensity to guide tempo and dynamics
- Incorporate thematic elements into the melodic development
- Create a complete, performance-ready composition
- Ensure the music tells the emotional story of the content"""

        return prompt
    
    def _determine_style(self, analysis: ContentAnalysis, config: Dict[str, Any]) -> str:
        """Determine musical style from analysis and config"""
        # Check explicit style in config
        if 'style' in config:
            return config['style']
        
        # Infer style from content themes
        for theme in analysis.themes:
            if theme.name in ['technology', 'science']:
                return 'contemporary'
            elif theme.name in ['nature', 'environment']:
                return 'celtic'
            elif theme.name in ['relationships', 'love']:
                return 'romantic'
            elif theme.name in ['adventure', 'action']:
                return 'cinematic'
        
        # Default based on emotion
        emotion = analysis.emotional_profile.primary_emotion.value
        style_map = {
            'joy': 'classical',
            'sadness': 'blues', 
            'contemplation': 'ambient',
            'excitement': 'jazz',
            'peace': 'folk',
            'love': 'romantic'
        }
        
        return style_map.get(emotion, 'classical')
    
    def _determine_complexity(self, analysis: ContentAnalysis) -> str:
        """Determine musical complexity from content analysis"""
        content_complexity = analysis.structure.get('complexity', 'medium')
        content_length = analysis.structure.get('length', 100)
        
        if content_complexity == 'simple' or content_length < 50:
            return 'simple'
        elif content_complexity == 'complex' or content_length > 500:
            return 'complex'
        else:
            return 'medium'
    
    def _call_chatmusician_api(self, prompt: str, style: str, emotional_weight: float,
                              complexity: str, config: Dict[str, Any]) -> str:
        """Call ChatMusician HuggingFace API for music generation"""
        
        # Build HuggingFace API compatible prompt
        enhanced_prompt = f"""Generate ABC notation for a {style} composition with {complexity} complexity.

{prompt}

Please provide only valid ABC notation with proper headers (X:, T:, K:, M:, L:) and musical content. The composition should reflect the specified emotional characteristics and style."""

        # HuggingFace Inference API payload
        payload = {
            "inputs": enhanced_prompt,
            "parameters": {
                "max_new_tokens": 800,
                "temperature": min(0.9, 0.3 + emotional_weight * 0.6),  # Dynamic temperature based on emotion
                "do_sample": True,
                "top_p": 0.9,
                "repetition_penalty": 1.1
            }
        }
        
        # Add any additional HuggingFace parameters
        if 'chatmusician_params' in config:
            hf_params = config['chatmusician_params'].get('hf_parameters', {})
            payload['parameters'].update(hf_params)
        
        for attempt in range(self.chatmusician_config.max_retries):
            try:
                response = self.session.post(
                    self.chatmusician_config.api_endpoint,
                    json=payload,
                    timeout=self.chatmusician_config.timeout
                )
                
                if response.status_code == 200:
                    result = response.json()
                    
                    # HuggingFace returns a list with generated text
                    if isinstance(result, list) and len(result) > 0:
                        generated_text = result[0].get('generated_text', '')
                    else:
                        generated_text = result.get('generated_text', '')
                    
                    # Extract ABC notation from the generated text
                    abc_notation = self._extract_abc_from_response(generated_text)
                    
                    if abc_notation:
                        return abc_notation
                    else:
                        raise ValueError("No valid ABC notation found in response")
                        
                elif response.status_code == 429:  # Rate limited
                    wait_time = 2 ** attempt
                    time.sleep(wait_time)
                    continue
                elif response.status_code == 503:  # Model loading
                    # Model is loading, wait longer
                    wait_time = 10 + (5 * attempt)
                    time.sleep(wait_time)
                    continue
                else:
                    raise ValueError(f"HuggingFace API error: {response.status_code} - {response.text}")
                    
            except requests.RequestException as e:
                if attempt == self.chatmusician_config.max_retries - 1:
                    raise
                time.sleep(2)
        
        raise RuntimeError("ChatMusician HuggingFace API call failed after all retries")
    
    def _extract_abc_from_response(self, generated_text: str) -> str:
        """Extract ABC notation from HuggingFace model response"""
        import re
        
        # Look for ABC notation pattern starting with X:
        abc_pattern = r'(X:\s*\d+.*?)(?=\n\s*\n|\n\s*[A-Z]:|$)'
        matches = re.findall(abc_pattern, generated_text, re.DOTALL | re.MULTILINE)
        
        if matches:
            # Return the first (and usually only) ABC block found
            abc_content = matches[0].strip()
            return abc_content
        
        # Fallback: look for lines that seem like ABC notation
        lines = generated_text.split('\n')
        abc_lines = []
        in_abc = False
        
        for line in lines:
            line = line.strip()
            # Start of ABC notation
            if line.startswith('X:'):
                in_abc = True
                abc_lines = [line]
            elif in_abc:
                # Continue collecting ABC lines
                if line and (line.startswith(('T:', 'M:', 'L:', 'K:', 'C:', 'Q:', 'A:', 'B:', 'R:', 'N:', 'Z:', 'S:', 'I:', 'H:', 'F:', 'G:', 'D:', 'P:')) or 
                           '|' in line or line.replace(' ', '').replace('|', '').replace(':', '').replace('-', '').replace('"', '').isalpha()):
                    abc_lines.append(line)
                elif line == '':
                    # Empty line might be end of ABC
                    if len(abc_lines) > 3:  # Has substantial content
                        break
                else:
                    # Non-ABC line, stop collection
                    break
        
        if abc_lines and len(abc_lines) > 1:
            return '\n'.join(abc_lines)
        
        return ""
    
    def _enhance_abc_notation(self, abc_result: str, analysis: ContentAnalysis) -> str:
        """Enhance generated ABC with metadata and validation"""
        emotion = analysis.emotional_profile.primary_emotion.value
        themes = ', '.join([t.name for t in analysis.themes])
        
        # Add LinkTune metadata header
        enhanced_header = f"""% Generated by LinkTune ChatMusician AI via HuggingFace
% Model: m-a-p/ChatMusician (6.74B parameters)
% Professional AI Composition Engine
% Emotion: {emotion.title()} (intensity: {analysis.emotional_profile.intensity:.2f})
% Themes: {themes}
% Features: Advanced harmonies, ornamental expressions, style transfer
% Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}

"""
        
        # Ensure the ABC has proper structure
        if not abc_result.startswith('X:'):
            # Add minimal headers if missing
            abc_result = f"""X:1
T:AI Generated Composition
C:ChatMusician via LinkTune
M:4/4
L:1/8
Q:1/4=120
K:C major
{abc_result}"""
        
        return enhanced_header + abc_result
    
    def _fallback_generation(self, analysis: ContentAnalysis, config: Dict[str, Any]) -> str:
        """Fallback to rule-based generation if ChatMusician fails"""
        from ...core.generator import MusicGenerator
        
        generator = MusicGenerator()
        abc_result = generator.generate_abc(analysis, config)
        
        # Add fallback notice
        fallback_header = """% Generated by LinkTune Core Engine (ChatMusician fallback)
% Note: ChatMusician AI was not available, using rule-based generation
% For professional AI composition, ensure ChatMusician API is accessible

"""
        
        return fallback_header + abc_result
    
    def get_info(self) -> Dict[str, Any]:
        """Get information about this block"""
        return {
            'name': 'ChatMusician AI Composer',
            'type': 'ai_generator',
            'capabilities': self.capabilities,
            'hf_model_id': self.chatmusician_config.hf_model_id,
            'hf_space_url': self.chatmusician_config.hf_space_url,
            'api_endpoint': self.chatmusician_config.api_endpoint,
            'connected': self._test_connection(),
            'use_local': self.chatmusician_config.use_local,
            'parameters': '6.74B',
            'provider': 'HuggingFace'
        }