from ultralytics import YOLO
import os

BASE_DIR = os.path.dirname(__file__)
data_path = os.path.join(BASE_DIR, 'My-First-Project-1', 'data.yaml')

local_weights = os.path.join(BASE_DIR, 'yolov8n.pt')
model = YOLO(local_weights if os.path.exists(local_weights) else 'yolov8n.pt')

results = model.train(
    data=data_path,
    epochs=50,
    imgsz=640,
    batch=16,
    name='yolo_jackets'
)

print("Entrenamiento finalizado. El modelo se guardó en: runs/detect/yolo_jackets/weights/best.pt")