"""
Local sandbox execution for Aegis.

Creates an isolated copy of the demo/ directory, applies proposed changes,
runs pytest, and generates a unified diff. All operations happen in a
temporary directory that is cleaned up after execution.

See docs/ARCHITECTURE.md for sandbox workflow details.
"""
import subprocess, tempfile, os, shutil, difflib

def dry_run(file_path: str, new_contents: str):
    """
    Execute a dry run in a local sandbox.
    
    Args:
        file_path: Path to file being modified (e.g., "config/app.yaml")
        new_contents: Proposed new file contents
        
    Returns:
        Dictionary with keys:
        - ok: bool - True if pytest passed
        - diff: str - Unified diff of changes
        - stdout: str - Last 400 chars of pytest stdout
        - stderr: str - Last 400 chars of pytest stderr
        
    Side effects:
        Creates and destroys a temporary directory
    """
    work = tempfile.mkdtemp()
    try:
        # copy demo -> work
        src = os.path.join(os.getcwd(), "demo")
        subprocess.run(["bash","-lc", f"cp -R '{src}/.' '{work}/'"], check=True)
        target = os.path.join(work, file_path)
        os.makedirs(os.path.dirname(target), exist_ok=True)

        old = ""
        if os.path.exists(target):
            with open(target,"r") as f: old = f.read()
        with open(target,"w") as f: f.write(new_contents)

        test = subprocess.run(["pytest","-q"], cwd=work, capture_output=True, text=True, timeout=30)
        diff = "\n".join(difflib.unified_diff(
            old.splitlines(), new_contents.splitlines(),
            fromfile=file_path, tofile=file_path
        ))
        ok = (test.returncode == 0)
        stdout = test.stdout[-400:] if test.stdout else ""
        stderr = test.stderr[-400:] if test.stderr else ""
        return {"ok": ok, "diff": diff, "stdout": stdout, "stderr": stderr}
    except subprocess.TimeoutExpired:
        return {"ok": False, "diff": "", "stdout": "", "stderr": "Tests timed out"}
    finally:
        shutil.rmtree(work, ignore_errors=True)
