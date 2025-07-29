from ipa_scanner import ipa_extractor as ipa
from ipa_scanner import excel_analyser as analyser
import os
import shutil

USERNAME = None
PASSWORD = None
DOWNLOAD_DIR = ""

def set_credentials():
    global USERNAME, PASSWORD
    USERNAME, PASSWORD = ipa.cli_entrypoint()
    # Add your logic here

def run_extractor():
    global DOWNLOAD_DIR
    DOWNLOAD_DIR = os.path.join(os.getcwd(), "downloads")

    # Ensure the directory exists; create if not
    if not os.path.exists(DOWNLOAD_DIR):
        os.makedirs(DOWNLOAD_DIR)
    else:
        # Clear existing files/subdirectories
        for filename in os.listdir(DOWNLOAD_DIR):
            file_path = os.path.join(DOWNLOAD_DIR, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.remove(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print(f"❌ Failed to delete {file_path}: {e}")

    print("Running IPA Extractor...")
    DOWNLOAD_DIR = ipa.run_bom_download(USERNAME, PASSWORD, DOWNLOAD_DIR)

def run_analyser():
    global DOWNLOAD_DIR
    print("Running IPA Analyser...")
    analyser.analyze_csv(DOWNLOAD_DIR)
    # Add your logic here

def main():
    while True:
        print("\n📦 Welcome to IPA Scanner!")
        print("1. Set User Name & Password")
        print("2. Run IPA Extractor")
        print("3. Run Analyser")
        print("4. Quit")

        choice = input("Enter your choice (1-4): ").strip()

        if choice == "1":
            set_credentials()
        elif choice == "2":
            run_extractor()
        elif choice == "3":
            run_analyser()
        elif choice == "4":
            print("👋 Exiting IPA Scanner. Goodbye!")
            break
        else:
            print("❌ Invalid choice. Please enter a number between 1 and 4.")

if __name__ == "__main__":
    main()
