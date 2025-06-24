import cv2
# Option: Importer LaMa, RePaint, ou utiliser OpenCV inpainting

def remove_text_with_inpainting(frame, bbox_list, method="opencv"):
    """
    Supprime le texte sur la frame via inpainting (bbox_list = liste [x,y,w,h]).
    Pour l'instant, version OpenCV simple ; TODO: intégrer LaMa/RePaint.
    """
    mask = np.zeros(frame.shape[:2], dtype=np.uint8)
    for x, y, w, h in bbox_list:
        mask[y:y+h, x:x+w] = 255
    if method == "opencv":
        return cv2.inpaint(frame, mask, 3, cv2.INPAINT_TELEA)
    # TODO: Ajouter appel LaMa/RePaint pour inpainting avancé
    return frame