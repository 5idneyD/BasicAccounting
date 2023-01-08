import cssmin
import sys

def minify(file):
    output = cssmin.cssmin(open(file).read())
    # print(output)
    with open("./" + file[0:file.index(".")]+".min.css", "w") as f:
        print("./" + file[0:file.index(".")]+".min.css", "w")
        f.write(output)

minify(sys.argv[1])

