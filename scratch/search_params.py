import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

def find_details(filename, method_name):
    print(f"\n==========================================")
    print(f"Searching for details of '{method_name}' in {filename}")
    print(f"==========================================")
    try:
        with open(filename, "r", encoding="utf-8") as f:
            content = f.read()
            
        pos = content.find(method_name)
        if pos == -1:
            print(f"Method '{method_name}' not found.")
            return
            
        snippet = content[pos:pos+4000]
        print(snippet)
    except Exception as e:
        print(f"Error reading file: {e}")

find_details(r'c:\Users\kang4\Downloads\OPEN API기술명세서_농업기상 상세 관측데이터V4_ver1.0_extracted.txt', "getWeatherTimeList4")
