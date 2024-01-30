import os
import re
import datetime

fileNameStartWith = "SAN-"
rel_notes_dir = "RelNotes"
feature_notes_dir = "FeatureNotes"

def get_latest_version(rel_notes_dir):
    ### Pobiera najnowszą wersję z plików Rel jeśli już takie istnieją ###
    pattern = r"(\d+\.\d+\.\d+).md"
    versions = [re.search(pattern, filename).group(1) for filename in os.listdir(rel_notes_dir) if re.search(pattern, filename)]
    if versions:
        return max(versions, key=lambda v: tuple(map(int, v.split('.'))))
    return "0.0.0"

def increment_version(version, part):
    """(MAJOR, MINOR, PATCH)"""
    major, minor, patch = version.split(".")
    if part == "MAJOR":
        major = str(int(major) + 1)
        minor = "0"
        patch = "0"
    elif part == "MINOR":
        minor = str(int(minor) + 1)
        patch = "0"
    elif part == "PATCH":
        patch = str(int(patch) + 1)
    return f"{major}.{minor}.{patch}"

def get_new_version(rel_notes_dir, version=None):
    return version if version else increment_version(get_latest_version(rel_notes_dir), "PATCH")

def get_formatted_version_header(version):
    today = datetime.date.today().strftime("%d.%m.%Y")
    header = f"{version} - {today}"
    separator = "=" * 20
    return f"{header}\n{separator}\n\n"

def update_env_file(version):
    """Aktualizuje plik .env z nową wersją"""
    env_file_path = os.path.join(os.path.dirname(__file__), ".env")
    with open(env_file_path, "r") as file:
        lines = file.readlines()

    # Znajdź linię z APP_BE_VERSION i zaktualizuj wersje RelNotes
    for i, line in enumerate(lines):
        if line.startswith("APP_BE_VERSION"):
            lines[i] = f"APP_BE_VERSION=\"{version}\"\n"

    # Zapisz zaktualizowany plik .env
    with open(env_file_path, "w") as file:
        file.writelines(lines)

def merge_feature_notes():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    rel_notes_dir_path = os.path.join(script_dir, rel_notes_dir)
    feature_notes_dir_path = os.path.join(script_dir, feature_notes_dir)
    version = get_new_version(rel_notes_dir_path)

    entries = {}
    for filename in os.listdir(feature_notes_dir_path):
        if not filename.startswith(fileNameStartWith):
            continue
        
        filepath = os.path.join(feature_notes_dir_path, filename)
        with open(filepath, "r") as file:
            content = file.read().strip()
        
        category, notes = content.split("\n", 1)
        category = category[3:]  # Usuwanie znaku "# " z nagłówka kategorii
        
        if category not in entries:
            entries[category] = []
        entries[category].append(notes)
        
        os.remove(filepath)

    new_rel_notes_file = os.path.join(rel_notes_dir_path, f"{version}.md")

    with open(new_rel_notes_file, "w") as file:
        version_header = get_formatted_version_header(version)
        file.write(version_header)
        for category, notes_list in entries.items():
            #file.write(f"###{category}\n")
            if notes_list:  # Sprawdź, czy lista notatek nie jest pusta
                file.write(f"###{category}\n")
                for notes in reversed(notes_list):
                    file.write(f" {notes}")
            file.write("\n\n")

    print(f"Scalono zawartość plików FeatureNotes do {new_rel_notes_file} dla wersji {version}.")

    # Aktualizuj plik .env z nową wersją
    update_env_file(version)

if __name__ == "__main__":
    merge_feature_notes()