#!/usr/bin/env python3
"""
Enhanced Document Analysis Example with Chunking
"""

import sys
import os
import json
from pathlib import Path

# Add src to path for local development
src_path = os.path.join(os.path.dirname(__file__), '..', 'src')
sys.path.insert(0, src_path)

try:
    from core.analyzer import DocumentAnalyzer
    from core.chunking import ChunkingOrchestrator
except ImportError as e:
    print(f"Error importing modules: {e}")
    sys.exit(1)

def main():
    if len(sys.argv) < 2:
        print("Usage: python enhanced_analysis.py <document_path> [strategy]")
        print("Strategies: auto, text, structured, code")
        sys.exit(1)
    
    document_path = sys.argv[1]
    strategy = sys.argv[2] if len(sys.argv) > 2 else 'auto'
    
    if not os.path.exists(document_path):
        print(f"Error: File not found: {document_path}")
        sys.exit(1)
    
    try:
        # Initialize analyzer and chunking orchestrator
        analyzer = DocumentAnalyzer()
        orchestrator = ChunkingOrchestrator()
        
        print(f"🚀 Enhanced Analysis: {Path(document_path).name}")
        print("=" * 60)
        
        # Step 1: Analyze document
        print("🔍 Step 1: Document Analysis...")
        result = analyzer.analyze_document(document_path)
        
        if 'error' in result:
            print(f"❌ Error: {result['error']}")
            return
        
        print(f"✅ Analysis completed")
        print(f"   Document Type: {result['document_type'].type_name}")
        print(f"   Confidence: {result['confidence']:.2f}")
        print(f"   Handler: {result['handler_used']}")
        
        # Step 2: Chunking
        print(f"\n📦 Step 2: Document Chunking (strategy: {strategy})...")
        
        # Convert analysis format for chunking
        chunking_analysis = {
            'document_type': {
                'type_name': result['document_type'].type_name,
                'confidence': result['document_type'].confidence,
                'category': result['document_type'].category
            },
            'analysis': result['analysis']
        }
        
        chunks = orchestrator.chunk_document(
            document_path,
            chunking_analysis,
            strategy=strategy
        )
        
        print(f"✅ Chunking completed")
        print(f"   Total chunks: {len(chunks)}")
        print(f"   Strategy used: {strategy}")
        
        # Step 3: Display results
        print(f"\n📊 Analysis Results:")
        print(f"   File size: {result['file_size']:,} bytes")
        
        if hasattr(result['document_type'], 'language') and result['document_type'].language:
            print(f"   Language: {result['document_type'].language}")
        
        # Key findings
        findings = result['analysis'].key_findings
        print(f"\n📋 Key Findings:")
        for key, value in findings.items():
            if isinstance(value, (int, float, str)) and len(str(value)) < 100:
                print(f"   {key}: {value}")
        
        # Quality metrics
        if result['analysis'].quality_metrics:
            print(f"\n📈 Quality Metrics:")
            for metric, score in result['analysis'].quality_metrics.items():
                print(f"   {metric}: {score:.2f}")
        
        # Chunk statistics
        total_tokens = sum(chunk.token_count or 0 for chunk in chunks)
        avg_tokens = total_tokens / len(chunks) if chunks else 0
        
        print(f"\n📦 Chunking Results:")
        print(f"   Total chunks: {len(chunks)}")
        print(f"   Total tokens: {total_tokens:,}")
        print(f"   Average tokens per chunk: {avg_tokens:.1f}")
        
        # Show sample chunks
        print(f"\n📄 Sample Chunks:")
        for i, chunk in enumerate(chunks[:3]):
            print(f"   Chunk {i+1}: {chunk.chunk_id} ({chunk.token_count or 0} tokens)")
            preview = chunk.content[:100].replace('\n', ' ')
            print(f"      {preview}{'...' if len(chunk.content) > 100 else ''}")
        
        if len(chunks) > 3:
            print(f"   ... and {len(chunks) - 3} more chunks")
        
        # AI use cases
        print(f"\n🤖 AI Use Cases ({len(result['analysis'].ai_use_cases)} total):")
        for i, use_case in enumerate(result['analysis'].ai_use_cases[:5], 1):
            print(f"   {i}. {use_case}")
        
        print(f"\n🎉 Enhanced analysis completed successfully!")
        print(f"This document is ready for AI/ML processing with {len(chunks)} optimized chunks.")
        
    except Exception as e:
        print(f"❌ Error during enhanced analysis: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()