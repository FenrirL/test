from autotranslate_shorts.processors.ocr_cleaning import clean_ocr_blocks

def test_clean_ocr_blocks():
    # Test stub OCR
    blocks = clean_ocr_blocks("dummy.mp4")
    assert isinstance(blocks, list)
    assert "text" in blocks[0]