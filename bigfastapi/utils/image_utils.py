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


def generate_thumbnail_for_image(full_image_path, unique_id, width=None, height=None):
    wpercent = None
    width = width if width else height
    height = height if height else width

    img = Image.open(full_image_path)
    if width and not height:
        wpercent = (width/float(img.size[0]))
        height = int((float(img.size[1])*float(wpercent)))
    elif height and not width:
        hpercent = (height/float(img.size[1]))
        width = int((float(img.size[1])*float(hpercent)))
    img = img.resize((width, height), Image.ANTIALIAS)
    
    thumbnail_path = create_thumbnail_dirs(unique_id)
    thumbnail_full_path = f"{ROOT_LOCATION}/{MAIN_BUCKET}/{thumbnail_path}"
    filename, ext = os.path.splitext(full_image_path.split("/")[-1])
    thumbnail_filename = f"{filename}_{width}x{height}{ext}"
    outfile = f"{thumbnail_full_path}/{thumbnail_filename}"
    img.save(outfile)

    thumbnail_path = f"{thumbnail_path}/{thumbnail_filename}"
    thumbnail = save_thumbnail_info(filename, thumbnail_path, unique_id, (width, height))

    return thumbnail
