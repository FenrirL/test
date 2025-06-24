from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload, MediaFileUpload
from google.oauth2.service_account import Credentials
import io
import os
from config import Config
from video_pipeline.utils import setup_logger

logger = setup_logger("video_pipeline.drive")

SCOPES = ['https://www.googleapis.com/auth/drive']

def authentification_drive():
    """Authentifie le service Google Drive."""
    creds = None
    if Config.GOOGLE_CREDENTIALS and os.path.exists(Config.GOOGLE_CREDENTIALS):
        creds = Credentials.from_service_account_file(
            Config.GOOGLE_CREDENTIALS, scopes=SCOPES)
    if not creds or not creds.valid:
        logger.error("Impossible de charger les identifiants Google Drive ou credentials invalides.")
        return None
    try:
        service = build('drive', 'v3', credentials=creds)
        logger.info("✅ Authentification Google Drive réussie.")
        return service
    except Exception as e:
        logger.error(f"❌ Erreur lors de l'authentification Google Drive : {e}")
        return None

def lister_videos_drive(service, folder_id):
    """Liste les fichiers vidéo dans le dossier spécifié."""
    try:
        results = service.files().list(
            q=f"'{folder_id}' in parents and mimeType contains 'video/' and trashed=false",
            fields="nextPageToken, files(id, name)").execute()
        items = results.get('files', [])
        if not items:
            logger.info(f"ℹ️ Aucun fichier vidéo trouvé dans le dossier : {folder_id}")
            return []
        logger.info(f"🔍 {len(items)} fichier(s) vidéo trouvé(s) dans le dossier : {folder_id}")
        return items
    except Exception as e:
        logger.error(f"❌ Erreur lors de la liste des fichiers Drive : {e}")
        return []

def telecharger_video_drive(service, file_id, local_path):
    """Télécharge un fichier depuis Google Drive."""
    try:
        request = service.files().get_media(fileId=file_id)
        fh = io.BytesIO()
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while not done:
            status, done = downloader.next_chunk()
            if status:
                logger.info(f"⬇️ Téléchargement {int(status.progress() * 100)}% du fichier ID : {file_id}")
        fh.seek(0)
        with open(local_path, 'wb') as f:
            f.write(fh.read())
        logger.info(f"✅ Fichier ID '{file_id}' téléchargé vers : {local_path}")
        return local_path
    except Exception as e:
        logger.error(f"❌ Erreur lors du téléchargement du fichier ID '{file_id}' : {e}")
        return None

def uploader_video_drive(service, local_path, folder_id):
    """Upload un fichier vers Google Drive."""
    try:
        file_name = os.path.basename(local_path)
        media = MediaFileUpload(local_path, mimetype='video/*')
        file_metadata = {'name': file_name, 'parents': [folder_id]}
        request = service.files().create(media_body=media, body=file_metadata, fields='id')
        response = None
        while response is None:
            status, response = request.next_chunk()
            if status:
                logger.info(f"⬆️ Upload {int(status.progress() * 100)}% du fichier : {file_name}")
        logger.info(f"✅ Fichier '{file_name}' uploadé vers le dossier ID '{folder_id}', ID du fichier : '{response.get('id')}'")
        return response.get('id')
    except Exception as e:
        logger.error(f"❌ Erreur lors de l'upload du fichier '{os.path.basename(local_path)}' : {e}")
        return None