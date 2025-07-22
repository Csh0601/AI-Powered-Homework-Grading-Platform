import os
import uuid
from werkzeug.utils import secure_filename

def save_upload_file(file, upload_folder):
    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder)
    ext = file.filename.rsplit('.', 1)[1].lower()
    filename = f"{uuid.uuid4().hex}.{ext}"
    filepath = os.path.join(upload_folder, secure_filename(filename))
    file.save(filepath)
    return filepath

def clean_expired_files(upload_folder, expire_seconds=3600):
    now = os.path.getmtime
    for fname in os.listdir(upload_folder):
        fpath = os.path.join(upload_folder, fname)
        if os.path.isfile(fpath) and (now(fpath) + expire_seconds < now(fpath)):
            os.remove(fpath)
