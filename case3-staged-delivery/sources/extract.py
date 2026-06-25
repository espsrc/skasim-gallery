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
        
        # Result is the 3rd from last (or just the cleaned image).
        # Subagent said: Last 3 are result, PSF, residual.
        # So Result = matches[-3], PSF = matches[-2], Residual = matches[-1]
        if len(matches) >= 3:
            result_data = base64.b64decode(matches[-3])
            with open(os.path.join(target_dir, f"{aa_name}_result.png"), "wb") as f:
                f.write(result_data)
                
            psf_data = base64.b64decode(matches[-2])
            with open(os.path.join(target_dir, f"{aa_name}_psf.png"), "wb") as f:
                f.write(psf_data)

            residual_data = base64.b64decode(matches[-1])
            with open(os.path.join(target_dir, f"{aa_name}_residual.png"), "wb") as f:
                f.write(residual_data)
