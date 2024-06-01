import cv2
from utils import *

def MiddleNet(model, image):
    
    _, binary_image = cv2.threshold(image, 127, 255, cv2.THRESH_BINARY_INV)
    contours, _ = cv2.findContours(binary_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if(len(contours) > 1): #循环符号
        answer = "repeat"
    
    else:
        for contour in contours:
            _, _, w, h = cv2.boundingRect(contour)
            if len(contour) < 15 and w / h > 2:
                answer = "dash"
            
            else:
                
                if(h / image.shape[0]) < 0.35:
                    answer = "dot"
                                   
                else:
                    answer = predict(model, image)
                    
    return answer
