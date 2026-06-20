import sys
import re

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

def extract_methods(filepath):
    print(f"\nExtracting method names from {filepath}...")
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
        
        # Look for words starting with getWeather and potentially ending with 4 or similar
        methods = re.findall(r'getWeather[A-Za-z0-9_]+', content)
        unique_methods = sorted(list(set(methods)))
        print("Found methods:")
        for m in unique_methods:
            print("  ", m)
    except Exception as e:
        print("Error:", e)

extract_methods(r'c:\Users\kang4\Downloads\OPEN API기술명세서_농업기상 상세 관측데이터V4_ver1.0_extracted.txt')
