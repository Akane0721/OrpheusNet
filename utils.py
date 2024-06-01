from PIL import Image
import cv2
import numpy as np
import torch
import torch.nn as nn
from torchvision import transforms, models
from CNNmodel import CNN_middle, CNN_meta

Idx_map_0 = {
    0:'(', 1:')', 2:'0', 3:'1', 4:'2', 5:'3', 6:'4', 7:'5', 8:'6', 9:'7', 10:'8', 
    11:'9', 12:'A', 13:'B', 14:'C', 15:'D', 16:'E', 17:'F', 18:'G', 19:'breath', 
    20:'flat', 21:'quarter', 22:'sharp'
}

Idx_map_mid = {
    0:'(', 1:')', 2:'0', 3:'1', 4:'2', 5:'3', 6:'4', 7:'5', 8:'6', 9:'7', 10:'breath', 
    11:'flat', 12:'sharp'
}

Idx_map_met = {
    0:'0', 1:'1', 2:'2', 3:'3', 4:'4', 5:'5', 6:'6', 7:'7', 8:'8', 9:'9', 10:'A', 
    11:'B', 12:'C', 13:'D', 14:'E', 15:'F', 16:'G', 17:'flat', 18:'quarter', 
    19:'sharp'
}

transform1 = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.Grayscale(3),
        transforms.ToTensor(),
        transforms.Normalize((0.1307,0.1307,0.1307), (0.3081,0.3081,0.3081)),
    ])

transform2 = transforms.Compose([
    transforms.Grayscale(num_output_channels=1),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.5],std=[0.5])])

def LoadModel(model_type):
    '''
    model_type = CNN, ResNet, VGG
    '''
    if model_type == "CNN": 
        middle_model = CNN_middle(output_size=13)
        meta_model = CNN_meta(output_size=20)
        middle_model_path = "pths/CNN_middle.pth"
        meta_model_path = "pths/CNN_meta.pth"
        middle_model.load_state_dict(torch.load(middle_model_path, map_location='cpu')) 
        print(f"Load middle model from {middle_model_path}")
        middle_model.eval()
        meta_model.load_state_dict(torch.load(meta_model_path, map_location='cpu')) 
        print(f"Load meta model from {meta_model_path}\n")
        meta_model.eval()
        return meta_model, middle_model

    elif model_type == "ResNet":
        model = models.resnet18(weights = None)
        in_features = model.fc.in_features
        model.fc = nn.Linear(in_features, 23)
        model_path = "pths/ResNet18.pth"
    
    elif model_type == "VGG":
        model = models.vgg16(weights = None) 
        in_features = model.classifier[6].in_features
        model.classifier[6] = nn.Linear(in_features, 23)
        model_path = "pths/VGG16.pth"
    
    model.load_state_dict(torch.load(model_path, map_location='cpu')) 
    print(f"Load model from {model_path}\n")
    model.eval()
    return model, model

def resize_and_pad_image(img, target_size):
    original_height, original_width = img.shape[:2]

    if original_height > original_width:
        scale = target_size / original_height
    else:
        scale = target_size / original_width

    resized_image = cv2.resize(img, None, fx=scale, fy=scale)

    # 创建目标大小的空白画布
    padded_height = target_size
    padded_width = target_size
    padded_image = np.squeeze(255 * np.ones((padded_height, padded_width, 1), dtype=np.uint8), axis=-1)
    
    x_offset = (padded_width - resized_image.shape[1]) // 2
    y_offset = (padded_height - resized_image.shape[0]) // 2

    # 将缩放后的图像放置在中心
    padded_image[y_offset:y_offset + resized_image.shape[0], x_offset:x_offset + resized_image.shape[1]] = resized_image

    return padded_image

def predict(model, image):
     if model._get_name() == "CNN_meta":
        transform = transform2
        Idx_map = Idx_map_met

     elif model._get_name() == "CNN_middle":
        transform = transform2
        Idx_map = Idx_map_mid
     else:
        transform = transform1
        Idx_map = Idx_map_0

     image = resize_and_pad_image(image, target_size=28)
     image = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
     image = Image.fromarray(image)
     trans = transform(image)
     trans = trans.unsqueeze(0)
     out = model(trans)
     predict = torch.max(out.data, 1)
     result = Idx_map[predict.indices.item()]
     return result