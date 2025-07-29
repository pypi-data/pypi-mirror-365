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