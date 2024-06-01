import cv2
from utils import *

def are_equal_signs(contour1, contour2):
    x1, _, w1, h1 = cv2.boundingRect(contour1)
    x2, _, w2, h2 = cv2.boundingRect(contour2)

    if w1 / h1 > 2 and w2 / h2 > 2: 
        if abs(x1/x2-1) < 0.1 and abs(w1/w2-1) < 0.1 and abs(h1 - h2) < w1 * 0.2: #相等
            return True
    return False

def tempo_correct(symbol):
    if symbol == "B":
        return "8"
    elif symbol == "D":
        return "0"
    else:
        return symbol

def MetaNet(model, image_list):
    key = -1
    speed = ""

    for i, image in enumerate(image_list):
        height = image.shape[0]
        _, binary_image = cv2.threshold(image, 127, 255, cv2.THRESH_BINARY_INV)
        contours, _ = cv2.findContours(binary_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        sorted_contours = sorted(contours, key=lambda c: cv2.boundingRect(c)[0])
        sorted_contours = [s for s in sorted_contours if cv2.contourArea(s) > 0.5]
        
        if(len(sorted_contours)<5):
            continue
        if not are_equal_signs(sorted_contours[1], sorted_contours[2]):
                continue
        
        # 从左往右第一个符号
        x, y, w, h = cv2.boundingRect(sorted_contours[0])
        img = image[y:y+h, x:x+w]    
        first_symbol = predict(model, img)

        if key == -1 and first_symbol == "1": # Key行          
            x, y, w, h = cv2.boundingRect(sorted_contours[3])
            img = image[y:y+h, x:x+w]  
            first = predict(model, img)
            if(first == "sharp" or first == "flat"):
                x2, y2, w2, h2 = cv2.boundingRect(sorted_contours[4])
                img2 = image[y2-1:y2+h2+1, x2:x2+w2+1]  
                second = predict(model, img2)  
                sj = "#" if first == "sharp" else "-"
                key = second + sj
            else:
                key = first
        
        elif speed == "" and first_symbol == "quarter":
            x1, y1, w1, h1 = cv2.boundingRect(sorted_contours[3])
            img1 = image[max(y1-1,0):min(y1+h1+1,height), x1:x1+w1]
            cv2.imwrite(f"cnmtest/imgy{i}.jpg", img1)
            first = tempo_correct(predict(model, img1))
            
            x2, y2, w2, h2 = cv2.boundingRect(sorted_contours[4])
            img2 = image[y2:y2+h2, x2:x2+w2]
            second = tempo_correct(predict(model, img2))
            if(first == "1" or first == "2"):   # 三位数
                if(len(sorted_contours) < 6):
                    raise ValueError("Abnormal BPM, should be no less than 30!")
                x3, y3, w3, h3 = cv2.boundingRect(sorted_contours[5])
                img3 = image[y3:y3+h3, x3:x3+w3]
                third = tempo_correct(predict(model, img3))
                speed = first + second + third
            
            else:   # 两位数
                speed = first + second   

        else:
            continue 

    return key, int(speed)  
