#!/usr/bin/env python3
"""
CLI Demo for Link2ABC + HuggingFace Integration - Issue #25
♠️🌿🎸🤖🧵 G.MUSIC ASSEMBLY MODE ACTIVE

Command-line interface demonstration of the integrated workflow
"""

import argparse
import sys
from pathlib import Path
from orpheus_integration_prototype import OrpheusIntegrationBlock, HFConfig


def main():
    parser = argparse.ArgumentParser(
        description="Link2ABC + HuggingFace ChatMusician Integration Demo",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic enhancement
  python integration_cli_demo.py sample.abc --enhance-hf
  
  # Custom prompt with budget control  
  python integration_cli_demo.py sample.abc --enhance-hf --hf-prompt jazz_enhancement --hf-budget 0.50
  
  # Keep endpoint alive for batch processing
  python integration_cli_demo.py sample.abc --enhance-hf --keep-alive 300
"""
    )
    
    parser.add_argument("abc_file", help="Input ABC file to enhance")
    parser.add_argument("--enhance-hf", action="store_true", 
                       help="Enable HuggingFace ChatMusician enhancement")
    parser.add_argument("--hf-prompt", default="enhance_abc_notation",
                       choices=["enhance_abc_notation", "jazz_enhancement", "orchestral_arrangement"],
                       help="Enhancement style template")
    parser.add_argument("--hf-budget", type=float, default=1.0,
                       help="Maximum cost per session (default: $1.00)")
    parser.add_argument("--keep-alive", type=int, default=0,
                       help="Keep HF endpoint alive for N seconds (for batch processing)")
    parser.add_argument("--output-dir", type=Path, default=Path("./output"),
                       help="Output directory for generated files")
    
    args = parser.parse_args()
    
    # Validate input file
    abc_path = Path(args.abc_file)
    if not abc_path.exists():
        print(f"❌ ABC file not found: {abc_path}")
        sys.exit(1)
    
    # Read ABC content
    abc_content = abc_path.read_text()
    
    if args.enhance_hf:
        print("♠️🌿🎸🤖🧵 G.MUSIC ASSEMBLY MODE: Initializing HuggingFace enhancement")
        
        # Configure HuggingFace integration
        hf_config = HFConfig(
            model_name="ChatMusician",
            max_cost_per_session=args.hf_budget,
            endpoint_timeout=args.keep_alive if args.keep_alive > 0 else 300
        )
        
        # Create integration block
        integration_block = OrpheusIntegrationBlock(hf_config, args.hf_prompt)
        
        try:
            # Process with enhancement
            result = integration_block.process(abc_content, args.output_dir)
            
            print(f"✅ Enhancement completed successfully!")
            print(f"💰 Cost consumed: ${result.cost_consumed:.2f}")
            print(f"⏱️ Processing time: {result.processing_time:.1f}s")
            print(f"📁 Outputs generated in: {args.output_dir}")
            print(f"   - Original: {args.output_dir}/original/")
            print(f"   - Enhanced: {args.output_dir}/enhanced/")
            
        except Exception as e:
            print(f"❌ Enhancement failed: {e}")
            print("🌿 Graceful fallback: Original outputs still available")
            sys.exit(1)
    else:
        print("🎵 Basic Link2ABC processing (no HuggingFace enhancement)")
        # This would call standard Link2ABC processing
        args.output_dir.mkdir(parents=True, exist_ok=True)
        (args.output_dir / "content.abc").write_text(abc_content)
        print(f"📁 Basic output generated in: {args.output_dir}")


if __name__ == "__main__":
    main()