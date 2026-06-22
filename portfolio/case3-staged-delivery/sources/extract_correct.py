import os
import re
import base64

source_dir = "."
target_dir = "../images"

files = {
    'AA0.5': 'weblog_05.html',
    'AA1': 'weblog_1.html',
    'AA2': 'weblog_2.html',
    'AAstar': 'weblog_star.html',
    'AA4': 'weblog_4.html'
}

for aa_name, filename in files.items():
    filepath = os.path.join(source_dir, filename)
    if not os.path.exists(filepath):
        print(f"Skipping {filename}")
        continue
    
    with open(filepath, 'r') as f:
        content = f.read()
    
    # find all img src="data:image/png;base64,..."
    pattern = r'<img\s+[^>]*src="data:image/png;base64,([^"]+)"'
    matches = re.findall(pattern, content)
    
    print(f"{aa_name}: found {len(matches)} images")
    
    if matches:
        # Layout is the first one
        layout_data = base64.b64decode(matches[0])
        with open(os.path.join(target_dir, f"{aa_name}_layout.png"), "wb") as f:
            f.write(layout_data)
        
        # Result (MFS-image) is the 2nd to last, matches[-2]
        if len(matches) >= 2:
            result_data = base64.b64decode(matches[-2])
            with open(os.path.join(target_dir, f"{aa_name}_result.png"), "wb") as f:
                f.write(result_data)
