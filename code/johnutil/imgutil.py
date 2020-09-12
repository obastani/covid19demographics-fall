import base64
from io import BytesIO
from PIL import Image
import pytesseract

# Given a selenium canvas object and the driver, get the OCR scan of its contents
def getCanvas(x, driver, flipBW = False):
    b64 = driver.execute_script("return arguments[0].toDataURL('image/png').substring(21);", x)
    img = Image.open(BytesIO(base64.b64decode(b64)))
    if flipBW:
        pix = img.load()
        cols, rows = img.size  # indexing is backward...
        for r in range(rows):
            for c in range(cols):
                if pix[c,r][:3] == (255, 255, 255):
                    pix[c,r] = (0, 0, 0, 255)
                elif pix[c,r][:3] == (0, 0, 0):
                    pix[c,r] = (255, 255, 255, 255)
    return pytesseract.image_to_string(img)

# Given a selenium canvas object and the driver, Returns pixel counts for each color in the canvas
def getColors(x, driver):
    b64 = driver.execute_script("return arguments[0].toDataURL('image/png').substring(21);", x)
    img = Image.open(BytesIO(base64.b64decode(b64)))
    pix = img.load()
    cols, rows = img.size  # indexing is backward...
    colors = {}
    for r in range(rows):
        for c in range(cols):
            if not pix[c,r] in colors:
                colors[pix[c,r]] = 0
            colors[pix[c,r]] += 1
    return colors

# Given a selenium canvas object with a horizonal barplot, a bar color, and a driver, get pct in each bar
def getGraph(x, color, driver):
    b64 = driver.execute_script("return arguments[0].toDataURL('image/png').substring(21);", x)
    img = Image.open(BytesIO(base64.b64decode(b64)))
    pix = img.load()
    cols, rows = img.size  # indexing is backward...
    widths = []
    currWid = -1
    for r in range(rows):
        thisWidth = max([-1] + [x for x in range(cols) if pix[x,r] == color])
        if thisWidth < 0 and currWid >= 0:
            widths.append(currWid)
        elif currWid >= 0 and thisWidth != currWid:
            raise Exception("Changing bar width")
        currWid = thisWidth
    if currWid >= 0:
        widths.append(currWid)
    return [x / sum(widths) * 100 for x in widths]

# Given a selenium canvas object with a horizonal stacked bar, a list of colors, and a driver, get pct in each bar
def getStackedGraph(x, colors, driver):
    b64 = driver.execute_script("return arguments[0].toDataURL('image/png').substring(21);", x)
    img = Image.open(BytesIO(base64.b64decode(b64)))
    pix = img.load()
    cols, rows = img.size  # indexing is backward...
    widths = []
    for color in colors:
        thisCols = []
        for c in range(cols):
            for r in range(rows):
                if pix[c,r] == color:
                    thisCols.append(c)
                    break
        widths.append(max(thisCols)-min(thisCols)+1)
    return [x / sum(widths) * 100 for x in widths]
