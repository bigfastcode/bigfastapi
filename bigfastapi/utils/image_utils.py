import os
from uuid import uuid4
from PIL import Image

from bigfastapi.db.database import SessionLocal


from bigfastapi.models.extra_info_models import ExtraInfo

MAIN_BUCKET = os.environ.get("IMAGES_FOLDER", "images")
ROOT_LOCATION = os.path.abspath(os.environ.get("FILES_BASE_FOLDER", "filestorage"))
THUMBNAIL_BUCKET = "thumbnails"


def create_thumbnail_dirs(unique_id):
    bucket_path = f"{THUMBNAIL_BUCKET}/{unique_id}"
    full_path = f"{ROOT_LOCATION}/{MAIN_BUCKET}/{bucket_path}"
    if not os.path.exists(full_path):
        os.makedirs(full_path)
    
    return bucket_path


def save_thumbnail_info(filename, thumbnail_path, unique_id, size, db=SessionLocal()):
    key = f"{filename}_{unique_id}_{size}"
    value = thumbnail_path

    with SessionLocal() as db:
        db.expire_on_commit = False
        image_info = db.query(ExtraInfo).filter(ExtraInfo.key==key).first()
        if image_info:
            image_info.key = key
            image_info.value = value
        else:
            image_info = ExtraInfo(
                id=uuid4().hex, key=key,
                value=value,
                rel_id=f"{unique_id}_thumbnails_{size}"
            )
        
        db.add(image_info)
        db.commit()

    return image_info


def generate_thumbnail_for_image(full_image_path, unique_id, width=None, height=None, scale="width"):

    width = width if width else height
    height = height if height else width

    # scale image
    img = Image.open(full_image_path)
    scaler = None
    if scale == "width" or scale == "height":
        scaler = width if scale == "width" else height
    if scaler is not None:
        img = img.resize((scaler, scaler))
        img.thumbnail((width, height))
    else:
        img.thumbnail((width, height))
    
    thumbnail_path = create_thumbnail_dirs(unique_id)
    thumbnail_full_path = f"{ROOT_LOCATION}/{MAIN_BUCKET}/{thumbnail_path}"
    filename, ext = os.path.splitext(full_image_path.split("/")[-1])
    thumbnail_filename = f"{filename}_{width}x{height}{ext}"
    outfile = f"{thumbnail_full_path}/{thumbnail_filename}"
    img.save(outfile, quality=95)

    thumbnail_path = f"{thumbnail_path}/{thumbnail_filename}"
    thumbnail = save_thumbnail_info(filename, thumbnail_path, unique_id, (width, height))

    return thumbnail
