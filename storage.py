import os
import uuid
import asyncio
from supabase import create_async_client, AsyncClient
from dotenv import load_dotenv
from pathlib import Path

# Explicitly load .env from the same directory as this file
BASE_DIR = Path(__file__).resolve().parent
load_dotenv(dotenv_path=BASE_DIR / ".env")

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
BUCKET_NAME = "products"

_supabase: AsyncClient = None

async def get_supabase_client() -> AsyncClient:
    """
    Returns a singleton instance of the Supabase AsyncClient.
    """
    global _supabase
    if _supabase is None:
        if not SUPABASE_URL or not SUPABASE_KEY:
            raise Exception("Supabase credentials missing. Please check your .env file.")
        _supabase = await create_async_client(SUPABASE_URL, SUPABASE_KEY)
    return _supabase

async def upload_image(file_content: bytes, filename: str) -> str:
    """
    Uploads an image to Supabase Storage and returns the public URL.
    """
    client = await get_supabase_client()
    
    file_ext = os.path.splitext(filename)[1].lower()
    if not file_ext:
        file_ext = ".jpg"
        
    unique_filename = f"{uuid.uuid4()}{file_ext}"
    content_type = f"image/{file_ext.lstrip('.')}"
    if file_ext in [".jpg", ".jpeg"]:
        content_type = "image/jpeg"
    elif file_ext == ".png":
        content_type = "image/png"
    
    try:
        # Uploading file to the bucket using the latest async API
        await client.storage.from_(BUCKET_NAME).upload(
            path=unique_filename,
            file=file_content,
            file_options={"content-type": content_type}
        )
        
        # Getting the public URL
        # In the latest version, get_public_url is often synchronous but some clients treat it as async.
        # To be safe, we check and call it directly.
        public_url_res = client.storage.from_(BUCKET_NAME).get_public_url(unique_filename)
        return str(public_url_res)
    except Exception as e:
        print(f"[ERROR] Supabase Upload Error: {str(e)}")
        raise Exception(f"Failed to upload image: {str(e)}")

async def delete_image(image_url: str):
    """
    Deletes an image from Supabase Storage based on its public URL.
    """
    client = await get_supabase_client()
    
    if not image_url:
        return

    try:
        if BUCKET_NAME in image_url:
            # Extract the path from the URL
            path = image_url.split(f"{BUCKET_NAME}/")[-1]
            # Remove any query parameters
            path = path.split("?")[0]
            
            await client.storage.from_(BUCKET_NAME).remove([path])
    except Exception as e:
        print(f"[ERROR] Supabase Delete Error: {str(e)}")
