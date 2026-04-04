import os
import uuid
from supabase import create_client, Client
from dotenv import load_dotenv
from pathlib import Path

# Explicitly load .env from the same directory as this file
BASE_DIR = Path(__file__).resolve().parent
load_dotenv(dotenv_path=BASE_DIR / ".env")

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
BUCKET_NAME = "products"

supabase: Client = None

if SUPABASE_URL and SUPABASE_KEY:
    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    except Exception as e:
        print(f"[ERROR] Failed to initialize Supabase client: {str(e)}")

async def upload_image(file_content: bytes, filename: str) -> str:
    """
    Uploads an image to Supabase Storage and returns the public URL.
    """
    if not supabase:
        raise Exception("Supabase storage is not configured. Please check your .env file.")

    file_ext = os.path.splitext(filename)[1].lower()
    if not file_ext:
        file_ext = ".jpg"
        
    unique_filename = f"{uuid.uuid4()}{file_ext}"
    content_type = f"image/{file_ext.lstrip('.')}"
    if file_ext == ".jpg" or file_ext == ".jpeg":
        content_type = "image/jpeg"
    elif file_ext == ".png":
        content_type = "image/png"
    
    try:
        # Uploading file to the bucket (sync call wrapped in to_thread)
        await asyncio.to_thread(
            supabase.storage.from_(BUCKET_NAME).upload,
            path=unique_filename,
            file=file_content,
            file_options={"content-type": content_type}
        )
        
        # Getting the public URL
        res = await asyncio.to_thread(
            supabase.storage.from_(BUCKET_NAME).get_public_url,
            unique_filename
        )
        return res
    except Exception as e:
        print(f"[ERROR] Supabase Upload Error: {str(e)}")
        raise Exception(f"Failed to upload image: {str(e)}")

async def delete_image(image_url: str):
    """
    Deletes an image from Supabase Storage based on its public URL.
    """
    if not supabase or not image_url:
        return

    try:
        if BUCKET_NAME in image_url:
            # Handle both full URL and path
            path = image_url.split(f"{BUCKET_NAME}/")[-1]
            # Remove any query parameters if present
            path = path.split("?")[0]
            await asyncio.to_thread(
                supabase.storage.from_(BUCKET_NAME).remove,
                [path]
            )
    except Exception as e:
        print(f"[ERROR] Supabase Delete Error: {str(e)}")
