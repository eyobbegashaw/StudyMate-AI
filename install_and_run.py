"""
Simple script to install dependencies and run StudyAI
"""
import os
import sys
import subprocess

def run_command(cmd, description):
    print(f"\n{'='*50}")
    print(f" {description}")
    print(f"{'='*50}")
    result = subprocess.run(cmd, shell=True)
    return result.returncode

def main():
    print("StudyAI - Installation and Setup")
    print("="*50)
    
    # Check Python version
    print(f"\nPython version: {sys.version}")
    
    # Install dependencies
    if run_command("pip install -r requirements.txt", "Installing dependencies") != 0:
        print("\nWarning: Some packages may have failed to install.")
        print("Trying alternative approach...")
        run_command("pip install pywebview python-docx python-pptx reportlab fpdf2 PyPDF2 pdfminer.six sentence-transformers==2.2.2 numpy packaging gpt4all nltk==3.8.1", "Installing core packages")
    
    # Run the app
    print("\n" + "="*50)
    print(" Starting StudyAI...")
    print("="*50 + "\n")
    
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    subprocess.run([sys.executable, "main.py"])

if __name__ == "__main__":
    main()
