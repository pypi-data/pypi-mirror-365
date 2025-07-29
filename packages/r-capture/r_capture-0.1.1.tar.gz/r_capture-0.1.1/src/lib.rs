use std::{thread::sleep, time::Duration};

use image::{imageops::FilterType, DynamicImage, ImageBuffer, Pixel};
use minifb::{Key, Window, WindowOptions};
use pyo3::{exceptions::PyTypeError, prelude::*};
use pyo3_stub_gen::{
    define_stub_info_gatherer,
    derive::{gen_stub_pyclass, gen_stub_pyfunction, gen_stub_pymethods},
};
use xcap::Monitor;

#[gen_stub_pyclass]
#[pyclass(subclass)]
struct Capture {
    capture: ImageBuffer<image::Rgba<u8>, Vec<u8>>,
    #[pyo3(get, set)]
    #[gen_stub()]
    width: usize,
    #[pyo3(get, set)]
    #[gen_stub()]
    height: usize,
}

impl Capture {
    fn inner_pic(&self) -> Vec<u32> {
        let mut screen = DynamicImage::ImageRgba8(self.capture.clone());
        screen = screen.resize_exact(self.width as u32, self.height as u32, FilterType::Lanczos3);
        let buffer = screen
            .to_rgba8()
            .pixels()
            .map(|p| {
                ((p.0[0] as u32) << 16)
                    | ((p.0[1] as u32) << 8)
                    | p.0[2] as u32
                    | (p.0[3] as u32) << 24
            })
            .collect::<Vec<u32>>();
        return buffer;
    }
}

#[gen_stub_pymethods]
#[pymethods]
impl Capture {
    fn show(&self) -> PyResult<bool> {
        let WIDTH = self.width;

        let HEIGHT = self.height;

        let buffer = self.inner_pic();
        let mut window = Window::new(
            "Notice - ESC to exit",
            WIDTH,
            HEIGHT,
            WindowOptions::default(),
        )
        .map_err(|e| PyErr::new::<PyTypeError, _>(format!("{}", e)))?;

        // Limit to max ~60 fps update rate
        window.set_target_fps(60);

        while window.is_open() && !window.is_key_down(Key::Escape) {
            // We unwrap here as we want this code to exit if it fails. Real applications may want to handle this in a different way
            window.update_with_buffer(&buffer, WIDTH, HEIGHT).unwrap();
        }
        Ok(true)
    }

    fn save(&self, filepath: String) -> PyResult<()> {
        let mut screen = DynamicImage::ImageRgba8(self.capture.clone());
        screen = screen.resize_exact(self.width as u32, self.height as u32, FilterType::Lanczos3);
        Ok(screen
            .save(filepath)
            .map_err(|e| PyErr::new::<PyTypeError, _>(format!("{}", e)))?)
    }

    fn pixels(&self) -> PyResult<Vec<u32>> {
        Ok(self.inner_pic())
    }
}
#[gen_stub_pyfunction]
#[pyfunction]
fn cap(delay: usize, width: usize, height: usize) -> PyResult<Capture> {
    sleep(Duration::from_secs(delay as u64));
    let monitors = Monitor::all().map_err(|e| PyErr::new::<PyTypeError, _>(format!("{}", e)))?;
    let monitor = monitors
        .into_iter()
        .find(|m| m.is_primary().unwrap_or(false));
    if monitor.is_none() {
        return Err(PyTypeError::new_err("primary monitor not found"));
    };
    let monitor = monitor.unwrap();
    let capture: ImageBuffer<image::Rgba<u8>, Vec<u8>> = monitor
        .capture_image()
        .map_err(|e| PyErr::new::<PyTypeError, _>(format!("{}", e)))?;
    return Ok(Capture {
        capture,
        width,
        height,
    });
}
#[gen_stub_pyfunction]
#[pyfunction]
fn from_argb(pixels: Vec<u32>, width: usize, height: usize) -> PyResult<Capture> {
    let mut buffer = Vec::new();
    for pixel in pixels.iter() {
        let red = ((*pixel >> 16) & 0xFF) as u8;
        let green = ((*pixel >> 8) & 0xFF) as u8;
        let blue = (*pixel & 0xFF) as u8;
        let alpha = ((*pixel >> 24) & 0xFF) as u8;
        buffer.push(red);
        buffer.push(green);
        buffer.push(blue);
        buffer.push(alpha);
    }
    let capture =
        ImageBuffer::<image::Rgba<u8>, Vec<u8>>::from_vec(width as u32, height as u32, buffer);
    if capture.is_none() {
        return Err(PyErr::new::<PyTypeError, _>("from_rgba error".to_owned()));
    }
    let capture = capture.unwrap();
    Ok(Capture {
        capture,
        width,
        height,
    })
}

/// A Python module implemented in Rust.
#[pymodule]
fn r_capture(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(cap, m)?)?;
    m.add_function(wrap_pyfunction!(from_argb, m)?)?;
    m.add_class::<Capture>()?;
    Ok(())
}
define_stub_info_gatherer!(stub_info);
