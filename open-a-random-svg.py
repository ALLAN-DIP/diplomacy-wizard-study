# a script that keeps in browser after entering in a inifinite loop

import webbrowser
import random
import sys
import os

# get from argv
svg_paths = os.listdir(sys.argv[1])
svg_paths = [path for path in svg_paths if path.split("_")[2][-1] == "M"]
random.seed(0)
random.shuffle(svg_paths)

good_files = []
i = 0
while True:
    try:
        result = webbrowser.open_new_tab("file:///" + os.path.join(os.getcwd(), sys.argv[1], svg_paths[i]))
        print(f"Opened {svg_paths[i]}", result)
        k = input("Press Enter to continue...[Y to save]") # wait for user input
        if k.upper() == "Y":
            good_files.append(svg_paths[i])
        i += 1
        i %= len(svg_paths)
    except Exception as e:
        print("Exiting...", e)
        break

print(good_files)
#save the good files
with open("good_files.txt", "w") as f:
    f.write("\n".join(good_files))

