# ==========================================
# 📄 object_detector.py
# ==========================================
from transformers import DetrImageProcessor, DetrForObjectDetection
from PIL import Image
import torch
import io

# Initialize model and processor
processor = DetrImageProcessor.from_pretrained("facebook/detr-resnet-50")
model = DetrForObjectDetection.from_pretrained("facebook/detr-resnet-50")

# Custom class mapping (COCO class index -> weapon category)
WEAPON_CLASSES = {
    44: "Bottle", 45: "Wine glass", 47: "Knife", 48: "Spoon", 49: "Fork",
    67: "Cell phone", 68: "Microwave", 75: "Remote", 85: "Toilet"
}

SEVERITY_MAP = {
    "Gun": "SERIOUS-URGENT",
    "Pistol": "SERIOUS-URGENT",
    "Knife": "SERIOUS",
    "Machete": "SERIOUS",
    "Stick": "LOW",
    "Stone": "LOW"
}

def detect_weapons(image_file):
    """Detect weapons in image and classify their severity"""
    image = Image.open(image_file).convert("RGB")
    inputs = processor(images=image, return_tensors="pt")
    outputs = model(**inputs)
    target_sizes = torch.tensor([image.size[::-1]])
    results = processor.post_process_object_detection(
        outputs, 
        target_sizes=target_sizes, 
        threshold=0.7
    )[0]

    detected = []
    for score, label, box in zip(results["scores"], results["labels"], results["boxes"]):
        label_name = model.config.id2label[label.item()]
        if label_name in WEAPON_CLASSES.values():
            severity = SEVERITY_MAP.get(label_name, "LOW")
            detected.append({
                "weapon": label_name,
                "severity": severity,
                "confidence": float(score.item()),
                "bbox": box.tolist()
            })
    return detected