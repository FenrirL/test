import cv2
import os
import sys
import logging
from typing import List, Dict, Optional, Tuple, Any
from dataclasses import dataclass
from contextlib import contextmanager
from functools import lru_cache
from concurrent.futures import ThreadPoolExecutor, as_completed
import hashlib
import json
from pathlib import Path
from difflib import SequenceMatcher

# Imports des modules existants
from video_pipeline.auto_analyse import analyse_video_type
from video_pipeline.ocr_cleaning import clean_ocr_blocks
from video_pipeline.translation import translate_blocks
from video_pipeline.video_editing import edit_video_with_translations
from video_pipeline.audio_sync import generate_tts_segments, align_overlay_timing_with_tts, merge_audio_on_video
from video_pipeline.quality_control import generate_quality_report
from video_pipeline.fallback_tools import ocr_with_fallback, translate_with_fallback

# Configuration centralisée
@dataclass
class PipelineConfig:
    """Configuration centralisée pour la pipeline"""
    # Extraction de frames
    frame_extraction_interval: int = 30
    max_frames_to_process: int = 100
    
    # Vidéo
    supported_formats: List[str] = None
    max_file_size_mb: float = 500.0
    min_duration_seconds: float = 1.0
    max_duration_seconds: float = 300.0
    
    # OCR et correspondance
    text_similarity_threshold: float = 0.7
    ocr_confidence_threshold: float = 0.5
    
    # Traitement parallèle
    max_workers: int = 4
    enable_caching: bool = True
    
    # Sortie
    output_quality: str = "high"  # low, medium, high
    generate_debug_files: bool = True
    
    def __post_init__(self):
        if self.supported_formats is None:
            self.supported_formats = ['.mp4', '.avi', '.mov', '.mkv', '.webm']

# Configuration globale
CONFIG = PipelineConfig()

# Configuration du logging
def setup_logging(log_level: str = "INFO", log_file: str = "pipeline.log"):
    """Configure le système de logging"""
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)

logger = setup_logging()

# Exceptions personnalisées
class PipelineError(Exception):
    """Exception de base pour la pipeline"""
    pass

class VideoProcessingError(PipelineError):
    """Erreur lors du traitement vidéo"""
    pass

class ValidationError(PipelineError):
    """Erreur de validation des données"""
    pass

@contextmanager
def video_capture_context(video_path: str):
    """Context manager pour cv2.VideoCapture avec gestion automatique des ressources"""
    cap = cv2.VideoCapture(video_path)
    try:
        if not cap.isOpened():
            raise VideoProcessingError(f"Impossible d'ouvrir la vidéo : {video_path}")
        yield cap
    finally:
        cap.release()

def validate_input_file(video_path: str) -> Dict[str, Any]:
    """Valide le fichier vidéo d'entrée et retourne ses métadonnées"""
    if not os.path.exists(video_path):
        raise ValidationError(f"Fichier non trouvé : {video_path}")
    
    # Vérification de l'extension
    ext = Path(video_path).suffix.lower()
    if ext not in CONFIG.supported_formats:
        raise ValidationError(f"Format non supporté : {ext}. Formats acceptés : {CONFIG.supported_formats}")
    
    # Vérification de la taille
    file_size_mb = os.path.getsize(video_path) / (1024 * 1024)
    if file_size_mb > CONFIG.max_file_size_mb:
        raise ValidationError(f"Fichier trop volumineux : {file_size_mb:.1f}MB > {CONFIG.max_file_size_mb}MB")
    
    # Extraction des métadonnées vidéo
    with video_capture_context(video_path) as cap:
        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        duration = frame_count / fps if fps > 0 else 0
        
        # Vérification de la durée
        if duration < CONFIG.min_duration_seconds:
            raise ValidationError(f"Vidéo trop courte : {duration:.1f}s < {CONFIG.min_duration_seconds}s")
        if duration > CONFIG.max_duration_seconds:
            raise ValidationError(f"Vidéo trop longue : {duration:.1f}s > {CONFIG.max_duration_seconds}s")
    
    metadata = {
        'path': video_path,
        'size_mb': file_size_mb,
        'fps': fps,
        'frame_count': frame_count,
        'width': width,
        'height': height,
        'duration': duration,
        'format': ext
    }
    
    logger.info(f"Validation réussie : {metadata}")
    return metadata

def calculate_frame_hash(frame) -> str:
    """Calcule un hash pour un frame (pour le cache)"""
    return hashlib.md5(frame.tobytes()).hexdigest()

@lru_cache(maxsize=128)
def cached_frame_analysis(frame_hash: str, frame_bytes: bytes) -> str:
    """Cache pour l'analyse de frames (placeholder pour l'implémentation réelle)"""
    # Cette fonction serait implémentée avec l'OCR réel
    return frame_hash

def extract_frames_optimized(video_path: str, metadata: Dict[str, Any]) -> List[Tuple[int, Any]]:
    """
    Extraction optimisée de frames avec gestion intelligente de l'intervalle
    Retourne une liste de tuples (frame_index, frame_array)
    """
    fps = metadata['fps']
    duration = metadata['duration']
    
    # Calcul intelligent de l'intervalle d'extraction
    if duration <= 10:  # Vidéos courtes : plus de frames
        interval = max(1, int(fps / 2))  # 2 frames par seconde
    elif duration <= 60:  # Vidéos moyennes
        interval = int(fps)  # 1 frame par seconde
    else:  # Vidéos longues
        interval = int(fps * 2)  # 1 frame toutes les 2 secondes
    
    # Limitation du nombre total de frames
    max_frames = min(CONFIG.max_frames_to_process, int(duration * fps / interval))
    
    frames = []
    with video_capture_context(video_path) as cap:
        frame_idx = 0
        processed_count = 0
        
        while processed_count < max_frames:
            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
            ret, frame = cap.read()
            
            if not ret:
                break
                
            frames.append((frame_idx, frame))
            frame_idx += interval
            processed_count += 1
    
    logger.info(f"Extraction terminée : {len(frames)} frames extraites (intervalle={interval})")
    return frames

def parallel_ocr_processing(frames: List[Tuple[int, Any]]) -> List[Dict[str, Any]]:
    """Traitement OCR parallèle avec gestion d'erreurs robuste"""
    ocr_boxes = []
    
    def process_single_frame(frame_data: Tuple[int, Any]) -> List[Dict[str, Any]]:
        frame_idx, frame = frame_data
        try:
            logger.debug(f"Traitement OCR frame {frame_idx}, type: {type(frame)}")
            
            # Vérification de la validité du frame
            if frame is None or frame.size == 0:
                logger.warning(f"Frame {frame_idx} invalide, ignorée")
                return []
            
            blocks = ocr_with_fallback(frame)
            
            # Filtrage par confiance
            valid_blocks = []
            for block in blocks:
                if block.get('conf', 0) >= CONFIG.ocr_confidence_threshold:
                    block['frame_idx'] = frame_idx
                    valid_blocks.append(block)
                else:
                    logger.debug(f"Block ignoré (confiance trop faible): {block.get('conf', 0)}")
            
            return valid_blocks
            
        except Exception as e:
            logger.error(f"Erreur OCR sur frame {frame_idx}: {e}")
            return []
    
    # Traitement parallèle
    if CONFIG.max_workers > 1 and len(frames) > 1:
        with ThreadPoolExecutor(max_workers=CONFIG.max_workers) as executor:
            future_to_frame = {executor.submit(process_single_frame, frame_data): frame_data[0] 
                             for frame_data in frames}
            
            for future in as_completed(future_to_frame):
                frame_idx = future_to_frame[future]
                try:
                    blocks = future.result()
                    ocr_boxes.extend(blocks)
                except Exception as e:
                    logger.error(f"Erreur dans le traitement parallèle frame {frame_idx}: {e}")
    else:
        # Traitement séquentiel si parallélisme désactivé
        for frame_data in frames:
            blocks = process_single_frame(frame_data)
            ocr_boxes.extend(blocks)
    
    logger.info(f"OCR terminé : {len(ocr_boxes)} blocs détectés")
    return ocr_boxes

def smart_text_matching(text1: str, text2: str, threshold: float = None) -> bool:
    """Correspondance de texte intelligente avec similarité floue"""
    if threshold is None:
        threshold = CONFIG.text_similarity_threshold
    
    # Nettoyage des textes
    clean_text1 = text1.strip().lower()
    clean_text2 = text2.strip().lower()
    
    # Correspondance exacte d'abord
    if clean_text1 == clean_text2:
        return True
    
    # Correspondance floue
    similarity = SequenceMatcher(None, clean_text1, clean_text2).ratio()
    return similarity >= threshold

def enhanced_overlay_timing(ocr_boxes: List[Dict], transcription: List[Dict]) -> Dict[int, Dict]:
    """Génération de timing d'overlay améliorée avec correspondance intelligente"""
    timing = {}
    used_transcription_indices = set()
    
    for box in ocr_boxes:
        best_match = None
        best_similarity = 0
        best_idx = -1
        
        for idx, transcript_seg in enumerate(transcription):
            if idx in used_transcription_indices:
                continue
                
            if smart_text_matching(box.get('text', ''), transcript_seg.get('text', '')):
                similarity = SequenceMatcher(None, 
                                           box.get('text', '').lower(), 
                                           transcript_seg.get('text', '').lower()).ratio()
                
                if similarity > best_similarity:
                    best_similarity = similarity
                    best_match = transcript_seg
                    best_idx = idx
        
        if best_match and best_similarity >= CONFIG.text_similarity_threshold:
            timing[box['frame_idx']] = {
                'start': best_match['start'],
                'end': best_match['end'],
                'confidence': best_similarity
            }
            used_transcription_indices.add(best_idx)
            logger.debug(f"Correspondance trouvée : '{box.get('text', '')}' -> '{best_match.get('text', '')}' (conf={best_similarity:.2f})")
    
    logger.info(f"Timing généré pour {len(timing)} éléments")
    return timing

def enhanced_transcription_stub(video_path: str) -> List[Dict[str, Any]]:
    """Version améliorée du stub de transcription (à remplacer par Whisper)"""
    # TODO: Remplacer par une vraie implémentation Whisper
    # Pour l'instant, données d'exemple plus réalistes
    return [
        {"text": "Bonjour et bienvenue", "start": 0.5, "end": 2.0, "confidence": 0.95},
        {"text": "dans cette vidéo", "start": 2.1, "end": 3.5, "confidence": 0.92},
        {"text": "nous allons voir", "start": 3.6, "end": 5.0, "confidence": 0.88},
        {"text": "comment améliorer", "start": 5.1, "end": 6.5, "confidence": 0.90},
        {"text": "vos compétences", "start": 6.6, "end": 8.0, "confidence": 0.93},
    ]

def process_text_content(video_path: str, metadata: Dict) -> Tuple[List[Dict], List[Dict], Dict[int, Dict]]:
    """Traitement du contenu textuel (OCR + nettoyage + timing)"""
    logger.info("Début du traitement textuel")
    
    # 1. Extraction de frames optimisée
    frames = extract_frames_optimized(video_path, metadata)
    if not frames:
        raise VideoProcessingError("Aucune frame extraite")
    
    # 2. OCR parallèle
    ocr_boxes = parallel_ocr_processing(frames)
    if not ocr_boxes:
        logger.warning("Aucun texte détecté dans la vidéo")
        return [], [], {}
    
    # 3. Nettoyage OCR
    try:
        sentences = clean_ocr_blocks(ocr_boxes)
        logger.info(f"Nettoyage OCR : {len(sentences)} phrases extraites")
    except Exception as e:
        logger.error(f"Erreur nettoyage OCR : {e}")
        sentences = [box.get('text', '') for box in ocr_boxes if box.get('text')]
    
    # 4. Timing avec transcription
    try:
        transcription = enhanced_transcription_stub(video_path)
        overlay_timing = enhanced_overlay_timing(ocr_boxes, transcription)
    except Exception as e:
        logger.error(f"Erreur génération timing : {e}")
        overlay_timing = {}
    
    return ocr_boxes, sentences, overlay_timing

def process_audio_content(video_path: str) -> Tuple[List[Dict], List[str], Dict[int, Dict]]:
    """Traitement du contenu audio (transcription + timing)"""
    logger.info("Début du traitement audio")
    
    try:
        # Transcription audio
        transcription = enhanced_transcription_stub(video_path)
        sentences = [seg["text"] for seg in transcription]
        
        # Génération de boxes fictives pour l'overlay
        ocr_boxes = []
        overlay_timing = {}
        
        for i, seg in enumerate(transcription):
            # Calcul de position approximative basée sur le timing
            frame_idx = int(seg["start"] * 25)  # Assumant 25 FPS
            
            box = {
                "frame_idx": frame_idx,
                "box": (50, 400 + (i % 3) * 100, 600, 80),  # Positions variées
                "text": seg["text"],
                "conf": seg.get("confidence", 0.9)
            }
            ocr_boxes.append(box)
            
            overlay_timing[frame_idx] = {
                "start": seg["start"],
                "end": seg["end"],
                "confidence": seg.get("confidence", 0.9)
            }
        
        logger.info(f"Traitement audio : {len(sentences)} segments transcrits")
        return ocr_boxes, sentences, overlay_timing
        
    except Exception as e:
        logger.error(f"Erreur traitement audio : {e}")
        return [], [], {}

def safe_translation(sentences: List[str], target_lang: str) -> List[Dict[str, str]]:
    """Traduction sécurisée avec gestion d'erreurs"""
    if not sentences:
        return []
    
    try:
        translations = translate_with_fallback(sentences, target_lang=target_lang)
        
        trad_blocks = []
        for i, sentence in enumerate(sentences):
            if i < len(translations):
                trad_blocks.append({
                    "text": sentence,
                    f"text_{target_lang}": translations[i],
                    "translation_confidence": 0.9  # TODO: obtenir la vraie confiance
                })
            else:
                logger.warning(f"Traduction manquante pour la phrase {i}")
                trad_blocks.append({
                    "text": sentence,
                    f"text_{target_lang}": sentence,  # Fallback: texte original
                    "translation_confidence": 0.0
                })
        
        logger.info(f"Traduction terminée : {len(trad_blocks)} éléments traduits")
        return trad_blocks
        
    except Exception as e:
        logger.error(f"Erreur traduction : {e}")
        # Fallback : retourner le texte original
        return [{"text": s, f"text_{target_lang}": s, "translation_confidence": 0.0} for s in sentences]

def save_debug_data(data: Dict[str, Any], outdir: str, filename: str):
    """Sauvegarde des données de debug en JSON"""
    if not CONFIG.generate_debug_files:
        return
    
    debug_path = os.path.join(outdir, "debug")
    os.makedirs(debug_path, exist_ok=True)
    
    filepath = os.path.join(debug_path, f"{filename}.json")
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2, default=str)
        logger.debug(f"Données debug sauvées : {filepath}")
    except Exception as e:
        logger.error(f"Erreur sauvegarde debug {filepath}: {e}")

def improved_main(video_path: str, lang: str = "en", outdir: str = "outputs") -> Dict[str, Any]:
    """
    Pipeline principale améliorée avec gestion d'erreurs robuste et logging complet
    
    Returns:
        Dict contenant les résultats et métriques de traitement
    """
    start_time = time.time()
    results = {
        "success": False,
        "video_path": video_path,
        "target_language": lang,
        "output_directory": outdir,
        "errors": [],
        "warnings": [],
        "processing_time": 0,
        "files_generated": []
    }
    
    try:
        logger.info(f"=== DÉBUT TRAITEMENT VIDÉO ===")
        logger.info(f"Fichier: {video_path}")
        logger.info(f"Langue cible: {lang}")
        logger.info(f"Dossier sortie: {outdir}")
        
        # Création du dossier de sortie
        os.makedirs(outdir, exist_ok=True)
        
        # PHASE 1: Validation et analyse
        logger.info("Phase 1: Validation et analyse")
        metadata = validate_input_file(video_path)
        video_type = analyse_video_type(video_path)
        
        logger.info(f"Type de vidéo détecté : {video_type}")
        results["video_type"] = video_type
        results["metadata"] = metadata
        
        # PHASE 2: Traitement selon le type
        ocr_boxes = []
        sentences = []
        overlay_timing = {}
        
        if video_type in ("music_or_silence", "text", "speech+text"):
            logger.info("Phase 2: Traitement contenu textuel")
            ocr_boxes, sentences, overlay_timing = process_text_content(video_path, metadata)
            
        elif video_type == "speech":
            logger.info("Phase 2: Traitement contenu audio")
            ocr_boxes, sentences, overlay_timing = process_audio_content(video_path)
            
        else:
            raise VideoProcessingError(f"Type de vidéo non supporté : {video_type}")
        
        # Sauvegarde debug
        save_debug_data({
            "ocr_boxes": ocr_boxes,
            "sentences": sentences,
            "overlay_timing": overlay_timing
        }, outdir, "extraction_data")
        
        # PHASE 3: Traduction
        logger.info("Phase 3: Traduction")
        trad_blocks = safe_translation(sentences, lang)
        
        if not trad_blocks:
            results["warnings"].append("Aucune traduction générée")
            logger.warning("Aucune traduction générée")
        
        save_debug_data({"translations": trad_blocks}, outdir, "translation_data")
        
        # PHASE 4: Édition vidéo
        logger.info("Phase 4: Édition vidéo")
        if ocr_boxes and trad_blocks:
            out_video = os.path.join(outdir, f"video_edited_{lang}.mp4")
            
            try:
                edit_video_with_translations(
                    video_path,
                    ocr_boxes,
                    trad_blocks,
                    out_path=out_video,
                    lang=lang,
                    overlay_timing=overlay_timing
                )
                results["files_generated"].append(out_video)
                logger.info(f"Vidéo éditée exportée : {out_video}")
                
            except Exception as e:
                error_msg = f"Erreur édition vidéo : {e}"
                results["errors"].append(error_msg)
                logger.error(error_msg)
        
        # PHASE 5: Synchronisation audio TTS
        logger.info("Phase 5: Génération et synchronisation audio")
        if trad_blocks and out_video:
            try:
                final_video = os.path.join(outdir, f"video_final_{lang}.mp4")
                
                tts_segments = generate_tts_segments(trad_blocks, lang=lang)
                tts_timing = align_overlay_timing_with_tts(ocr_boxes, tts_segments, fps=metadata.get('fps', 25))
                merge_audio_on_video(out_video, tts_segments, out_path=final_video)
                
                results["files_generated"].append(final_video)
                logger.info(f"Vidéo finale avec audio : {final_video}")
                
                save_debug_data({
                    "tts_segments": tts_segments,
                    "tts_timing": tts_timing
                }, outdir, "tts_data")
                
            except Exception as e:
                error_msg = f"Erreur synchronisation audio : {e}"
                results["errors"].append(error_msg)
                logger.error(error_msg)
        
        # PHASE 6: Contrôle qualité
        logger.info("Phase 6: Contrôle qualité")
        try:
            generate_quality_report(
                video_path,
                ocr_boxes,
                trad_blocks,
                tts_segments if 'tts_segments' in locals() else [],
                errors=results["errors"],
                outdir=outdir
            )
            
            quality_report_path = os.path.join(outdir, "quality_report.json")
            if os.path.exists(quality_report_path):
                results["files_generated"].append(quality_report_path)
                
        except Exception as e:
            error_msg = f"Erreur génération rapport qualité : {e}"
            results["errors"].append(error_msg)
            logger.error(error_msg)
        
        # Finalisation
        results["success"] = len(results["errors"]) == 0
        results["processing_time"] = time.time() - start_time
        
        logger.info(f"=== TRAITEMENT TERMINÉ ===")
        logger.info(f"Succès: {results['success']}")
        logger.info(f"Temps: {results['processing_time']:.2f}s")
        logger.info(f"Fichiers générés: {len(results['files_generated'])}")
        logger.info(f"Erreurs: {len(results['errors'])}")
        logger.info(f"Avertissements: {len(results['warnings'])}")
        
        return results
        
    except Exception as e:
        error_msg = f"Erreur critique pipeline : {e}"
        results["errors"].append(error_msg)
        results["processing_time"] = time.time() - start_time
        logger.error(error_msg, exc_info=True)
        return results

if __name__ == "__main__":
    import time
    
    if len(sys.argv) < 2:
        print("Usage: python improved_pipeline.py <video_path> [lang] [outdir] [config_file]")
        print("Exemple: python improved_pipeline.py video.mp4 en outputs config.json")
        sys.exit(1)
    
    # Paramètres
    video_path = sys.argv[1]
    lang = sys.argv[2] if len(sys.argv) > 2 else "en"
    outdir = sys.argv[3] if len(sys.argv) > 3 else "outputs"
    config_file = sys.argv[4] if len(sys.argv) > 4 else None
    
    # Chargement configuration personnalisée
    if config_file and os.path.exists(config_file):
        try:
            with open(config_file, 'r') as f:
                custom_config = json.load(f)
            # Mise à jour de la configuration globale
            for key, value in custom_config.items():
                if hasattr(CONFIG, key):
                    setattr(CONFIG, key, value)
            logger.info(f"Configuration chargée depuis {config_file}")
        except Exception as e:
            logger.error(f"Erreur chargement configuration {config_file}: {e}")
    
    # Exécution de la pipeline
    results = improved_main(video_path, lang=lang, outdir=outdir)
    
    # Affichage des résultats
    print("\n" + "="*60)
    print("RÉSULTATS DE TRAITEMENT")
    print("="*60)
    print(f"Succès: {'✓' if results['success'] else '✗'}")
    print(f"Temps de traitement: {results['processing_time']:.2f}s")
    print(f"Fichiers générés: {len(results['files_generated'])}")
    
    if results['files_generated']:
        print("\nFichiers créés:")
        for file in results['files_generated']:
            print(f"  - {file}")
    
    if results['errors']:
        print(f"\nErreurs ({len(results['errors'])}):")
        for error in results['errors']:
            print(f"  ✗ {error}")
    
    if results['warnings']:
        print(f"\nAvertissements ({len(results['warnings'])}):")
        for warning in results['warnings']:
            print(f"  ⚠ {warning}")
    
    # Code de sortie
    sys.exit(0 if results['success'] else 1)