import sys
import os
import olefile
import zlib
import re

# Set stdout/stderr to UTF-8 to prevent CP949 errors in the console
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

def extract_hwp_text(filepath):
    print(f"\n==========================================")
    print(f"File: {os.path.basename(filepath)}")
    print(f"==========================================")
    if not os.path.exists(filepath):
        print(f"File not found: {filepath}")
        return
        
    try:
        f = olefile.OleFileIO(filepath)
        dirs = f.listdir()
        
        is_hwp5 = False
        for d in dirs:
            if d[0] == "FileHeader":
                is_hwp5 = True
                break
                
        if not is_hwp5:
            print("Not a valid HWP5 file.")
            return
            
        sections = [d for d in dirs if d[0] == "BodyText"]
        # Sort sections by name Section0, Section1, etc.
        sections.sort(key=lambda x: int(re.findall(r'\d+', x[1])[0]) if re.findall(r'\d+', x[1]) else 0)
        
        full_text = []
        for section in sections:
            stream = f.openstream(section)
            data = stream.read()
            
            try:
                decompressed = zlib.decompress(data, -15)
            except Exception:
                decompressed = data
                
            try:
                text = decompressed.decode("utf-16le", errors="ignore")
                full_text.append(text)
            except Exception as e:
                print(f"Decode error in section {section}: {e}")
                
        text_content = "\n".join(full_text)
        
        # Remove common control characters but keep printable ones and spacing
        cleaned_lines = []
        for line in text_content.splitlines():
            line_cleaned = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', line)
            line_cleaned = line_cleaned.strip()
            if line_cleaned:
                cleaned_lines.append(line_cleaned)
                
        text_cleaned = "\n".join(cleaned_lines)
        
        # Print snippet of text
        print("--- Snippet of text (first 3000 chars) ---")
        print(text_cleaned[:3000])
        
        # Search for URLs
        print("\n--- Search Analysis ---")
        urls = re.findall(r'https?://[a-zA-Z0-9./_?=&%-]+', text_cleaned)
        print("Potential URLs/Endpoints:")
        for url in sorted(list(set(urls))):
            print("  ", url)
            
        # Write to txt file
        output_txt = filepath.replace(".hwp", "_extracted.txt")
        # Ensure target folder exists
        os.makedirs(os.path.dirname(output_txt), exist_ok=True)
        with open(output_txt, "w", encoding="utf-8") as out:
            out.write(text_cleaned)
        print(f"\nSaved full extracted text to: {output_txt}")
        
    except Exception as e:
        print(f"Error parsing {filepath}: {e}")

# Process downloads
extract_hwp_text(r'c:\Users\kang4\Downloads\OPEN API기술명세서_농업기상 기본 관측데이터V3_ver1.0.hwp')
extract_hwp_text(r'c:\Users\kang4\Downloads\OPEN API기술명세서_농업기상 상세 관측데이터V4_ver1.0.hwp')
