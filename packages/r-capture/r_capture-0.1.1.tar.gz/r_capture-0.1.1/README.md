# r-capture

A Python package for screen capturing and image manipulation, published on PyPI.

## Installation

Install via pip:
```bash
pip install r-capture
```

## Features

- **Screen Capture**: Capture the current screen.
- **Image Display**: Display the captured image.
- **Custom Dimensions**: Adjust the width and height of the captured image by modifying the `width` and `height` attributes of the `Capture` class instance.
- **Pixel Data**: Retrieve the pixel data of the captured image as a list of integers (`list[int]`).
- **Import Pixel Data**: Create a `Capture` object from pixel data.
- **Save Images**: Save the image stored in the `Capture` object.

## Usage Example

```python
import r_capture

# Capture the screen with a delay of 3 seconds
capture = r_capture.cap(delay=3,width=1200,height=800)

# Show the captured image
capture.show()

# Get pixel data as a list of integers
pixels = capture.pixels()
print(pixels)

#Create Capture object using pixels list
capture = r_capture.from_argb(pixels=pixels,width=1200,height=800)

# Resize image to specified resolution
capture.width = 800
capture.height = 600

# Save the captured image
capture.save("screenshot.png")
```

## Contributing

Feel free to open an Issue or submit a Pull Request to improve the project.

## License

MIT