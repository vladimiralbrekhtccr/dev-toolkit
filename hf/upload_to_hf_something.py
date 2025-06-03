from huggingface_hub import HfApi
from pathlib import Path
import time
import concurrent.futures
import dotenv
import os

dotenv.load_dotenv()

# Set folder path and repository details
folder_path = Path("")
repo_name = ""
api = HfApi(token=os.getenv("HF_TOKEN"))

# Check if folder exists
if not folder_path.is_dir():
    print(f"Error: Folder does not exist at: {folder_path}")
    exit(1)

# Write README.md content to a temporary location
import tempfile
readme_content = """
"""
# Create README.md in a temporary directory
temp_readme = tempfile.NamedTemporaryFile(mode="w", suffix="_README.md", delete=False, encoding="utf-8")
temp_readme.write(readme_content)
temp_readme.close()
readme_path = Path(temp_readme.name)
print(f"README.md created at temporary location: {readme_path}")

# Check/create repository
try:
    api.repo_info(repo_id=repo_name, repo_type="model")
    print(f"Repository {repo_name} exists")
except Exception:
    print(f"Creating repository {repo_name}...")
    api.create_repo(repo_id=repo_name, repo_type="model", private=True)

# Function to upload a single file with retries
def upload_file_with_retry(file_path):
    max_retries = 3
    retry_delay = 60
    
    # Determine the path in repo (use README.md for the temporary readme file)
    if file_path.name.endswith("_README.md"):
        path_in_repo = "README.md"
    else:
        path_in_repo = file_path.name
    
    for attempt in range(max_retries):
        try:
            api.upload_file(
                path_or_fileobj=str(file_path),
                path_in_repo=path_in_repo,
                repo_id=repo_name,
                repo_type="model"
            )
            print(f"File {path_in_repo} uploaded successfully")
            return True
        except Exception as e:
            print(f"Upload failed for {path_in_repo} (attempt {attempt + 1}/{max_retries}): {e}")
            if attempt < max_retries - 1:
                print(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
    
    print(f"Max retries reached. Upload failed for {path_in_repo}")
    return False

# Get list of files to upload, excluding the global_step11355 folder
files_to_upload = [readme_path]  # Start with the temporary README.md
for item in folder_path.glob('*'):
    if item.is_file():
        files_to_upload.append(item)
    elif item.is_dir() and item.name == "global_step11355":
        print(f"Skipping folder: {item.name}")
        continue
    # If you want to include other directories, you can add logic here

print(f"Found {len(files_to_upload)} files to upload (including README.md)")

# Upload files in parallel using ThreadPoolExecutor
max_workers = 8  # Adjust based on your network capacity
print(f"Uploading with {max_workers} concurrent workers")

with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
    results = list(executor.map(upload_file_with_retry, files_to_upload))

# Report results
success_count = results.count(True)
print(f"Upload complete: {success_count}/{len(files_to_upload)} files uploaded successfully")

# Clean up temporary README file
import os
try:
    os.unlink(readme_path)
    print(f"Temporary README file cleaned up: {readme_path}")
except Exception as e:
    print(f"Warning: Could not clean up temporary file {readme_path}: {e}")
