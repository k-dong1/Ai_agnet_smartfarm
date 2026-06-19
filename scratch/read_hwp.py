import re
import os

def extract_strings_from_hwp(filepath):
    print(f"\n--- Checking File: {os.path.basename(filepath)} ---")
    if not os.path.exists(filepath):
        print(f"File does not exist: {filepath}")
        return
        
    try:
        with open(filepath, 'rb') as f:
            content = f.read()
        # Decode as utf-16le and utf-8 to extract readable text
        # HWP files often use UTF-16LE for body text
        text_utf16 = content.decode('utf-16le', errors='ignore')
        text_utf8 = content.decode('utf-8', errors='ignore')
        
        combined_text = text_utf8 + "\n" + text_utf16
        
        # Check for URLs
        urls = re.findall(r'https?://[a-zA-Z0-9./_?=&%-]+', combined_text)
        print("Potential URLs found:")
        for url in sorted(list(set(urls))):
            if "api" in url or "rda" in url or "Weather" in url:
                print("  ", url)
                
        # Check for parameter keywords (case-insensitive)
        keywords = [
            "search_Year", "search_Month", "Page_No", "Page_Size", 
            "serviceKey", "ServiceKey", "stn_Cd", "stnCd", "obsrDiv",
            "GnrlWeather", "InsttWeather", "stn_Code", "stn_Cd"
        ]
        print("\nKeyword search matches:")
        for kw in keywords:
            matches = len(re.findall(kw, combined_text, re.IGNORECASE))
            print(f"  {kw}: {matches} matches")
            
        # Print snippet around URL or parameter-like assignments
        # Look for things like key = value or similar
        print("\nSample snippets containing keywords:")
        lines = combined_text.splitlines()
        printed = 0
        for line in lines:
            if any(kw.lower() in line.lower() for kw in keywords if len(kw) > 3) and len(line.strip()) > 5:
                # Clean line from non-printable characters for clean terminal view
                clean_line = "".join(ch for ch in line if ch.isprintable() or ch.isspace())
                if len(clean_line.strip()) > 10:
                    print("  ", clean_line.strip()[:150])
                    printed += 1
                    if printed > 20:
                        break
                        
    except Exception as e:
        print(f"Error reading file: {e}")

# Read both files
extract_strings_from_hwp(r'c:\Users\kang4\Downloads\OPEN API기술명세서_농업기상 기본 관측데이터V3_ver1.0.hwp')
extract_strings_from_hwp(r'c:\Users\kang4\Downloads\OPEN API기술명세서_농업기상 상세 관측데이터V4_ver1.0.hwp')
