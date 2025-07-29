import click
import glob
import os
import pathlib
import json
import dimg4md.img4 as img4

@click.group()
def cli():
    pass

@cli.command(name='download', help='Download images from Markdown file.')
@click.option('--file', default='myPythonProject', help='The markdown file to download images from.')
@click.option('--output', help='The output directory to save the images.')
@click.option('--rewrite', default=False, is_flag=True, help='Rewrite the markdown file with the new image urls.')
@click.option('--force', default=False, is_flag=True, help='Force to download all the images from the Markdown file.')
def download(file, output, rewrite, force):

    os.makedirs(output, exist_ok=True)

    exist_files_in_output = glob.glob(f"{output}/*")
    exist_files_in_output = [pathlib.Path(file).name for file in exist_files_in_output]

    with open(f"{file}", 'r') as f: md_file = f.read()
    img_paths = img4.find_img_path(md_file) # find img paths from the markdown file

    # check if the img path is a url
    img_paths = [img_path for img_path in img_paths if not img4.img_path_is_url(img_path)]
    
    for img_path in img_paths:
        if not force and img_path.split('/')[-1] in exist_files_in_output:
            print(f"🔥 Skipping {img_path} because it already exists in {output}")
        else:
            img4.download_img(img_path, output)
        
        md_file = md_file.replace(img_path, f"{output}/{img_path.split('/')[-1]}")
            

    if rewrite:
        print(f"📓 Rewriting {file} with the new image urls")
        with open(f"{file}", 'w') as f: f.write(md_file)

def setup_picgo_config():
    picgo_config = {
        "picBed": {
            "current": "github",
            "uploader": "github",
            "github": {
                "repo": os.getenv("PICGO_GITHUB_REPO"),
                "token": os.getenv("PICGO_GITHUB_TOKEN"),
                "path": os.getenv("PICGO_GITHUB_PATH"),
                "customUrl": os.getenv("PICGO_GITHUB_CUSTOM_URL", ""),
                "branch": os.getenv("PICGO_GITHUB_BRANCH")
            }
        }
    }

    if not all([picgo_config['picBed']['github']['repo'], picgo_config['picBed']['github']['token'], picgo_config['picBed']['github']['path'], picgo_config['picBed']['github']['branch']]):
        raise click.UsageError("Missing one or more required environment variables: PICGO_GITHUB_REPO, PICGO_GITHUB_TOKEN, PICGO_GITHUB_PATH, PICGO_GITHUB_BRANCH")

    config_path = os.path.expanduser("~/.picgo/config.json")
    os.makedirs(os.path.dirname(config_path), exist_ok=True)
    with open(config_path, 'w') as f:
        json.dump(picgo_config, f)

def cleanup_picgo_config():
    config_path = os.path.expanduser("~/.picgo/config.json")
    if os.path.exists(config_path):
        os.remove(config_path)

@cli.command(name='upload', help='Upload web images to GitHub via PicGo.')
@click.option('--file', required=True, help='The markdown file to process.')
@click.option('--rewrite', default=False, is_flag=True, help='Rewrite the markdown file with the new image urls.')
def upload(file, rewrite):
    try:
        setup_picgo_config()
        github_repo = os.getenv("PICGO_GITHUB_REPO")

        with open(file, 'r') as f:
            md_file = f.read()

        img_paths = img4.find_img_path(md_file)

        changed = False
        for img_path in img_paths:
            if img4.img_path_is_url(img_path) and not img4.is_github_repo_url(img_path, github_repo):
                try:
                    new_url = img4.upload_img_by_picgo(img_path)
                    md_file = md_file.replace(img_path, new_url)
                    changed = True
                    print(f"✅ Replaced {img_path} with {new_url}")
                except Exception as e:
                    print(f"❌ Failed to upload {img_path}: {e}")

        if rewrite and changed:
            with open(file, 'w') as f:
                f.write(md_file)
            print(f"📓 Rewrote {file} with updated image URLs.")

    finally:
        cleanup_picgo_config()

if __name__ == '__main__':
    cli()
