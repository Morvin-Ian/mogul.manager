import uuid
from io import BytesIO
import boto3
from PIL import Image, ImageOps
from starlette.concurrency import run_in_threadpool

from config import settings

def get_s3_client():
    return boto3.client(
        "s3",
        endpoint_url=settings.s3_endpoint_url,
        aws_access_key_id=settings.s3_access_key_id.get_secret_value(),
        aws_secret_access_key=settings.s3_secret_access_key.get_secret_value(),
    )


s3_client = get_s3_client()


def _upload_to_s3(content: bytes, filename: str) -> str:
    s3_client.put_object(
        Bucket=settings.s3_bucket_name,
        Key=filename,
        Body=content,
        ContentType="image/jpeg",
    )
    return filename


def _delete_from_s3(filename: str) -> None:
    s3_client.delete_object(
        Bucket=settings.s3_bucket_name,
        Key=filename,
    )


async def upload_profile_image(content: bytes, filename: str) -> None:
    key = f"profile_pics/{filename}"
    await run_in_threadpool(_upload_to_s3, content, key)


async def delete_profile_image(filename: str | None) -> None:
    if filename is None:
        return
    await run_in_threadpool(_delete_from_s3, f"profile_pics/{filename}")


def process_profile_image(content: bytes) -> tuple[bytes, str]:
    with Image.open(BytesIO(content)) as original:
        img = ImageOps.exif_transpose(original)

        img = ImageOps.fit(img, (300, 300), method=Image.Resampling.LANCZOS)
        if img.mode in ("LA", "p", "RGBA"):
            img = img.convert("RGB")

        filename = f"{uuid.uuid4().hex}.jpg"
        output = BytesIO()
        img.save(output, "JPEG", quality=85, optimize=True)
        output.seek(0)
        return output.read(), filename
