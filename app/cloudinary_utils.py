import os
import cloudinary
import cloudinary.uploader

cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET"),
    secure=True
)

def upload_avatar_file(file) -> str:
    # file is a SpooledTemporaryFile or file-like (fastapi UploadFile)
    result = cloudinary.uploader.upload(file, folder="avatars", overwrite=True)
    return result.get("secure_url")