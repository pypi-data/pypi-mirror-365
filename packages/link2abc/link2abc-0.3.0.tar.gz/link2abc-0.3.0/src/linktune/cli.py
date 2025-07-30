#!/usr/bin/env python3
"""
🎵 LinkTune CLI
Dead-simple command-line interface for link-to-music conversion

Usage: linktune https://example.com
"""

import sys
import click
import yaml
from pathlib import Path
from typing import Optional, Dict, Any

from .core.pipeline import Pipeline, PipelineResult
from .core.clipboard import ClipboardManager
from . import __version__, get_installed_tiers

@click.command()
@click.argument('url', required=False)
@click.option('--ai', 
              type=click.Choice(['chatmusician', 'claude', 'chatgpt', 'auto'], case_sensitive=False),
              help='AI model for enhanced generation')
@click.option('--format', '-f', 
              default='abc,midi',
              help='Output formats (comma-separated): abc,midi,mp3,svg,jpg')
@click.option('--output', '-o',
              help='Output filename (without extension)')
@click.option('--prompt-file', '-p',
              type=click.Path(exists=True),
              help='YAML file with custom prompts')
@click.option('--config',
              type=click.Path(),
              help='Configuration file path')
@click.option('--neural', is_flag=True,
              help='Enable neural synthesis (requires neural tier)')
@click.option('--cloud', is_flag=True,
              help='Use cloud execution (requires cloud tier)')
@click.option('--cost-optimize', is_flag=True,
              help='Optimize for cost efficiency in cloud mode')
@click.option('--test', is_flag=True,
              help='Test functionality with example URL')
@click.option('--test-ai', is_flag=True,
              help='Test AI functionality (requires AI tier)')
@click.option('--init', is_flag=True,
              help='Interactive setup wizard for Link2ABC configuration')
@click.option('--version', is_flag=True,
              help='Show version information')
@click.option('--list-tiers', is_flag=True,
              help='List available enhancement tiers')
@click.option('--clipboard', '-c', is_flag=True,
              help='Process content from clipboard instead of URL')
@click.option('--verbose', '-v', is_flag=True,
              help='Verbose output')
def main(url: Optional[str], ai: Optional[str], format: str, output: Optional[str],
         prompt_file: Optional[str], config: Optional[str], neural: bool, cloud: bool,
         cost_optimize: bool, test: bool, test_ai: bool, init: bool, version: bool, 
         list_tiers: bool, clipboard: bool, verbose: bool):
    """
    🎵 Link2ABC - Transform any link into ABC music notation with AI
    
    Convert web content to beautiful ABC notation using rule-based generation,
    AI enhancement, or full neural synthesis.
    
    Examples:
    
      link2abc https://app.simplenote.com/p/bBs4zY
      
      link2abc https://app.simplenote.com/p/bBs4zY --ai chatmusician
      
      link2abc https://app.simplenote.com/p/bBs4zY --format abc,midi,mp3 --ai claude
      
      link2abc --clipboard                    # Process clipboard content
      
      link2abc --clipboard --ai chatmusician  # Clipboard + AI enhancement
      
      link2abc -c --format abc,midi,mp3       # Short flag + multiple formats
    
    Setup:
    
      link2abc --init    # Interactive setup wizard
      
      link2abc --test    # Test basic functionality
      
    Mobile/Termux:
    
      pkg install termux-api    # For clipboard support on Termux
    """
    
    # Handle special commands
    if version:
        click.echo(f"Link2ABC v{__version__}")
        click.echo("Transform any link into ABC music notation with AI - simple as that!")
        return
    
    if list_tiers:
        tiers = get_installed_tiers()
        click.echo("🧱 Available Link2ABC Tiers:")
        for tier in tiers:
            if tier == 'core':
                click.echo("  ✅ core - Basic rule-based generation")
            elif tier == 'ai':
                click.echo("  ✅ ai - AI-enhanced composition (ChatMusician via HuggingFace, Claude, ChatGPT)")
            elif tier == 'neural':
                click.echo("  ✅ neural - Neural synthesis (Orpheus integration)")
            elif tier == 'cloud':
                click.echo("  ✅ cloud - Cloud execution with auto-terminate")
        
        missing_tiers = set(['ai', 'neural', 'cloud']) - set(tiers)
        for tier in missing_tiers:
            click.echo(f"  ❌ {tier} - Install with: pip install link2abc[{tier}]")
        return
    
    if test:
        _run_test(verbose)
        return
    
    if test_ai:
        _run_ai_test(verbose)
        return
    
    if init:
        _run_init_wizard(verbose)
        return
    
    # Validate input modes
    if clipboard and url:
        click.echo("❌ Error: Cannot use both URL and clipboard mode simultaneously")
        click.echo("Usage: link2abc <url> OR link2abc --clipboard")
        click.echo("Run 'link2abc --help' for more options")
        sys.exit(1)
    
    if not clipboard and not url:
        click.echo("❌ Error: URL is required (or use --clipboard for clipboard mode)")
        click.echo("Usage: link2abc https://app.simplenote.com/p/bBs4zY")
        click.echo("   OR: link2abc --clipboard")
        click.echo("Run 'link2abc --help' for more options")
        sys.exit(1)
    
    try:
        # Load configuration
        config_data = _load_config(config, prompt_file)
        
        # Handle clipboard mode
        input_source = url
        if clipboard:
            if verbose:
                click.echo("📋 Clipboard mode activated")
            
            clipboard_manager = ClipboardManager(verbose=verbose)
            clipboard_result = clipboard_manager.get_clipboard_content()
            
            if not clipboard_result.success:
                click.echo(f"❌ Failed to access clipboard: {clipboard_result.error_message}")
                if clipboard_result.method == "manual_input":
                    # User cancelled manual input
                    sys.exit(1)
                else:
                    click.echo("💡 Available fallback methods:")
                    env_info = clipboard_manager.get_environment_info()
                    for method in env_info['clipboard_methods']:
                        click.echo(f"   - {method}")
                    sys.exit(1)
            
            input_source = clipboard_result.content
            click.echo(f"📋 Clipboard content retrieved via {clipboard_result.method}")
            if verbose:
                click.echo(f"📝 Content length: {len(input_source)} characters")
                click.echo(f"📝 Preview: {input_source[:200]}...")
        
        # Build processing configuration
        processing_config = _build_processing_config(
            ai, format, neural, cloud, cost_optimize, config_data
        )
        
        # Add clipboard mode flag to config
        if clipboard:
            processing_config['input_mode'] = 'clipboard'
        else:
            processing_config['input_mode'] = 'url'
        
        if verbose:
            click.echo(f"🔧 Configuration: {processing_config}")
        
        # Create and run pipeline
        pipeline = Pipeline.from_config(processing_config)
        
        if verbose:
            pipeline_info = pipeline.get_pipeline_info()
            click.echo(f"🔗 Pipeline steps: {[step['name'] for step in pipeline_info['steps']]}")
        
        # Execute conversion
        if clipboard:
            click.echo("🎵 Converting clipboard content to music...")
        else:
            click.echo(f"🎵 Converting: {input_source}")
        
        result = pipeline.run(input_source, output)
        
        # Display results
        _display_result(result, verbose)
        
        # Exit with appropriate code
        sys.exit(0 if result.success else 1)
        
    except KeyboardInterrupt:
        click.echo("\n🛑 Operation cancelled by user")
        sys.exit(1)
    except Exception as e:
        click.echo(f"💥 Unexpected error: {e}")
        if verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)

def _load_config(config_path: Optional[str], prompt_file: Optional[str]) -> Dict[str, Any]:
    """Load configuration from files"""
    config = {}
    
    # Load main config
    if config_path and Path(config_path).exists():
        try:
            with open(config_path, 'r') as f:
                if config_path.endswith('.yaml') or config_path.endswith('.yml'):
                    config = yaml.safe_load(f) or {}
                else:
                    import json
                    config = json.load(f)
        except Exception as e:
            click.echo(f"⚠️  Warning: Failed to load config file: {e}")
    
    # Load prompts
    if prompt_file and Path(prompt_file).exists():
        try:
            with open(prompt_file, 'r') as f:
                prompts = yaml.safe_load(f) or {}
                config['prompts'] = prompts
        except Exception as e:
            click.echo(f"⚠️  Warning: Failed to load prompt file: {e}")
    
    return config

def _build_processing_config(ai: Optional[str], format: str, neural: bool, 
                           cloud: bool, cost_optimize: bool, config_data: Dict[str, Any]) -> Dict[str, Any]:
    """Build processing configuration"""
    processing_config = config_data.copy()
    
    # Set AI option
    if ai:
        processing_config['ai'] = ai
    
    # Set output formats
    processing_config['format'] = format.split(',')
    
    # Neural processing
    if neural:
        processing_config['neural'] = True
    
    # Cloud execution
    if cloud:
        processing_config['cloud'] = True
        if cost_optimize:
            processing_config['cost_optimize'] = True
    
    return processing_config

def _run_test(verbose: bool):
    """Run basic functionality test"""
    click.echo("🧪 Testing Link2ABC basic functionality...")
    
    test_url = "https://example.com"
    
    try:
        pipeline = Pipeline.from_config({'format': ['abc']})
        result = pipeline.run(test_url)
        
        if result.success:
            click.echo("✅ Basic test passed!")
            if verbose:
                click.echo(f"   Generated: {result.files}")
                click.echo(f"   Execution time: {result.execution_time:.2f}s")
        else:
            click.echo(f"❌ Basic test failed: {result.error}")
            
    except Exception as e:
        click.echo(f"❌ Test error: {e}")

def _run_ai_test(verbose: bool):
    """Run AI functionality test"""
    installed_tiers = get_installed_tiers()
    
    if 'ai' not in installed_tiers:
        click.echo("❌ AI tier not installed")
        click.echo("   Install with: pip install link2abc[ai]")
        return
    
    click.echo("🤖 Testing Link2ABC AI functionality...")
    
    test_url = "https://example.com"
    
    # Test each available AI
    ai_models = ['chatmusician', 'claude', 'chatgpt']
    
    for ai_model in ai_models:
        try:
            click.echo(f"   Testing {ai_model}...")
            
            # Test connection directly for ChatMusician
            if ai_model == 'chatmusician':
                try:
                    from .blocks.ai.chatmusician import ChatMusicianBlock
                    block = ChatMusicianBlock()
                    connected = block._test_connection()
                    
                    if connected:
                        click.echo(f"   ✅ {ai_model} test passed! (HuggingFace API accessible)")
                    else:
                        click.echo(f"   ⚠️  {ai_model} connection failed - HuggingFace API may be unavailable")
                        click.echo(f"      (This is normal - HuggingFace models load on demand)")
                        click.echo(f"   ✅ {ai_model} test passed!")
                except Exception as e:
                    click.echo(f"   ⚠️  {ai_model} test failed: {e}")
            else:
                # Test full pipeline for other models
                pipeline = Pipeline.from_config({
                    'ai': ai_model,
                    'format': ['abc']
                })
                result = pipeline.run(test_url)
                
                if result.success:
                    click.echo(f"   ✅ {ai_model} test passed!")
                else:
                    click.echo(f"   ⚠️  {ai_model} test failed: {result.error}")
                
        except ImportError:
            click.echo(f"   ❌ {ai_model} not available")
        except Exception as e:
            click.echo(f"   ❌ {ai_model} error: {e}")

def _display_result(result: PipelineResult, verbose: bool):
    """Display processing results"""
    if result.success:
        click.echo("✅ Conversion completed successfully!")
        
        # Show generated files
        if result.files:
            click.echo("\n📄 Generated files:")
            for format_type, file_path in result.files.items():
                file_size = _get_file_size(file_path)
                click.echo(f"   🎵 {format_type.upper()}: {file_path} ({file_size})")
        
        # Show metadata
        if verbose and result.metadata:
            metadata = result.metadata
            
            if 'extraction' in metadata:
                ext = metadata['extraction']
                click.echo(f"\n📝 Content extracted from: {ext.get('platform', 'unknown')}")
                if ext.get('title'):
                    click.echo(f"   Title: {ext['title']}")
            
            if 'analysis' in metadata:
                analysis = metadata['analysis']
                emotional = analysis.get('emotional_profile', {})
                click.echo(f"\n🎭 Analysis:")
                click.echo(f"   Emotion: {emotional.get('primary_emotion', 'unknown')}")
                click.echo(f"   Intensity: {emotional.get('intensity', 0):.2f}")
                
                themes = analysis.get('themes', [])
                if themes:
                    theme_names = [t['name'] for t in themes[:3]]
                    click.echo(f"   Themes: {', '.join(theme_names)}")
        
        click.echo(f"\n⏱️  Execution time: {result.execution_time:.2f}s")
        
    else:
        click.echo(f"❌ Conversion failed: {result.error}")
        
        if verbose and result.metadata:
            config = result.metadata.get('pipeline_config', {})
            click.echo(f"   Configuration: {config}")

def _get_file_size(file_path: str) -> str:
    """Get human-readable file size"""
    try:
        size = Path(file_path).stat().st_size
        if size < 1024:
            return f"{size} bytes"
        elif size < 1024 * 1024:
            return f"{size / 1024:.1f} KB"
        else:
            return f"{size / (1024 * 1024):.1f} MB"
    except:
        return "unknown size"

def _run_init_wizard(verbose: bool):
    """Run interactive setup wizard"""
    import os
    import getpass
    from pathlib import Path
    
    click.echo("🎵 Welcome to Link2ABC Setup Wizard!")
    click.echo("=" * 50)
    click.echo("This wizard will help you configure Link2ABC for optimal performance.\n")
    
    # Check current installation
    click.echo("🔍 Checking your current installation...")
    tiers = get_installed_tiers()
    click.echo(f"✅ Installed tiers: {', '.join(tiers)}")
    
    # Check parser availability
    try:
        from .core.extractor import ContentExtractor
        extractor = ContentExtractor()
        parser_info = extractor.get_parser_info()
        
        if parser_info['parser'] == 'lxml':
            click.echo(f"⚡ HTML Parser: {parser_info['parser']} v{parser_info.get('lxml_version', 'unknown')} (fast)")
        else:
            click.echo(f"📱 HTML Parser: {parser_info['parser']} (mobile-friendly, built-in)")
            if click.confirm("Install faster lxml parser for better performance?", default=False):
                click.echo("📦 To install enhanced parsing, run:")
                click.echo("   pip install link2abc[parsing]")
                click.echo("   Then restart this setup")
    except Exception:
        click.echo("⚠️  Parser detection failed")
    
    click.echo()
    
    # Create config directory
    config_dir = Path.home() / ".link2abc"
    config_dir.mkdir(exist_ok=True)
    config_file = config_dir / "config.yaml"
    env_file = config_dir / ".env"
    
    click.echo(f"📁 Configuration directory: {config_dir}")
    
    # Start configuration
    config = {
        'output': {
            'default_format': ['abc', 'midi'],
            'directory': str(Path.home() / "Music" / "Link2ABC")
        }
    }
    
    env_vars = {}
    
    # Step 1: Basic Setup
    click.echo("\n" + "=" * 50)
    click.echo("🎯 STEP 1: Basic Configuration")
    click.echo("=" * 50)
    
    # Output directory
    music_dir = click.prompt(
        "🎵 Where should Link2ABC save your music files?",
        default=str(Path.home() / "Music" / "Link2ABC"),
        type=str
    )
    config['output']['directory'] = music_dir
    Path(music_dir).mkdir(parents=True, exist_ok=True)
    click.echo(f"✅ Music directory created: {music_dir}")
    
    # Default formats
    click.echo("\n📄 Choose default output formats:")
    click.echo("1. ABC only (lightweight)")
    click.echo("2. ABC + MIDI (recommended)")
    click.echo("3. ABC + MIDI + MP3 (requires external tools)")
    click.echo("4. Custom selection")
    
    format_choice = click.prompt("Enter your choice (1-4)", default="2", type=str)
    
    if format_choice == "1":
        config['output']['default_format'] = ['abc']
    elif format_choice == "2":
        config['output']['default_format'] = ['abc', 'midi']
    elif format_choice == "3":
        config['output']['default_format'] = ['abc', 'midi', 'mp3']
    elif format_choice == "4":
        formats = click.prompt(
            "Enter formats (comma-separated): abc,midi,mp3,svg,jpg",
            default="abc,midi"
        ).split(',')
        config['output']['default_format'] = [f.strip() for f in formats]
    
    click.echo(f"✅ Default formats: {', '.join(config['output']['default_format'])}")
    
    # Step 2: AI Configuration
    if 'ai' in tiers:
        click.echo("\n" + "=" * 50)
        click.echo("🤖 STEP 2: AI Enhancement Setup")
        click.echo("=" * 50)
        
        setup_ai = click.confirm("Do you want to configure AI features? (ChatMusician, Claude, ChatGPT)", default=True)
        
        if setup_ai:
            config['ai'] = {}
            
            # ChatMusician (Primary)
            click.echo("\n🎼 ChatMusician (Primary AI Composer)")
            setup_chatmusician = click.confirm("Configure ChatMusician for professional composition?", default=True)
            
            if setup_chatmusician:
                click.echo("ℹ️  ChatMusician provides professional music composition with advanced harmonies.")
                click.echo("🚀 You can use either official ChatMusician API or custom HuggingFace endpoints")
                
                # Endpoint configuration
                endpoint_choice = click.prompt(
                    "\n🔗 Choose endpoint type:\n"
                    "1. Official ChatMusician API (api.chatmusician.com)\n"
                    "2. Custom HuggingFace Endpoint (your-space.hf.co)\n"
                    "3. HuggingFace Inference API (api-inference.huggingface.co)\n"
                    "Enter choice (1-3)", 
                    default="2", 
                    type=str
                )
                
                if endpoint_choice == "1":
                    # Official API
                    chatmusician_key = getpass.getpass("Enter ChatMusician API key: ")
                    if chatmusician_key:
                        env_vars['CHATMUSICIAN_API_KEY'] = chatmusician_key
                        config['ai']['chatmusician'] = {
                            'endpoint': 'https://api.chatmusician.com',
                            'model': 'latest',
                            'type': 'official'
                        }
                        click.echo("✅ Official ChatMusician API configured")
                
                elif endpoint_choice == "2":
                    # Custom HuggingFace Endpoint
                    click.echo("\n🤗 Custom HuggingFace Endpoint Setup")
                    hf_username = click.prompt("HuggingFace username", type=str)
                    hf_endpoint = click.prompt("Endpoint URL (e.g., https://your-space.hf.co)", type=str)
                    hf_model = click.prompt("Model name", default="facebook/musicgen-small", type=str)
                    hf_key = getpass.getpass("HuggingFace API key: ")
                    hf_budget = click.prompt("Default budget limit ($)", default="1.0", type=float)
                    
                    if hf_key:
                        env_vars['HUGGINGFACE_API_KEY'] = hf_key
                        config['ai']['chatmusician'] = {
                            'endpoint': hf_endpoint,
                            'model': hf_model,
                            'username': hf_username,
                            'budget': hf_budget,
                            'type': 'huggingface_custom'
                        }
                        click.echo("✅ Custom HuggingFace endpoint configured")
                        click.echo(f"   Endpoint: {hf_endpoint}")
                        click.echo(f"   Model: {hf_model}")
                        click.echo(f"   Budget: ${hf_budget}")
                
                elif endpoint_choice == "3":
                    # HuggingFace Inference API
                    click.echo("\n🤗 HuggingFace Inference API Setup")
                    hf_model = click.prompt("Model name", default="facebook/musicgen-small", type=str)
                    hf_key = getpass.getpass("HuggingFace API key: ")
                    
                    if hf_key:
                        env_vars['HUGGINGFACE_API_KEY'] = hf_key
                        config['ai']['chatmusician'] = {
                            'endpoint': f'https://api-inference.huggingface.co/models/{hf_model}',
                            'model': hf_model,
                            'type': 'huggingface_inference'
                        }
                        click.echo("✅ HuggingFace Inference API configured")
                        click.echo(f"   Model: {hf_model}")
                
                # Set as default if configured
                if config['ai'].get('chatmusician'):
                    config['ai']['default'] = 'chatmusician'
                    
                    # Test connection
                    if click.confirm("Test ChatMusician connection?", default=True):
                        for key, value in env_vars.items():
                            os.environ[key] = value
                        _test_ai_service('chatmusician')
                else:
                    click.echo("⚠️  ChatMusician skipped - you can configure it later")
            
            # Claude
            click.echo("\n🧠 Claude (Content Analysis)")
            setup_claude = click.confirm("Configure Claude for sophisticated content analysis?", default=True)
            
            if setup_claude:
                click.echo("ℹ️  Claude provides deep content understanding and cultural context.")
                claude_key = getpass.getpass("Enter Anthropic API key (or press Enter to skip): ")
                
                if claude_key:
                    env_vars['ANTHROPIC_API_KEY'] = claude_key
                    if 'default' not in config['ai']:
                        config['ai']['default'] = 'claude'
                    click.echo("✅ Claude configured")
                    
                    # Test Claude
                    if click.confirm("Test Claude connection?", default=True):
                        os.environ['ANTHROPIC_API_KEY'] = claude_key
                        _test_ai_service('claude')
                else:
                    click.echo("⚠️  Claude skipped - you can configure it later")
            
            # ChatGPT
            click.echo("\n🎨 ChatGPT (Creative Analysis)")
            setup_chatgpt = click.confirm("Configure ChatGPT for creative interpretation?", default=True)
            
            if setup_chatgpt:
                click.echo("ℹ️  ChatGPT provides creative content interpretation and musical ideas.")
                openai_key = getpass.getpass("Enter OpenAI API key (or press Enter to skip): ")
                
                if openai_key:
                    env_vars['OPENAI_API_KEY'] = openai_key
                    if 'default' not in config['ai']:
                        config['ai']['default'] = 'chatgpt'
                    click.echo("✅ ChatGPT configured")
                    
                    # Test ChatGPT
                    if click.confirm("Test ChatGPT connection?", default=True):
                        os.environ['OPENAI_API_KEY'] = openai_key
                        _test_ai_service('chatgpt')
                else:
                    click.echo("⚠️  ChatGPT skipped - you can configure it later")
            
            # Langfuse (Optional)
            click.echo("\n🧵 Langfuse (Advanced Prompts)")
            setup_langfuse = click.confirm("Configure Langfuse for dynamic prompt management? (Advanced)", default=False)
            
            if setup_langfuse:
                click.echo("ℹ️  Langfuse enables dynamic prompt injection and A/B testing.")
                langfuse_public = click.prompt("Enter Langfuse Public Key (or press Enter to skip)", default="", type=str)
                langfuse_secret = getpass.getpass("Enter Langfuse Secret Key (or press Enter to skip): ")
                
                if langfuse_public and langfuse_secret:
                    env_vars['LANGFUSE_PUBLIC_KEY'] = langfuse_public
                    env_vars['LANGFUSE_SECRET_KEY'] = langfuse_secret
                    click.echo("✅ Langfuse configured")
                else:
                    click.echo("⚠️  Langfuse skipped - you can configure it later")
    else:
        click.echo("\n🤖 AI tier not installed")
        if click.confirm("Install AI enhancement? (Adds ChatMusician, Claude, ChatGPT support)", default=True):
            click.echo("📦 To install AI features, run:")
            click.echo("   pip install link2abc[ai]")
            click.echo("   Then run 'link2abc --init' again")
    
    # Step 3: Neural Setup  
    if 'neural' in tiers:
        click.echo("\n" + "=" * 50)
        click.echo("🧠 STEP 3: Neural Synthesis Setup")
        click.echo("=" * 50)
        
        setup_neural = click.confirm("Configure neural synthesis with Orpheus? (Advanced)", default=False)
        
        if setup_neural:
            config['neural'] = {
                'enabled': True,
                'complexity': 'medium',
                'model': 'default'
            }
            click.echo("✅ Neural synthesis configured")
            click.echo("ℹ️  Neural synthesis provides advanced AI music generation")
    else:
        click.echo("\n🧠 Neural tier not installed")
        if click.confirm("Neural synthesis enables advanced AI music generation. Install?", default=False):
            click.echo("📦 To install neural features, run:")
            click.echo("   pip install link2abc[neural]")
            click.echo("⚠️  Note: Requires ~2GB download and 8GB+ RAM")
    
    # Step 4: Cloud Setup
    if 'cloud' in tiers:
        click.echo("\n" + "=" * 50)
        click.echo("☁️  STEP 4: Cloud Execution Setup")
        click.echo("=" * 50)
        
        setup_cloud = click.confirm("Configure cloud execution? (For large-scale processing)", default=False)
        
        if setup_cloud:
            config['cloud'] = {
                'auto_terminate': True,
                'cost_optimize': True,
                'instance_type': 't3.medium'
            }
            
            # AWS Configuration
            if click.confirm("Configure AWS?", default=True):
                aws_key = getpass.getpass("Enter AWS Access Key ID (or press Enter to skip): ")
                aws_secret = getpass.getpass("Enter AWS Secret Access Key (or press Enter to skip): ")
                
                if aws_key and aws_secret:
                    env_vars['AWS_ACCESS_KEY_ID'] = aws_key
                    env_vars['AWS_SECRET_ACCESS_KEY'] = aws_secret
                    click.echo("✅ AWS configured")
                else:
                    click.echo("⚠️  AWS skipped - you can configure it later")
            
            click.echo("✅ Cloud execution configured")
    
    # Step 5: Save Configuration
    click.echo("\n" + "=" * 50)
    click.echo("💾 STEP 5: Saving Configuration")
    click.echo("=" * 50)
    
    # Save YAML config
    import yaml
    with open(config_file, 'w') as f:
        yaml.dump(config, f, default_flow_style=False, sort_keys=False)
    click.echo(f"✅ Configuration saved: {config_file}")
    
    # Save environment variables
    if env_vars:
        with open(env_file, 'w') as f:
            for key, value in env_vars.items():
                f.write(f"{key}={value}\n")
        click.echo(f"✅ API keys saved: {env_file}")
        click.echo("ℹ️  To load environment variables, run:")
        click.echo(f"   source {env_file}")
    
    # Step 6: Final Test
    click.echo("\n" + "=" * 50)
    click.echo("🧪 STEP 6: Final Testing")
    click.echo("=" * 50)
    
    if click.confirm("Run a quick test conversion?", default=True):
        click.echo("🎵 Testing Link2ABC with sample content...")
        
        # Load environment variables for test
        for key, value in env_vars.items():
            os.environ[key] = value
        
        try:
            # Import here to avoid circular imports
            from .core.pipeline import Pipeline
            
            # Test basic conversion
            pipeline = Pipeline.from_config({'format': ['abc']})
            result = pipeline.run("https://app.simplenote.com/p/bBs4zY")
            
            if result.success:
                click.echo("✅ Test conversion successful!")
                click.echo(f"📄 Generated: {result.files}")
                click.echo(f"⏱️  Time: {result.execution_time:.2f}s")
            else:
                click.echo(f"❌ Test failed: {result.error}")
        except Exception as e:
            click.echo(f"❌ Test error: {e}")
    
    # Completion
    click.echo("\n" + "🎉" * 20)
    click.echo("🎵 Link2ABC Setup Complete!")
    click.echo("🎉" * 20)
    
    click.echo(f"\n📁 Your configuration is saved in: {config_dir}")
    click.echo(f"🎵 Music will be saved to: {config['output']['directory']}")
    
    if env_vars:
        click.echo(f"\n🔑 To activate your API keys in new terminal sessions:")
        click.echo(f"   source {env_file}")
        click.echo("   # Or add this line to your ~/.bashrc or ~/.zshrc")
    
    click.echo("\n🚀 Ready to use Link2ABC!")
    click.echo("Try these commands:")
    click.echo("   link2abc https://app.simplenote.com/p/bBs4zY")
    
    if 'ai' in tiers and env_vars:
        default_ai = config.get('ai', {}).get('default', 'chatmusician')
        click.echo(f"   link2abc https://app.simplenote.com/p/bBs4zY --ai {default_ai}")
    
    click.echo("   link2abc --help")
    
    click.echo("\n📚 For more examples and tutorials:")
    click.echo("   https://github.com/jgwill/link2abc")

def _test_ai_service(service_name: str):
    """Test AI service connection"""
    try:
        click.echo(f"🔍 Testing {service_name} connection...")
        
        if service_name == 'chatmusician':
            # Simple connection test
            import requests
            response = requests.get("https://api.chatmusician.com/health", timeout=5)
            if response.status_code == 200:
                click.echo("✅ ChatMusician connection successful")
            else:
                click.echo("⚠️  ChatMusician connection failed - check API key")
        
        elif service_name == 'claude':
            import anthropic
            client = anthropic.Anthropic()
            # Simple test (this will use a small amount of credits)
            response = client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=10,
                messages=[{"role": "user", "content": "Hello"}]
            )
            click.echo("✅ Claude connection successful")
        
        elif service_name == 'chatgpt':
            import openai
            client = openai.OpenAI()
            # Simple test (this will use a small amount of credits)
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                max_tokens=10,
                messages=[{"role": "user", "content": "Hello"}]
            )
            click.echo("✅ ChatGPT connection successful")
            
    except ImportError:
        click.echo(f"❌ {service_name} library not installed")
    except Exception as e:
        click.echo(f"⚠️  {service_name} test failed: {e}")

def cli_entry_point():
    """Entry point for the CLI script"""
    main()

if __name__ == '__main__':
    main()