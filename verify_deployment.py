import os
import sys
import time
import importlib.util

def print_status(message, success=True):
    icon = "[OK]" if success else "[MISSING]"
    print(f"{icon} {message}")

def check_file(path):
    if os.path.exists(path):
        print_status(f"Found required file: {path}")
        return True
    print_status(f"MISSING file: {path}", success=False)
    return False

def check_directory(path):
    if os.path.isdir(path):
        print_status(f"Found required directory: {path}")
        return True
    print_status(f"MISSING directory: {path}", success=False)
    return False

def check_api_key_in_app():
    # Since API key is hardcoded in app for now, checking file content
    try:
        with open("app_v2.py", "r", encoding="utf-8") as f:
            content = f.read()
            if '"GEMINI_API_KEY"' in content and "AIza" in content:
                print_status("API Key detected in app code")
                return True
            else:
                print_status("API Key might be missing or invalid format in app_v2.py", success=False)
                return False
    except Exception as e:
        print_status(f"Could not read app_v2.py: {e}", success=False)
        return False

def check_dependencies():
    required = ["streamlit", "google.generativeai", "fitz"]
    all_good = True
    for pkg in required:
        if importlib.util.find_spec(pkg) is None:
             # fitz is usually 'fitz' but import name is 'fitz' (pymupdf)
             if pkg == "fitz":
                 try:
                     import fitz
                 except ImportError:
                     print_status(f"MISSING dependency: {pkg} (install pymupdf)", success=False)
                     all_good = False
                     continue
             
             print_status(f"MISSING dependency: {pkg}", success=False)
             all_good = False
        else:
            print_status(f"Dependency installed: {pkg}")
    return all_good

def run_checks():
    print("\nDeepDive System Verification running...\n" + "="*40)
    
    files_ok = all([
        check_file("app_v2.py"),
        check_file(".streamlit/config.toml"),
        check_file("DEMO_SCRIPT.md"),
        check_directory("data")
    ])

    deps_ok = check_dependencies()
    api_ok = check_api_key_in_app()

    print("="*40)
    if files_ok and deps_ok and api_ok:
        print("\n[SUCCESS] SYSTEM HEALTHY: READINESS CONFIRMED")
        print("You can confidently start the demo.")
        return True
    else:
        print("\n[WARNING] SYSTEM ISSUES DETECTED")
        print("Please resolve the items marked with [MISSING] before presenting.")
        return False

if __name__ == "__main__":
    if not run_checks():
        sys.exit(1)
