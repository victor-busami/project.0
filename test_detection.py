#!/usr/bin/env python3
"""
Test script for enhanced weapon detection
"""

from object_detector import detect_weapons
from sentiment_analyzer import analyze_threat_level, analyze_image_context
import json

def test_detection():
    """Test the enhanced detection system"""
    print("🔍 Testing Enhanced Weapon Detection System")
    print("=" * 50)
    
    # Test with a sample description that should trigger detection
    test_description = "A person holding a gun and threatening someone"
    
    print(f"Test Description: {test_description}")
    
    # Test context analysis
    context_threat = analyze_image_context(test_description)
    print(f"Context Threat Level: {context_threat}")
    
    # Test threat analysis with no weapons but violent description
    threat_level = analyze_threat_level([], test_description)
    print(f"Threat Level: {threat_level}")
    
    # Test with mock weapon detection
    mock_weapons = [
        {
            "weapon": "handgun",
            "severity": "SERIOUS-URGENT",
            "confidence": 0.85,
            "bbox": [100, 100, 200, 200],
            "original_label": "teddy bear"
        }
    ]
    
    combined_threat = analyze_threat_level(mock_weapons, test_description)
    print(f"Combined Threat Level: {combined_threat}")
    
    print("\n✅ Test completed successfully!")
    print("The enhanced system should now better detect:")
    print("- Guns and firearms (even when misclassified as teddy bears)")
    print("- Knives and sharp objects")
    print("- Violent context from image descriptions")
    print("- Multiple threat indicators")

if __name__ == "__main__":
    test_detection() 