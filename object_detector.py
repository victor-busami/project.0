from transformers import DetrImageProcessor, DetrForObjectDetection, YolosImageProcessor, YolosForObjectDetection
from PIL import Image
import torch
import io
import numpy as np

# Initialize multiple models for better detection
try:
    # Try to use YOLO model which is better for weapon detection
    processor = YolosImageProcessor.from_pretrained("hustvl/yolos-tiny")
    model = YolosForObjectDetection.from_pretrained("hustvl/yolos-tiny")
    print("Using YOLO model for detection")
except:
    # Fallback to DETR
    processor = DetrImageProcessor.from_pretrained("facebook/detr-resnet-50")
    model = DetrForObjectDetection.from_pretrained("facebook/detr-resnet-50")
    print("Using DETR model for detection")

# Comprehensive weapon and dangerous object mappings
WEAPON_CLASSES = {
    # COCO dataset IDs
    43: "knife",
    44: "bottle", 
    45: "wine glass",
    46: "cup",
    47: "fork",
    48: "knife",
    49: "spoon",
    76: "scissors",
    77: "handgun",  # Often misclassified as teddy bear
    78: "hair drier",
    79: "sharp object",
    
    # Additional weapon-like objects
    1: "person",  # Check for threatening poses
    2: "bicycle",
    3: "car",
    4: "motorcycle",
    5: "airplane",
    6: "bus",
    7: "train",
    8: "truck",
    9: "boat",
    10: "traffic light",
    11: "fire hydrant",
    12: "stop sign",
    13: "parking meter",
    14: "bench",
    15: "bird",
    16: "cat",
    17: "dog",
    18: "horse",
    19: "sheep",
    20: "cow",
    21: "elephant",
    22: "bear",
    23: "zebra",
    24: "giraffe",
    25: "backpack",
    26: "umbrella",
    27: "handbag",
    28: "tie",
    29: "suitcase",
    30: "frisbee",
    31: "skis",
    32: "snowboard",
    33: "sports ball",
    34: "kite",
    35: "baseball bat",  # Potential weapon
    36: "baseball glove",
    37: "skateboard",
    38: "surfboard",
    39: "tennis racket",
    40: "bottle",
    41: "wine glass",
    42: "cup",
    43: "fork",
    44: "knife",
    45: "spoon",
    46: "bowl",
    47: "banana",
    48: "apple",
    49: "sandwich",
    50: "orange",
    51: "broccoli",
    52: "carrot",
    53: "hot dog",
    54: "pizza",
    55: "donut",
    56: "cake",
    57: "chair",
    58: "couch",
    59: "potted plant",
    60: "bed",
    61: "dining table",
    62: "toilet",
    63: "tv",
    64: "laptop",
    65: "mouse",
    66: "remote",
    67: "keyboard",
    68: "cell phone",
    69: "microwave",
    70: "oven",
    71: "toaster",
    72: "sink",
    73: "refrigerator",
    74: "book",
    75: "clock",
    76: "vase",
    77: "scissors",
    78: "teddy bear",
    79: "hair drier",
    80: "toothbrush"
}

# Enhanced severity mapping
SEVERITY_MAP = {
    "knife": "SERIOUS-URGENT",
    "handgun": "SERIOUS-URGENT", 
    "gun": "SERIOUS-URGENT",
    "pistol": "SERIOUS-URGENT",
    "rifle": "SERIOUS-URGENT",
    "weapon": "SERIOUS-URGENT",
    "baseball bat": "SERIOUS",
    "bottle": "MEDIUM",
    "scissors": "MEDIUM",
    "sharp object": "MEDIUM",
    "knife-like": "SERIOUS",
    "wine glass": "LOW",
    "fork": "LOW",
    "person": "LOW",  # Context dependent
    "car": "LOW",
    "motorcycle": "LOW"
}

# Weapon keywords for text-based detection
WEAPON_KEYWORDS = [
    "knife", "gun", "pistol", "rifle", "weapon", "sword", "dagger", "blade",
    "firearm", "handgun", "shotgun", "machine gun", "rifle", "pistol",
    "baseball bat", "bat", "stick", "pipe", "hammer", "axe", "machete",
    "scissors", "razor", "blade", "sharp", "pointed", "dangerous"
]

def detect_weapons(image_file):
    """Enhanced weapon detection with multiple strategies"""
    image = Image.open(image_file).convert("RGB")
    inputs = processor(images=image, return_tensors="pt")
    outputs = model(**inputs)
    target_sizes = torch.tensor([image.size[::-1]])
    results = processor.post_process_object_detection(
        outputs, 
        target_sizes=target_sizes, 
        threshold=0.3  # Lower threshold for better detection
    )[0]

    # Debug output
    print("\n=== Raw Detections ===")
    for score, label, box in zip(results["scores"], results["labels"], results["boxes"]):
        label_id = label.item()
        label_name = model.config.id2label.get(label_id, f"unknown_{label_id}")
        print(f"- {label_name} (ID: {label_id}) with confidence {score.item():.2f}")

    detected = []
    for score, label, box in zip(results["scores"], results["labels"], results["boxes"]):
        label_id = label.item()
        label_name = model.config.id2label.get(label_id, f"unknown_{label_id}").lower()
        confidence = float(score.item())
        
        # Enhanced weapon detection logic
        weapon_name = None
        severity = "LOW"
        
        # Check by class ID
        if label_id in WEAPON_CLASSES:
            weapon_name = WEAPON_CLASSES[label_id]
        
        # Check by label name with keyword matching
        if not weapon_name:
            for keyword in WEAPON_KEYWORDS:
                if keyword in label_name:
                    weapon_name = keyword
                    break
        
        # Special handling for common misclassifications
        if not weapon_name:
            if label_id == 77:  # teddy bear - often misclassified guns
                weapon_name = "handgun"
            elif "bear" in label_name and confidence > 0.4:
                weapon_name = "handgun"  # High confidence teddy bear might be gun
            elif "bottle" in label_name and confidence > 0.5:
                weapon_name = "bottle"
            elif "knife" in label_name or "blade" in label_name:
                weapon_name = "knife"
            elif "scissor" in label_name:
                weapon_name = "scissors"
            elif "bat" in label_name:
                weapon_name = "baseball bat"
        
        # Additional context-based detection
        if not weapon_name:
            # Check for threatening objects based on shape and context
            if label_name in ["person", "man", "woman"] and confidence > 0.6:
                # Person detection might indicate threat context
                weapon_name = "person"
            elif any(obj in label_name for obj in ["stick", "pipe", "rod"]) and confidence > 0.4:
                weapon_name = "sharp object"
        
        if weapon_name:
            severity = SEVERITY_MAP.get(weapon_name, "LOW")
            detected.append({
                "weapon": weapon_name,
                "severity": severity,
                "confidence": confidence,
                "bbox": [round(c, 2) for c in box.tolist()],
                "original_label": label_name
            })
    
    # Additional heuristic: if we detect multiple objects, check for weapon-like combinations
    if len(detected) == 0 and len(results["scores"]) > 0:
        # Check for suspicious object combinations
        detected_labels = [model.config.id2label.get(label.item(), "").lower() for label in results["labels"]]
        if "person" in detected_labels and any(obj in detected_labels for obj in ["bottle", "stick", "pipe"]):
            detected.append({
                "weapon": "suspicious object",
                "severity": "MEDIUM",
                "confidence": 0.5,
                "bbox": [0, 0, 100, 100],
                "original_label": "person with object"
            })
    
    print(f"\n=== Filtered Weapons ===")
    for item in detected:
        print(f"- {item['weapon']} ({item['severity']}) conf: {item['confidence']:.2f}")

    # --- Enhancement: Post-process for gun-like objects ---
    gun_keywords = ["gun", "pistol", "rifle", "firearm"]
    gun_like_labels = ["baseball bat", "tennis racket"]
    for score, label, box in zip(results["scores"], results["labels"], results["boxes"]):
        label_name = model.config.id2label.get(label.item(), f"unknown_{label.item()}").lower()
        confidence = float(score.item())
        # Debug print for all detected labels
        print(f"[DEBUG] Detected label: {label_name}, confidence: {confidence:.2f}")
        if any(x in label_name for x in gun_keywords) or label_name in gun_like_labels:
            # Only add if not already detected as a weapon
            if not any(d['original_label'] == label_name for d in detected):
                detected.append({
                    "weapon": "gun",
                    "severity": "SERIOUS-URGENT",
                    "confidence": confidence,
                    "bbox": [round(c, 2) for c in box.tolist()],
                    "original_label": label_name
                })

    # --- Workaround: If no objects detected, check image description for gun/weapon keywords ---
    import streamlit as st
    if len(detected) == 0:
        # Try to get the image description from Streamlit session state
        image_description = st.session_state.get('image_description', '')
        if any(x in image_description.lower() for x in gun_keywords):
            detected.append({
                "weapon": "gun (from description)",
                "severity": "SERIOUS-URGENT",
                "confidence": 1.0,
                "bbox": [],
                "original_label": "description"
            })

    return detected