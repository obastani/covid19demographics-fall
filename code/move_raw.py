import time
import os
import shutil

SECONDS_IN_DAY = 24 * 60 * 60

src = "../../covid19demographics-fall/"
dst = "../../covid19demographics/raw/"

now = time.time()
before = now - 7 * (SECONDS_IN_DAY)

def last_mod_time(fname):
    return os.path.getmtime(fname)

unwanted = [".git", ".vscode", "code", "code_alex", "code_uncensor", "logs", "safegraph", "SouthKoreaCensus", "unacast", "US_Census", ".gitignore", "README", "nytimes"]

for folder in os.listdir(src):
    raw_dir = src + folder + "/raw/"
    try:
        if folder in unwanted:
            continue
        for file in os.listdir(raw_dir):
            path = raw_dir + file
            if last_mod_time(path) <  before:
                dst_fname = dst + folder + "/" + file
                print(raw_dir + file)
                shutil.move(path, dst_fname)
                print("Moving " + folder)
    except:
        print("No dir: " + raw_dir)
    
    # res = input("Continue? y or n")
    # if (res.lower()).strip() == "y":
    #     continue
    # else:
    #     break
    