import os
from uuid import uuid4
from PIL import Image, ImageChops

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


def crop_image(image, width, height, crop_type="middle"):
    # If height is higher we resize vertically, if not we resize horizontally
    img = image
    size = (width, height)
    # Get current and desired ratio for the images
    img_ratio = img.size[0] / float(img.size[1])
    ratio = size[0] / float(size[1])
    #The image is scaled/cropped vertically or horizontally depending on the ratio
    if ratio > img_ratio:
        img = img.resize((size[0], int(round(size[0] * img.size[1] / img.size[0]))),
            Image.ANTIALIAS)
        # Crop in the top, middle or bottom
        if crop_type == 'top':
            box = (0, 0, img.size[0], size[1])
        elif crop_type == 'middle':
            box = (0, int(round((img.size[1] - size[1]) / 2)), img.size[0],
                int(round((img.size[1] + size[1]) / 2)))
        elif crop_type == 'bottom':
            box = (0, img.size[1] - size[1], img.size[0], img.size[1])
        else :
            raise ValueError('ERROR: invalid value for crop_type')
        img = img.crop(box)
    elif ratio < img_ratio:
        img = img.resize((int(round(size[1] * img.size[0] / img.size[1])), size[1]),
            Image.ANTIALIAS)
        # Crop in the top, middle or bottom
        if crop_type == 'top':
            box = (0, 0, size[0], img.size[1])
        elif crop_type == 'middle':
            box = (int(round((img.size[0] - size[0]) / 2)), 0,
                int(round((img.size[0] + size[0]) / 2)), img.size[1])
        elif crop_type == 'bottom':
            box = (img.size[0] - size[0], 0, img.size[0], img.size[1])
        else :
            raise ValueError('ERROR: invalid value for crop_type')
        img = img.crop(box)
    else :
        img = img.resize((size[0], size[1]),
            Image.ANTIALIAS)
    # If the scale is the same, we do not need to crop
    return img


def generate_thumbnail_for_image(full_image_path, unique_id, width=None, height=None, scale="width"):

    width = width if width else height
    height = height if height else width

    # scale image
    img = Image.open(full_image_path)
    img = crop_image(img, width, height)
    
    thumbnail_path = create_thumbnail_dirs(unique_id)
    thumbnail_full_path = f"{ROOT_LOCATION}/{MAIN_BUCKET}/{thumbnail_path}"
    filename, ext = os.path.splitext(full_image_path.split("/")[-1])
    thumbnail_filename = f"{filename}_{width}x{height}{ext}"
    outfile = f"{thumbnail_full_path}/{thumbnail_filename}"
    img.save(outfile, quality=95)

    thumbnail_path = f"{thumbnail_path}/{thumbnail_filename}"
    thumbnail = save_thumbnail_info(filename, thumbnail_path, unique_id, (width, height))

    return thumbnail


def delete_thumbnails(filename, bucket_name, file_instance, file_path, db):
    filename = os.path.splitext(filename)[0]
    key = f"{filename}_{bucket_name}_%"
    thumbnails = db.query(ExtraInfo).filter(
        ExtraInfo.key.ilike(key)
    ).all()
    dir_full_path = os.path.join(ROOT_LOCATION, MAIN_BUCKET)
    for thumbnail in thumbnails:
        thumbnail_full_path = os.path.join(dir_full_path, thumbnail.value)
        try:
            os.remove(thumbnail_full_path)
            db.delete(thumbnail)
        except Exception as ex:
            raise ex
    os.remove(file_path)
    db.delete(file_instance)
    db.commit()

    return True
