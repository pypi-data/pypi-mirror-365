import json
import os
import subprocess
from pathlib import Path

# Configuration
INPUT_FILE = "data/US.json"
OUTPUT_DIR = "data/split_data"
MAX_SIZE_MB = 20
MAX_SIZE_BYTES = MAX_SIZE_MB * 1024 * 1024  # 20 MB in bytes
RIPGREP_PATH = "rg"  # Ensure ripgrep is installed and in PATH
REQUIRED_FIELDS = [
    "bin", "brand", "type", "category", "issuer",
    "phone", "website", "country_code", "country_code_alpha3", "country_name"
]

def validate_json_with_ripgrep(file_path: str) -> bool:
    """Validate JSON file using ripgrep with multiline mode."""
    try:
        # Regex to match an indented JSON array of objects with required fields
        regex = r'^\[\n\s*(?:\{\n\s*"bin"\s*:\s*"[^"]*"\s*,\n\s*"brand"\s*:\s*"[^"]*"\s*,\n\s*"type"\s*:\s*"[^"]*"\s*,\n\s*"category"\s*:\s*"[^"]*"\s*,\n\s*"issuer"\s*:\s*"[^"]*"\s*,\n\s*"phone"\s*:\s*"[^"]*"\s*,\n\s*"website"\s*:\s*"[^"]*"\s*,\n\s*"country_code"\s*:\s*"[^"]*"\s*,\n\s*"country_code_alpha3"\s*:\s*"[^"]*"\s*,\n\s*"country_name"\s*:\s*"[^"]*"\n\s*\}(?:,\n\s*\{\n\s*"bin"\s*:\s*"[^"]*"\s*,\n\s*"brand"\s*:\s*"[^"]*"\s*,\n\s*"type"\s*:\s*"[^"]*"\s*,\n\s*"category"\s*:\s*"[^"]*"\s*,\n\s*"issuer"\s*:\s*"[^"]*"\s*,\n\s*"phone"\s*:\s*"[^"]*"\s*,\n\s*"website"\s*:\s*"[^"]*"\s*,\n\s*"country_code"\s*:\s*"[^"]*"\s*,\n\s*"country_code_alpha3"\s*:\s*"[^"]*"\s*,\n\s*"country_name"\s*:\s*"[^"]*"\n\s*\})*,\n\s*)*\]\s*$'
        result = subprocess.run(
            [RIPGREP_PATH, "--multiline", "--quiet", regex, file_path],
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        if result.returncode == 0:
            print(f"Validated {file_path} as a valid indented JSON array")
            return True
        else:
            print(f"ripgrep validation failed for {file_path}: {result.stderr}")
            return False
    except subprocess.CalledProcessError as e:
        print(f"ripgrep validation failed for {file_path}: {e.stderr}")
        return False
    except FileNotFoundError:
        print("ripgrep not found. Please install ripgrep (`rg`) and ensure it's in PATH.")
        return False

def fallback_json_validation(file_path: str) -> bool:
    """Fallback validation by parsing JSON."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        if not isinstance(data, list):
            print(f"Fallback validation failed: {file_path} is not a JSON array")
            return False
        for entry in data:
            if not all(field in entry for field in REQUIRED_FIELDS):
                print(f"Fallback validation failed: {file_path} has entries missing required fields")
                return False
        print(f"Fallback validation passed for {file_path}")
        return True
    except Exception as e:
        print(f"Fallback JSON validation failed for {file_path}: {str(e)}")
        return False

def get_approximate_json_size(data: list) -> int:
    """Estimate the size of JSON data in bytes with indentation."""
    return len(json.dumps(data, indent=2).encode('utf-8'))  # Include indentation

def validate_entry(entry: dict) -> bool:
    """Validate that an entry has all required fields."""
    if not isinstance(entry, dict):
        return False
    return all(field in entry for field in REQUIRED_FIELDS)

def split_json_file():
    """Split US.json into multiple files, each under MAX_SIZE_BYTES, with proper formatting."""
    # Create output directory if it doesn't exist
    Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)
    
    # Read the input JSON file
    try:
        with open(INPUT_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
        if not isinstance(data, list):
            print("Error: US.json must contain a JSON array")
            return
        print(f"Loaded {INPUT_FILE} with {len(data)} entries")
    except Exception as e:
        print(f"Error reading {INPUT_FILE}: {str(e)}")
        return

    # Initialize variables for splitting
    current_chunk = []
    current_size = 0
    chunk_index = 1
    total_entries = len(data)
    valid_entries = 0

    for i, entry in enumerate(data):
        # Validate entry structure
        if not validate_entry(entry):
            print(f"Warning: Skipping invalid entry at index {i}: {entry}")
            continue

        valid_entries += 1
        # Estimate size of the current entry with indentation
        entry_size = len(json.dumps([entry], indent=2).encode('utf-8'))
        
        # If adding the entry exceeds MAX_SIZE_BYTES, save the current chunk
        if current_size + entry_size > MAX_SIZE_BYTES - 1024 * 100 and current_chunk:  # 100 KB buffer
            output_file = Path(OUTPUT_DIR) / f"split{chunk_index}.json"
            try:
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(current_chunk, f, indent=2)  # Pretty-print with indentation
                file_size = output_file.stat().st_size / (1024 * 1024)
                print(f"Wrote {output_file} with {len(current_chunk)} entries ({file_size:.2f} MB)")
                
                # Validate the output file
                if not validate_json_with_ripgrep(str(output_file)):
                    print(f"Warning: {output_file} failed ripgrep validation, checking with fallback")
                    if not fallback_json_validation(str(output_file)):
                        print(f"Error: {output_file} is not a valid JSON array")
                
                # Reset for the next chunk
                current_chunk = [entry]
                current_size = entry_size
                chunk_index += 1
            except Exception as e:
                print(f"Error writing {output_file}: {str(e)}")
                return
        else:
            current_chunk.append(entry)
            current_size += entry_size

        # Log progress
        if (i + 1) % 1000 == 0 or i + 1 == total_entries:
            print(f"Processed {i + 1}/{total_entries} entries, {valid_entries} valid")

    # Write the final chunk if it exists
    if current_chunk:
        output_file = Path(OUTPUT_DIR) / f"split{chunk_index}.json"
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(current_chunk, f, indent=2)  # Pretty-print with indentation
            file_size = output_file.stat().st_size / (1024 * 1024)
            print(f"Wrote {output_file} with {len(current_chunk)} entries ({file_size:.2f} MB)")
            
            # Validate the output file
            if not validate_json_with_ripgrep(str(output_file)):
                print(f"Warning: {output_file} failed ripgrep validation, checking with fallback")
                if not fallback_json_validation(str(output_file)):
                    print(f"Error: {output_file} is not a valid JSON array")
        except Exception as e:
            print(f"Error writing {output_file}: {str(e)}")
            return

    print(f"Completed splitting. Generated {chunk_index} files in {OUTPUT_DIR}, {valid_entries}/{total_entries} entries valid")

if __name__ == "__main__":
    # Verify ripgrep is available
    try:
        subprocess.run([RIPGREP_PATH, "--version"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print("ripgrep found, proceeding with split...")
        split_json_file()
    except FileNotFoundError:
        print("Error: ripgrep (`rg`) not found. Please install it and ensure it's in PATH.")
    except Exception as e:
        print(f"Error checking ripgrep: {str(e)}")