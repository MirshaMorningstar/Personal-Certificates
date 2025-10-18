import git
import os
import shutil
import stat
from pathlib import Path

def handle_remove_readonly(func, path, exc):
    """
    Error handler for Windows readonly files during rmtree operations
    """
    if os.path.exists(path):
        # Make the file writable and retry
        os.chmod(path, stat.S_IWRITE)
        func(path)

def safe_rmtree(path):
    """
    Safely remove directory tree on Windows, handling readonly files
    """
    if os.path.exists(path):
        try:
            shutil.rmtree(path, onerror=handle_remove_readonly)
        except Exception as e:
            print(f"Warning: Could not completely remove {path}: {e}")

def clone_and_push_folder_fixed(repo_url, local_folder_path, clone_dir="temp_repo", commit_message="Add new files", branch_name="main"):
    """
    Fixed version: Clone repository, add folder contents, and push back
    
    Args:
        repo_url (str): GitHub repository URL
        local_folder_path (str): Path to folder you want to push
        clone_dir (str): Temporary directory name for cloning
        commit_message (str): Commit message
        branch_name (str): Target branch name
    """
    try:
        # Ensure we're working with absolute paths
        local_folder_path = os.path.abspath(local_folder_path)
        clone_dir = os.path.abspath(clone_dir)
        
        print(f"Local folder: {local_folder_path}")
        print(f"Clone directory: {clone_dir}")
        
        # Remove existing clone directory if it exists
        if os.path.exists(clone_dir):
            print("Removing existing clone directory...")
            safe_rmtree(clone_dir)
        
        # Clone the repository
        print(f"Cloning repository from {repo_url}...")
        repo = git.Repo.clone_from(repo_url, clone_dir)
        print("Repository cloned successfully")
        
        # Switch to target branch
        try:
            if branch_name in [branch.name for branch in repo.branches]:
                repo.git.checkout(branch_name)
                print(f"Switched to existing branch: {branch_name}")
            elif f"origin/{branch_name}" in [ref.name for ref in repo.refs]:
                repo.git.checkout('-b', branch_name, f'origin/{branch_name}')
                print(f"Created and switched to branch: {branch_name}")
            else:
                print(f"Using current branch (could not find {branch_name})")
        except Exception as e:
            print(f"Branch switching warning: {e}")
        
        # Copy contents of your folder into the cloned repository (not the folder itself)
        print(f"Copying contents from {local_folder_path} to {clone_dir}")
        
        # Copy each item in the source folder to the repository root
        for item in os.listdir(local_folder_path):
            source_item = os.path.join(local_folder_path, item)
            target_item = os.path.join(clone_dir, item)
            
            if os.path.isdir(source_item):
                if os.path.exists(target_item):
                    print(f"Merging directory: {item}")
                    # Merge directories
                    shutil.copytree(source_item, target_item, dirs_exist_ok=True)
                else:
                    print(f"Copying directory: {item}")
                    shutil.copytree(source_item, target_item)
            else:
                print(f"Copying file: {item}")
                shutil.copy2(source_item, target_item)
        
        print("Files copied successfully")
        
        # Add all changes
        repo.git.add(all=True)
        print("Files added to staging area")
        
        # Check for changes and commit
        if repo.is_dirty() or repo.untracked_files:
            repo.index.commit(commit_message)
            print(f"Changes committed: {commit_message}")
            
            # Push to remote
            try:
                origin = repo.remote(name='origin')
                origin.push()
                print("Successfully pushed to remote repository")
            except git.exc.GitCommandError as e:
                print(f"Push failed: {e}")
                print("You may need to configure authentication or check repository permissions")
        else:
            print("No changes to commit")
            
    except git.exc.GitCommandError as e:
        print(f"Git command error: {e}")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        # Guaranteed cleanup with proper error handling
        print("Performing cleanup...")
        safe_rmtree(clone_dir)
        print("Cleanup completed")

# Alternative: Push to existing repository without cloning
def push_to_existing_repo(local_folder_path, repo_path, commit_message="Add files", branch_name="main"):
    """
    Push contents of a folder to an existing local git repository
    """
    try:
        local_folder_path = os.path.abspath(local_folder_path)
        repo_path = os.path.abspath(repo_path)
        
        print(f"Source folder: {local_folder_path}")
        print(f"Target repo: {repo_path}")
        
        # Initialize repository object
        repo = git.Repo(repo_path)
        
        # Switch to target branch
        if branch_name in [branch.name for branch in repo.branches]:
            repo.git.checkout(branch_name)
            print(f"Switched to branch: {branch_name}")
        
        # Copy contents (not the folder itself)
        for item in os.listdir(local_folder_path):
            source_item = os.path.join(local_folder_path, item)
            target_item = os.path.join(repo_path, item)
            
            print(f"Processing: {item}")
            
            if os.path.isdir(source_item):
                if os.path.exists(target_item):
                    # Merge directories
                    shutil.copytree(source_item, target_item, dirs_exist_ok=True)
                else:
                    shutil.copytree(source_item, target_item)
            else:
                shutil.copy2(source_item, target_item)
        
        # Add all changes
        repo.git.add(all=True)
        print("Files staged successfully")
        
        # Commit and push
        if repo.is_dirty() or repo.untracked_files:
            repo.index.commit(commit_message)
            print(f"Committed: {commit_message}")
            
            origin = repo.remote(name='origin')
            origin.push()
            print("Pushed to remote repository")
        else:
            print("No changes to commit")
            
    except Exception as e:
        print(f"Error: {e}")

# Usage examples
if __name__ == "__main__":
    # Option 1: Clone and push (recommended for your case)
    REPO_URL = "https://github.com/MirshaMorningstar/Personal-Certificates.git"
    LOCAL_FOLDER = "C:/Users/DELL/Desktop/CAREER-CREDENTIALS/CERTIFICATES"
    
    print("Starting clone and push operation...")
    clone_and_push_folder_fixed(
        repo_url=REPO_URL,
        local_folder_path=LOCAL_FOLDER,
        clone_dir="temp_repo_fixed",  # Different temp directory name
        commit_message="Add certificates and career credentials",
        branch_name="main"
    )
    
    # Option 2: If you already have a local repository
    # LOCAL_REPO_PATH = r"C:\path\to\your\local\git\repository"
    # push_to_existing_repo(LOCAL_FOLDER, LOCAL_REPO_PATH)
