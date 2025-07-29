import requests
import re
import subprocess
import tempfile
import os

def find_img_path(md: str) -> list:
    img_urls_md = re.findall(r"!\[.*?\]\((.*?)\)", md)
    img_urls_html = re.findall(r"<img.*?src=\"(.*?)\".*?>", md)
    return img_urls_md + img_urls_html

def img_path_is_url(img_path: str) -> bool:
    return bool(re.match(r"https?://", img_path))

def download_img(img_path: str, output: str) -> None:
    r = requests.get(img_path)
    img_name = img_path.split('/')[-1]

    if r.status_code == 200:
        with open(f"{output}/{img_name}", 'wb') as f:
            f.write(r.content)
        print(f"🔥 Downloaded {img_path} to {output}/{img_name}")
    
    else:
        print(f"💀 Failed to download {img_path} with status code {r.status_code}")

def upload_img_by_picgo(img_url: str) -> str:
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        r = requests.get(img_url)
        if r.status_code == 200:
            temp_file.write(r.content)
            temp_file_path = temp_file.name
        else:
            raise Exception(f"Failed to download image from {img_url}")

    try:
        result = subprocess.run(['picgo', 'upload', temp_file_path], capture_output=True, text=True, check=True)
        os.remove(temp_file_path)
        output = result.stdout.strip()
        # Extract the URL from the output
        for line in output.split('\n'):
            if line.startswith('http'):
                return line
        raise Exception(f"Could not find URL in picgo output: {output}")
    except subprocess.CalledProcessError as e:
        os.remove(temp_file_path)
        raise Exception(f"PicGo upload failed: {e.stderr}")
    except Exception as e:
        os.remove(temp_file_path)
        raise e

def is_github_repo_url(img_url: str, repo: str) -> bool:
    return repo in img_url


