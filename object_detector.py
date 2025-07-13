from transformers import DetrImageProcessor, DetrForObjectDetection
from PIL import Image
import torch
import io

# Initialize model and processor
processor = DetrImageProcessor.from_pretrained("facebook/detr-resnet-50")
model = DetrForObjectDetection.from_pretrained("facebook/detr-resnet-50")

# Correct COCO class IDs for weapons/dangerous objects
WEAPON_CLASSES = {
    43: "knife",
    44: "bottle",
    45: "wine glass",
    46: "cup",
    47: "fork",
    48: "knife",  # Some models detect knives with this ID
    49: "spoon",
    76: "scissors",
    77: "handgun",  # Often misclassified as teddy bear
    78: "hair drier",  # Can look like weapons
    79: "sharp object"  # For toothbrush/small pointed items
}

SEVERITY_MAP = {
    "knife": "SERIOUS",
    "handgun": "SERIOUS-URGENT",
    "bottle": "MEDIUM",
    "scissors": "MEDIUM",
    "wine glass": "LOW",
    "sharp object": "MEDIUM",
    "fork": "LOW"
}

def detect_weapons(image_file):
    """Detect weapons with debug output and improved detection"""
    image = Image.open(image_file).convert("RGB")
    inputs = processor(images=image, return_tensors="pt")
    outputs = model(**inputs)
    target_sizes = torch.tensor([image.size[::-1]])
    results = processor.post_process_object_detection(
        outputs, 
        target_sizes=target_sizes, 
        threshold=0.5  # Lower threshold for better detection
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
        
        # Check both ID and name for weapons
        weapon_name = None
        if label_id in WEAPON_CLASSES:
            weapon_name = WEAPON_CLASSES[label_id]
        elif "knife" in label_name:
            weapon_name = "knife"
        elif "gun" in label_name:
            weapon_name = "handgun"
        elif "scissor" in label_name:
            weapon_name = "scissors"
        elif any(w in label_name for w in ["bottle", "glass", "sharp"]):
            weapon_name = label_name

        if weapon_name:
            detected.append({
                "weapon": weapon_name,
                "severity": SEVERITY_MAP.get(weapon_name, "LOW"),
                "confidence": float(score.item()),
                "bbox": [round(c, 2) for c in box.tolist()]
            })
    
    print(f"\n=== Filtered Weapons ===")
    for item in detected:
        print(f"- {item['weapon']} ({item['severity']}) conf: {item['confidence']:.2f}")
    
    return detected