import cssmin
import sys

def minify(file):
    output = cssmin.cssmin(open("./static/styles/" + file).read())
    # print(output)
    with open("./static/styles/" + file[0:file.index(".")]+".min.css", "w") as f:
        # print("./static/" + file[0:file.index(".")]+".min.css", "w")
        f.write(output)

minify(sys.argv[1])
print("./static/styles/" + sys.argv[1][0:sys.argv[1].index(".")]+".min.css" + " produced")

