#!/usr/bin/env python3
"""
Basic Document Analysis Example using Document Analysis Framework
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
except ImportError as e:
    print(f"Error importing DocumentAnalyzer: {e}")
    sys.exit(1)

def main():
    if len(sys.argv) < 2:
        print("Usage: python basic_analysis.py <document_path>")
        sys.exit(1)
    
    document_path = sys.argv[1]
    
    if not os.path.exists(document_path):
        print(f"Error: File not found: {document_path}")
        sys.exit(1)
    
    try:
        # Initialize analyzer
        analyzer = DocumentAnalyzer()
        
        print(f"🔍 Analyzing document: {document_path}")
        print("=" * 60)
        
        # Analyze document
        result = analyzer.analyze_document(document_path)
        
        if 'error' in result:
            print(f"❌ Error: {result['error']}")
            return
        
        # Display results
        print(f"📄 Document Type: {result['document_type'].type_name}")
        print(f"🎯 Confidence: {result['confidence']:.2f}")
        print(f"🔧 Handler Used: {result['handler_used']}")
        print(f"📐 File Size: {result['file_size']:,} bytes")
        
        if hasattr(result['document_type'], 'language') and result['document_type'].language:
            print(f"💻 Language: {result['document_type'].language}")
        
        # Show key findings
        findings = result['analysis'].key_findings
        print(f"\n📊 Key Findings:")
        for key, value in findings.items():
            if isinstance(value, (int, float, str)) and len(str(value)) < 100:
                print(f"  {key}: {value}")
        
        # Show AI use cases
        print(f"\n🤖 AI Use Cases:")
        for i, use_case in enumerate(result['analysis'].ai_use_cases[:5], 1):
            print(f"  {i}. {use_case}")
        
        # Show quality metrics
        if result['analysis'].quality_metrics:
            print(f"\n📈 Quality Metrics:")
            for metric, score in result['analysis'].quality_metrics.items():
                print(f"  {metric}: {score:.2f}")
        
        print(f"\n✅ Analysis completed successfully!")
        
    except Exception as e:
        print(f"❌ Error during analysis: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()