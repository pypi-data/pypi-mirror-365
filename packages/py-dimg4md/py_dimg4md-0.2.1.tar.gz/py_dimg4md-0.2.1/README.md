<div align="center">
    <img width="300px" src="image/cover.png">
</div>

# DIMG4MD

Many companies offer services that allow easy creation of Markdown on the web. However, when pasting images into their services, the images are not stored locally. Instead, they are stored in the cloud. If you need to automatically download the image and update the link in the Markdown, you can use this tool.

DIMG4MD provides two main functionalities:
1. **Download**: Download images from Markdown files to local storage
2. **Upload**: Upload external images to GitHub via PicGo and update Markdown links

## Installation

### Basic Installation (Download functionality only)

You can install the package via pip:
```bash
pip install py-dimg4md
```

### Full Installation (Download + Upload functionality)

For upload functionality, you need Node.js and PicGo. Install with the picgo extra:
```bash
pip install py-dimg4md[picgo]
```

Or you can install the package from source:
```bash
pip install git+https://github.com/hsiangjenli/pyimg4md.git
```

### Docker Installation (Recommended for Upload)

The easiest way to use the upload functionality is via Docker, which includes all dependencies:

```bash
docker pull pydimg4md
```

## Requirements

### For Download functionality:
- Python 3.8+

### For Upload functionality:
- Python 3.8+
- Node.js 14+
- PicGo CLI tool
- GitHub Personal Access Token

## Usage

### Download Command

Download images from Markdown file and optionally update local paths:

```bash
Usage: dimg download [OPTIONS]

  Download images from Markdown file.

Options:
  --file TEXT        The markdown file to download images from.
  --output TEXT      The output directory to save the images.
  --rewrite BOOLEAN  Rewrite the markdown file with the new image urls.
  --force BOOLEAN    Force to download all the images from the Markdown file.
  --help             Show this message and exit.
```

Example:
```bash
dimg download --file README.md --output ./images --rewrite
```

### Upload Command

Upload external images to GitHub via PicGo and update Markdown links:

```bash
Usage: dimg upload [OPTIONS]

  Upload web images to GitHub via PicGo.

Options:
  --file TEXT     The markdown file to process. [required]
  --rewrite BOOLEAN  Rewrite the markdown file with the new image urls.
  --help          Show this message and exit.
```

#### Environment Variables for Upload

The upload command requires the following environment variables:

- `PICGO_GITHUB_REPO`: (Required) GitHub repository in format `username/repo`
- `PICGO_GITHUB_TOKEN`: (Required) GitHub Personal Access Token
- `PICGO_GITHUB_PATH`: (Required) Path for images in repository, e.g., `images/`
- `PICGO_GITHUB_BRANCH`: (Required) Repository branch, e.g., `main`
- `PICGO_GITHUB_CUSTOM_URL`: (Optional) Custom domain for images

#### Docker Usage Example

```bash
docker run --rm -it \
  -v $(pwd):/app \
  -e PICGO_GITHUB_REPO="username/reponame" \
  -e PICGO_GITHUB_TOKEN="your_personal_access_token" \
  -e PICGO_GITHUB_PATH="images/" \
  -e PICGO_GITHUB_BRANCH="main" \
  pydimg4md \
  upload --file README.md --rewrite
```

#### Local Usage Example

First, set up environment variables:
```bash
export PICGO_GITHUB_REPO="username/reponame"
export PICGO_GITHUB_TOKEN="your_personal_access_token"
export PICGO_GITHUB_PATH="images/"
export PICGO_GITHUB_BRANCH="main"
```

Then run the upload command:
```bash
dimg upload --file README.md --rewrite
```
