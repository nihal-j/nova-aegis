"""
Modal cloud sandbox execution for Aegis.

Runs sandbox execution in Modal's cloud infrastructure. Clones the specified
repository, applies changes, runs pytest, and returns results. This allows
testing against real repositories without local setup.

Requires:
- Modal package installed
- Modal token configured (modal token set)
- DEMO_REPO environment variable set
- Modal app deployed (run: modal deploy app.modal_runner)

See docs/WALKTHROUGH.md for Modal setup instructions.
"""
import modal, subprocess, tempfile, os, shutil, difflib

image = modal.Image.debian_slim().pip_install("pytest","pyyaml","gitpython")
app = modal.App("aegis")

@app.function(image=image, timeout=180)
def dry_run_repo(repo_url: str, file_path: str, new_contents: str):
    """
    Execute a dry run in Modal cloud sandbox.
    
    Args:
        repo_url: Git repository URL to clone
        file_path: Path to file being modified
        new_contents: Proposed new file contents
        
    Returns:
        Dictionary with keys:
        - ok: bool - True if pytest passed
        - diff: str - Unified diff of changes
        - stdout: str - Last 400 chars of pytest stdout
        - stderr: str - Last 400 chars of pytest stderr
        
    Side effects:
        Clones repository and runs tests in Modal cloud
    """
    work = tempfile.mkdtemp()
    try:
        subprocess.run(["git","clone","--depth","1",repo_url,work], check=True, capture_output=True)
        target = os.path.join(work, file_path)
        os.makedirs(os.path.dirname(target), exist_ok=True)

        old = ""
        if os.path.exists(target):
            with open(target,"r") as f: old = f.read()
        with open(target,"w") as f: f.write(new_contents)

        test = subprocess.run(["pytest","-q"], cwd=work, capture_output=True, text=True, timeout=60)
        diff = "\n".join(difflib.unified_diff(
            old.splitlines(), new_contents.splitlines(),
            fromfile=file_path, tofile=file_path
        ))
        ok = (test.returncode == 0)
        stdout = test.stdout[-400:] if test.stdout else ""
        stderr = test.stderr[-400:] if test.stderr else ""
        return {"ok": ok, "diff": diff, "stdout": stdout, "stderr": stderr}
    except subprocess.TimeoutExpired:
        return {"ok": False, "diff": "", "stdout": "", "stderr": "Modal tests timed out"}
    finally:
        shutil.rmtree(work, ignore_errors=True)
