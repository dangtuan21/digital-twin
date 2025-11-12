import os
import shutil
import zipfile
import subprocess


def main():
    print("Creating complete Lambda deployment package for Python 3.13...")

    # Clean up
    if os.path.exists("lambda-package"):
        shutil.rmtree("lambda-package")
    if os.path.exists("lambda-deployment.zip"):
        os.remove("lambda-deployment.zip")

    # Create package directory
    os.makedirs("lambda-package")

    print("Installing ALL dependencies for Python 3.13 Lambda runtime...")
    
    # Complete requirements including all missing modules
    temp_requirements = """
fastapi
mangum
openai
python-dotenv
pydantic>=2.0.0
pypdf
boto3
python-multipart
uvicorn
"""
    
    with open("temp_requirements.txt", "w") as f:
        f.write(temp_requirements.strip())

    try:
        # Use Python 3.13 Lambda runtime and install all dependencies with proper platform targeting
        subprocess.run([
            "docker", "run", "--rm", 
            "-v", f"{os.getcwd()}:/var/task",
            "--platform", "linux/x86_64",  # Ensure x86_64 architecture
            "--entrypoint", "",
            "public.ecr.aws/lambda/python:3.13",
            "sh", "-c", 
            """
            cd /var/task && \
            pip install --target lambda-package \
            -r temp_requirements.txt \
            --no-cache-dir \
            --disable-pip-version-check \
            --upgrade \
            --only-binary=:all: \
            --platform linux_x86_64 \
            --implementation cp \
            --python-version 3.13 \
            --abi cp313
            """
        ], check=True)
    finally:
        if os.path.exists("temp_requirements.txt"):
            os.remove("temp_requirements.txt")

    # Copy application files
    print("Copying application files...")
    
    # Copy the original lambda handler
    shutil.copy2("lambda_handler.py", "lambda-package/")
    print("  ✓ Copied lambda_handler.py")
    
    for file in ["server.py", "context.py", "resources.py"]:
        if os.path.exists(file):
            shutil.copy2(file, "lambda-package/")
            print(f"  ✓ Copied {file}")
    
    # Copy data directory
    if os.path.exists("data"):
        shutil.copytree("data", "lambda-package/data")
        print("  ✓ Copied data directory")

    # Copy me.txt if it exists
    if os.path.exists("me.txt"):
        shutil.copy2("me.txt", "lambda-package/")
        print("  ✓ Copied me.txt")

    # Create zip
    print("Creating zip file...")
    with zipfile.ZipFile("lambda-deployment.zip", "w", zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk("lambda-package"):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, "lambda-package")
                zipf.write(file_path, arcname)

    # Show package size
    size_mb = os.path.getsize("lambda-deployment.zip") / (1024 * 1024)
    print(f"✓ Created lambda-deployment.zip ({size_mb:.2f} MB)")

    # Verify pydantic_core native binary exists and is correct architecture
    print("\nVerifying pydantic_core binary...")
    pydantic_core_found = False
    for root, dirs, files in os.walk("lambda-package"):
        for file in files:
            if "_pydantic_core" in file and file.endswith(".so"):
                pydantic_core_path = os.path.join(root, file)
                print(f"✓ Found pydantic_core binary: {pydantic_core_path}")
                # Check if file command is available to verify architecture
                try:
                    result = subprocess.run(["file", pydantic_core_path], 
                                          capture_output=True, text=True, check=True)
                    print(f"  Architecture: {result.stdout.strip()}")
                    if "x86-64" in result.stdout or "x86_64" in result.stdout:
                        print("  ✓ Correct architecture for Lambda")
                    else:
                        print("  ⚠️  Architecture may not be compatible with Lambda")
                except (subprocess.CalledProcessError, FileNotFoundError):
                    print("  (Could not verify architecture - file command not available)")
                pydantic_core_found = True
                break
        if pydantic_core_found:
            break
    
    if not pydantic_core_found:
        print("❌ ERROR: pydantic_core native binary not found!")
        print("   This will cause 'No module named pydantic_core._pydantic_core' error in Lambda")
        return False

    # List other key installed packages
    print("\nChecking for other key dependencies...")
    key_modules = ["pypdf", "boto3", "openai", "fastapi", "mangum"]
    for module in key_modules:
        found = False
        for root, dirs, files in os.walk("lambda-package"):
            if module in root or any(module in file for file in files):
                print(f"✓ {module} found")
                found = True
                break
        if not found:
            print(f"⚠️  {module} not found")

    print("\n🚀 Complete Python 3.13 deployment package ready!")
    print("All dependencies should now be included")


if __name__ == "__main__":
    main()