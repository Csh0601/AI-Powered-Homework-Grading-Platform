import os
from werkzeug.utils import secure_filename

def allowed_file(filename: str) -> bool:
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'jpg', 'jpeg', 'png'}

def save_upload_file(file, upload_folder: str, username: str) -> str:
    filename = secure_filename(f"{username}_{file.filename}")
    filepath = os.path.join(upload_folder, filename)
    file.save(filepath)
    return filepath
