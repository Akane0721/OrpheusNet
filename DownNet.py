import cv2

def DownNet(image):
    _, binary_image = cv2.threshold(image, 127, 255, cv2.THRESH_BINARY_INV)
    contours, _ = cv2.findContours(binary_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    sorted_contours = sorted(contours, key=lambda c: cv2.boundingRect(c)[1], reverse=False)
    symbols = []

    for contour in sorted_contours:
        x, y, w, h = cv2.boundingRect(contour) 
        aspect_ratio = w / h

        if(aspect_ratio) < 2:   
            symbols.append("dot") 
        else: 
            symbols.append("dash")

    cv2.waitKey(0)
    cv2.destroyAllWindows()
    return symbols
