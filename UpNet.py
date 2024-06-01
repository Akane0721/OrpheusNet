import cv2
import numpy as np

# 查找轮廓定位
def find_place(x, column_ranges):
    for i, (start, end) in enumerate(column_ranges):
        fringe = column_ranges[-1][-1] * 0.0012
        if start + fringe < x < end - fringe:
            return i
    return -1

def UpNet(image, column_ranges):
    image_width = image.shape[1]
    _, binary_image = cv2.threshold(image, 180, 255, cv2.THRESH_BINARY_INV)
    contours, _ = cv2.findContours(binary_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    sorted_contours = sorted(contours, key=lambda c: cv2.boundingRect(c)[0], reverse=False)

    symbols = []

    for i, contour in enumerate(sorted_contours):
        
        if cv2.contourArea(contour) < 0.1:
             continue

        x, y, w, h = cv2.boundingRect(contour) 
        aspect_ratio = w / h

        if len(contour) < 8 and aspect_ratio > 2:
                idx = find_place(x + w/2, column_ranges)
                symbols.append((idx, "line"))
                continue      
        
        estimated_pi = (cv2.arcLength(contour, closed=False) ** 2) / (4 * cv2.contourArea(contour))
        if abs(1 - estimated_pi / np.pi) < 0.39 and w / image_width < 0.005:
            idx = find_place(x + w/2, column_ranges)
            symbols.append((idx, "dot"))
            continue

        M = cv2.moments(contour)
        cy = int(M['m01'] / M['m00'])
        cyp = (cy-y)/h

        if cyp < 0.388:
            left_idx = find_place(x, column_ranges)
            right_idx = find_place(x + w, column_ranges)
            symbols.append(((left_idx, right_idx), "tie"))
            continue

    cv2.waitKey(0)
    cv2.destroyAllWindows()
    return symbols


