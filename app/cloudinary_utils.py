import cloudinary
import cloudinary.uploader
from app.config import CLOUDINARY_CLOUD_NAME, CLOUDINARY_API_KEY, CLOUDINARY_API_SECRET

cloudinary.config(
  cloud_name=CLOUDINARY_CLOUD_NAME,
  api_key=CLOUDINARY_API_KEY,
  api_secret=CLOUDINARY_API_SECRET,
  secure=True
)

def upload_avatar(file) -> str:
    # file: UploadFile
    res = cloudinary.uploader.upload(file.file, folder="contacts_avatars", overwrite=True)
    return res.get("secure_url")
