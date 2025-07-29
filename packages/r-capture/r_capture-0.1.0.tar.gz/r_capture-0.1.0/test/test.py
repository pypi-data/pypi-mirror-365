from r_capture import cap,from_argb
capture = cap(3,1200,800)
pixels = capture.pixels()
capture2 = from_argb(pixels,capture.width,capture.height)
capture2.width = 800
capture2.height = 600
capture2.show()
capture2.save("/capture.png")