import os
from pathlib import Path
from dotenv import load_dotenv
import boto3
import cv2
from botocore.client import Config
import shutil

def download_file_from_s3(client, object_name):
    file_name, file_extension = object_name.split(".")
    temp_folder = Path("/tmp") / file_name
    temp_folder.mkdir(parents=True, exist_ok=True)

    download_target = Path(f"{temp_folder}/{file_name}.{file_extension}")
    client.download_file(
        os.environ.get("S3_BUCKET_NAME_CONVERTED"), object_name, download_target
    )
    return download_target


def extract_thumbnail(file_path: Path):
    cap = cv2.VideoCapture(file_path.__str__())
    if not cap.isOpened():
        print("Error opening video file")
        exit()
    
    file_name, _ = file_path.name.split(".")
    output_path = f"{os.path.dirname(file_path)}/{file_name}.jpg"

    middle_frame = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) // 2
    cap.set(cv2.CAP_PROP_POS_FRAMES, middle_frame)
    ret, frame = cap.read()

    if ret:
        cv2.imwrite(output_path, frame)
        print(f"Frame extracted and saved at {output_path}")
    else:
        print("Error reading frame")
    cap.release()
    cv2.destroyAllWindows()
    
    os.remove(file_path) # remove mp4 file

    return Path(output_path)


def upload_thumbnail_to_s3(client, file_path: Path):
    client.upload_file(
        file_path,
        os.environ.get("S3_BUCKET_NAME_THUMBNAIL"),
        file_path.name,
        ExtraArgs={"ContentType": "image/jpg", "ACL": "public-read"},
    )
    temp_folder = file_path.parent
    shutil.rmtree(temp_folder)
    return True


if __name__ == "__main__":
    load_dotenv()
    s3_client = boto3.client(
        "s3",
        region_name=os.environ.get("S3_REGION"),
        endpoint_url=os.environ.get("S3_RAW_ENDPOINT"),
        aws_access_key_id=os.environ.get("S3_ACCESS_KEY"),
        aws_secret_access_key=os.environ.get("S3_SECRET_ACCESS_KEY"),
        config=Config(s3={"addressing_style": "virtual"}, signature_version="v4"),
    )

    print("Start downloading")
    downloaded_path = download_file_from_s3(s3_client, "IMG_6376_2.mp4")
    print("Done downloading")
    
    print("Start extracting frame")
    result_path = extract_thumbnail(downloaded_path)
    print("Finished chunking")
    
    print("Start uploading")
    upload_thumbnail_to_s3(s3_client, result_path)
    print("Finished uploading")

    print("exited")