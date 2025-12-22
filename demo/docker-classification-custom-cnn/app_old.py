from flask import Flask, request, send_file, jsonify, Response
import torch
import os
from PIL import Image
from torchvision import transforms
from torch.utils.data import Dataset, DataLoader
import numpy as np
from pathlib import Path
import torch.nn as nn
import torch.optim as optim
import io

print("resizing and normalizing images...")
transform = transforms.Compose([
    transforms.Resize((128,128)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.5, 0.5, 0.5], std=[0.5, 0.5, 0.5])]
)
class ImageDataset(Dataset):
    def __init__(self, image_dir, transform=None):
        self.image_dir = image_dir
        self.image_paths = []
        self.labels = []
        self.class_name = {}
        self.transform = transform
        for label, class_dir in enumerate(os.listdir(image_dir)):
            self.class_name[label] = class_dir
            class_path = os.path.join(image_dir, class_dir)
        for img_name in os.listdir(class_path):
            self.image_paths.append(os.path.join(class_path, img_name))
            self.labels.append(label)	
    def __len__(self):
            return len(self.image_paths)
    def __getitem__(self, idx):
        img_path = self.image_paths[idx]
        image = Image.open(img_path).convert("RGB")
        label = self.labels[idx]
        if self.transform:
            image = self.transform(image)
        return image, label



file_path = Path("/app/cnn_model.pth")
train_image_dir = '/app/Classification_dataset_v3/images/train'
test_image_dir = '/app/Classification_dataset_v3/images/test'

train_image_dataset = ImageDataset(image_dir=train_image_dir, transform=transform)
test_image_dataset = ImageDataset(image_dir=test_image_dir, transform=transform)

train_image_loader = DataLoader(dataset=train_image_dataset, batch_size=32, shuffle=True)
test_image_loader = DataLoader(dataset=test_image_dataset, batch_size=32, shuffle=True)
class CustomCnnModel(nn.Module):
    def __init__(self,input_dim, num_classes):
        super(CustomCnnModel, self).__init__()
        self.input_dim = input_dim
        self.num_classes = num_classes

        self.conv_layers = nn.Sequential(
            # C1
            nn.Conv2d(3, 32, kernel_size=3, stride=1, padding=1),
            # 128x128x3 --> 3x3x3x32 --> wxhx32
            nn.BatchNorm2d(32),
            nn.ReLU(),
            nn.MaxPool2d(kernel_size=2, stride=2),

            # C2
            nn.Conv2d(32, 64, kernel_size=3, stride=1, padding=1),
            nn.BatchNorm2d(64),
            nn.ReLU(),
            nn.MaxPool2d(kernel_size=2, stride=2),

            # C3
            nn.Conv2d(64, 128, kernel_size=3, stride=1, padding=1),
            nn.BatchNorm2d(128),
            nn.ReLU(),
            nn.MaxPool2d(kernel_size=2, stride=2),

            # C4
            nn.Conv2d(128, 256, kernel_size=3, stride=1, padding=1),
            nn.BatchNorm2d(256),
            nn.ReLU(),
            nn.MaxPool2d(kernel_size=2, stride=2)
        )

        self._to_linear = None
        self._get_conv_output(self.input_dim)

        self.fc_layers = nn.Sequential(
            nn.Linear(self._to_linear, 512),
            nn.ReLU(),
            # nn.Dropout(0.2)
            nn.Linear(512, 128),
            nn.ReLU(),
            nn.Linear(128, self.num_classes),
        )

        # 256 x 12 x 12

    def _get_conv_output(self, input_dim=128):
        with torch.no_grad():
            dummy_input = torch.zeros(1,3, input_dim, input_dim)
            output = self.conv_layers(dummy_input)
            self._to_linear = output.view(1, -1).size(1)
    def forward(self,x):
        x = self.conv_layers(x)
        x = x.view(x.size(0), -1)
        x = self.fc_layers(x)
        return x
    
if file_path.exists():
    print("CNN File exists")
    device = torch.device('cpu')
    model = CustomCnnModel(input_dim=128, num_classes=3).to(device)
else:
    print("Started reading images...")
    image_dir = '/app/Classification_dataset_v3/images/train'
    for label, class_dir in enumerate(os.listdir(image_dir)):
      print(label, class_dir)
    for images,labels in train_image_loader:
        print(images.shape, labels.shape)
        break
	
    print(train_image_dataset.class_name)
    print(test_image_dataset.class_name)
	
        
    # Initialize Model
    device = torch.device('cpu')
    model = CustomCnnModel(input_dim=128, num_classes=3).to(device)
    print("model for images...")
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(),lr=0.001)
    
    print("Started training cnn")
    # Training loop
    epochs = 40
    for epoch in range(epochs):
        model.train()
        running_loss = 0.0
        for images, labels in train_image_loader:
            images,labels = images.to(device), labels.to(device)
            optimizer.zero_grad()
            outputs = model(images)    
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()
            running_loss+=loss.item()
        print(f"Epoch {epoch+1}/{epochs}, Loss : {running_loss/len(train_image_loader)}")
	
    torch.save(model.state_dict(), "cnn_model.pth")


# Evaluate model

model.eval()
correct = 0
total = 0

with torch.no_grad():
  for images, labels in test_image_loader:
    images,labels = images.to(device), labels.to(device)
    outputs = model(images)
    _, predicted = torch.max(outputs, 1)
    total += labels.size(0)
    correct += (predicted == labels).sum().item()

print(f"Test accuracy is :{100* correct / total:.2f}%")


import cv2

class ImageClassifier:
  def __init__(self, model_path, class_names):
    self.device = torch.device('cpu')
    self.model = CustomCnnModel(input_dim=128, num_classes=3).to(self.device)
    self.model.load_state_dict(torch.load(model_path, map_location=self.device))
    self.model.eval()
    self.class_names = class_names
    self.transform = transforms.Compose([
      transforms.Resize((128,128)),
      transforms.ToTensor(),
      transforms.Normalize(mean=[0.5, 0.5, 0.5], std=[0.5, 0.5, 0.5])]
    )

  def predict(self, image_pil):
    input_tensor = self.transform(image_pil).unsqueeze(0).to(self.device)
    with torch.no_grad():
      output = self.model(input_tensor)
      _, predicted = torch.max(output, 1)
    label = self.class_names[predicted.item()]
    return label

classfier = ImageClassifier("/app/cnn_model.pth", train_image_dataset.class_name )

app = Flask(__name__)

@app.post("/classify")
def classify():
    if "image" not in request.files:
        return jsonify({"error": "No image uploaded"}), 400

    # Read image
    file = request.files["image"]
    image = Image.open(file.stream).convert("RGB")
    
    
    
    label = classfier.predict(image)
    print(f"Predicted class is : {label}")
    annotated_img = np.array(image)
    # Draw classification label
    cv2.putText(
        annotated_img,
        f"Class: {label}",
        (20, 40),
        cv2.FONT_HERSHEY_SIMPLEX,
        1,
        (0, 255, 0),
        2
    )
    
    # Convert to bytes
    annotated_pil = Image.fromarray(annotated_img)
    img_io = io.BytesIO()
    annotated_pil.save(img_io, format="JPEG")
    img_io.seek(0)

    return send_file(img_io, mimetype="image/jpeg")
# ================================
# Server
# ================================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8005)