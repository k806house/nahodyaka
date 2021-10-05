import glob
import os
import random
import sys
import zipfile

dir = os.path.abspath(sys.argv[1])
limit = int(sys.argv[2])

files = glob.glob(dir + "/**/*.jpg", recursive=True)
files = random.sample(files, k=limit)

zipf = zipfile.ZipFile('images.zip', 'w', zipfile.ZIP_DEFLATED)
for f in files:
    zipf.write(f, os.path.basename(f))
