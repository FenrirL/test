from autotranslate_shorts.core.pipeline import run_pipeline

def test_run_pipeline(tmp_path):
    # Test pipeline sur fichier fictif
    video_path = tmp_path / "dummy.mp4"
    video_path.write_text("fake video")
    res = run_pipeline(str(video_path), "fr", str(tmp_path))
    assert "files_generated" in res