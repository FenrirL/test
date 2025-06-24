import cv2
import numpy as np

def inpaint_text_on_frame(frame, bbox):
    """
    Efface la zone bbox (format: 4 points ou x,y,w,h) de la frame via inpainting OpenCV.
    """
    mask = np.zeros(frame.shape[:2], np.uint8)
    # Pour bbox 4 points:
    pts = np.array([bbox], dtype=np.int32)
    cv2.fillPoly(mask, pts, 255)
    # Pour bbox x,y,w,h, décommente:
    # x, y, w, h = bbox; mask[y:y+h, x:x+w] = 255
    inpainted = cv2.inpaint(frame, mask, 3, cv2.INPAINT_TELEA)
    return inpainted