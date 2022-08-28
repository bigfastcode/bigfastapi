import os, shutil
from PIL import Image
from uuid import uuid4

from bigfastapi.models.extra_info_models import ExtraInfo


def save_thumbnail_info(thumbnail_path, organization_id, db, size=(100, 100)):
    """
    Save thumbnail info to ExtraInfo table in DB
    :param thumbnail_path: Absolute path to where thumbnail
    :param organization_id: unique identifier for the organization
    :param db: Database session object
    :param size: thumbnail image size
    :return: None
    """
    try:
        key = f"thumbnail_{organization_id}_{size}"
        value = f"{thumbnail_path} && {size}"
        thumbnail_info = db.query(ExtraInfo).filter(ExtraInfo.key==key).first()
        if not thumbnail_info:
            thumbnail_info = ExtraInfo(id=uuid4().hex, key=key, value=value)
        else:
            thumbnail_info.key = key
            thumbnail_info.value = value
        db.add(thumbnail_info)
        db.commit()
        db.refresh(thumbnail_info)
    except Exception as ex:
        raise ex
    

def gen_thumbnail(
    filename, root_location, thumb_id, size=(100, 100), bucket="thumbnails", clean=False):
    """
    Function to generate variable sized thumbnails from an image
    :param filename: Name of image file
    :param root_location: Full path to for saving and fetching image file
    :param thumb_id: Unique identify added to thumbnail filename
    :param size: Generated thumbnail size
    :param bucket: directory name to save thumbnail
    :return: A string
    """

    # delete previous thumbnails on new image upload
    if clean and os.path.exists(root_location + f"/{bucket}/{thumb_id}"):
        shutil.rmtree(root_location + f"/{bucket}/{thumb_id}")

    # create buckets if not exist
    if not os.path.exists(root_location + f"/{bucket}"):
        os.mkdir(root_location + f"/{bucket}")

    if not os.path.exists(root_location + f"/{bucket}/{thumb_id}"):
        os.mkdir(root_location + f"/{bucket}/{thumb_id}")

    # create thumbnail of specific size
    image = Image.open(root_location + filename)
    image.thumbnail(size, Image.ANTIALIAS)
    outfile_name = f"{root_location}/{bucket}/{thumb_id}/{thumb_id}_{size[0]}x{size[1]}.png"
    image.save(outfile_name)

    return outfile_name