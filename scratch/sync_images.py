import os
import shutil

src_dir = '/Users/michael/Desktop/Self Publishing/Tool Creazione Libri in html/images ok'
dst_dir = '/Users/michael/Desktop/Self Publishing/Tool Creazione Libri in html/images'

if not os.path.exists(dst_dir):
    os.makedirs(dst_dir)

for filename in os.listdir(src_dir):
    if filename.endswith('.png'):
        recipe_num = filename.split('.')[0]
        new_filename = f'recipe_{recipe_num}.png'
        src_path = os.path.join(src_dir, filename)
        dst_path = os.path.join(dst_dir, new_filename)
        shutil.copy2(src_path, dst_path)
        print(f'Copied {filename} to {new_filename}')
