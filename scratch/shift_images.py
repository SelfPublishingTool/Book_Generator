import os
import shutil

base_dir = '/Users/michael/Desktop/Self Publishing/Tool Creazione Libri in html/images'
temp_dir = '/Users/michael/Desktop/Self Publishing/Tool Creazione Libri in html/images_temp'

if not os.path.exists(temp_dir):
    os.makedirs(temp_dir)

# Move 36-90 to temp with shifted names
for i in range(36, 91):
    old_name = f'recipe_{i}.png'
    new_name = f'recipe_{i+1}.png'
    old_path = os.path.join(base_dir, old_name)
    new_path = os.path.join(temp_dir, new_name)
    
    if os.path.exists(old_path):
        shutil.move(old_path, new_path)
        print(f'Moved {old_name} to {new_name} in temp')

# Move them back to base
for filename in os.listdir(temp_dir):
    src = os.path.join(temp_dir, filename)
    dst = os.path.join(base_dir, filename)
    shutil.move(src, dst)
    print(f'Moved {filename} back to images/')

os.rmdir(temp_dir)
