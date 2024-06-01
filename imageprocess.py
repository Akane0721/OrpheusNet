import os
import cv2
import numpy as np

def horizontal_protection(image, error_rate=0.0015, min_height=3, extension_rate = 5e-4, merge=False):
    image_height, image_width = image.shape
    projection = np.sum(image, axis=1)
    threshold = (image.shape[1] - error_rate * image_width)*255

    rows = []
    row_ranges = []
    top = -1
    for i,val in enumerate(projection):
        if top == -1:
            if val < threshold:
                top = i
        elif val >= threshold:
            if i - top >= min_height:
                extension = int(extension_rate * image_height + 0.5)
                row_ranges.append((top-extension, i+extension))
                top = -1

    if merge:
        merged_row_ranges = [row_ranges[0]]
        for i in range(1, len(row_ranges)):
            top, bottom = row_ranges[i]
            last_top, last_bottom = merged_row_ranges[-1]
            if top - last_bottom < 0.0045 * image_height:
                merged_row_ranges.pop()
                merged_row_ranges.append((last_top, bottom))
            else:
                merged_row_ranges.append((top, bottom))
        row_ranges = merged_row_ranges
    
    for top, bottom in row_ranges:
        rows.append(image[top: bottom, :])

    return rows

def vertical_protection(image, error_rate=0.04, min_width=3, extension_rate=0.001):
    image_height, image_width = image.shape
    projection = np.sum(image, axis=0)
    threshold = (image.shape[0] - error_rate * image_height)*255

    column_ranges = []
    left = -1
    for i,val in enumerate(projection):
        if left == -1:
            if val < threshold:
                left = i
        elif val >= threshold:
            if i - left >= min_width:
                extension = int(extension_rate * image_width + 0.5) 
                column_ranges.append((left - extension, i + extension))
                left = -1

    return column_ranges


def image_segmentation(image_path): # 通过水平投影切割简谱图像
    image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    rows = horizontal_protection(image, min_height=3, merge=True)
    return rows

def melody_line_identification(lines):
    # 定义长宽比阈值为0.09
    target_aspect_ratio = 0.09
    target_aspect_ratio2 = 0.11 # 终止线
    melody_lines = []
    note_line_index = 0
    first_note_line = -1
    lyric_start = False
    lyric_height = 0

    for index, image in enumerate(lines): 
        image_width = image.shape[1]
        haveBarline = False
        _, binary = cv2.threshold(image, 127, 255, cv2.THRESH_BINARY_INV)
        contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        sorted_contours = sorted(contours, key=lambda c: cv2.boundingRect(c)[0], reverse=True)
        midpoints = []
        
        for contour_index, contour in enumerate(sorted_contours):
            x, y, w, h = cv2.boundingRect(contour)
            aspect_ratio = w / h

            if contour_index == 0:
                if aspect_ratio >= target_aspect_ratio:
                    if not (index == len(lines) - 1 - lyric_height and aspect_ratio < target_aspect_ratio2):
                        if lyric_start and lyric_height == 0:
                            lyric_height += 1
                        break

            haveBarline = True

            if aspect_ratio < target_aspect_ratio2:
                if first_note_line == -1:
                    first_note_line = index
                
                midpoints.append(y + h / 2)
                # 去除小节线
                image[y-2:y+h+2, x-2:x+w+2] = 255
            
        if haveBarline:
            lyric_start = not lyric_start
            average_midpoint = sum(midpoints) / len(midpoints)
            melody_lines.append((image, average_midpoint))
            note_line_index += 1
    
    metadata_lines = []

    for i in range(0, first_note_line):
        line = lines[i]
        width = line.shape[1]
        metadata_lines += horizontal_protection(line[:,0:width//2], min_height=3, merge=False)   
    
    return melody_lines, metadata_lines

def symbols_adjustment(melody_lines):
    lines = []
    for index, (line, midpoint) in enumerate(melody_lines):
        _, binary = cv2.threshold(line, 127, 255, cv2.THRESH_BINARY_INV)
        contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        upper_bounds = []
        lower_bounds = []
        
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            if y < midpoint and y + h > midpoint: # 数字音符，附点符，延时符
                upper_bounds.append(y)
                lower_bounds.append(y + h)
        
        upper_bound = min(upper_bounds)
        lower_bound = max(lower_bounds)
        
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            if y + h > upper_bound and y < upper_bound: #升，降，还原音符
                temp = line[y-1:y+h+1 , x-1:x+w+1].copy()
                line[y-1:y+h+1, x-1:x+w+1] = 255
                line[upper_bound+2 : upper_bound+4+h, x-3:x+w-1] = temp

        lines.append((line, upper_bound, lower_bound))

    return lines  
        