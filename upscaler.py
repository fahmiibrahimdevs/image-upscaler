import cv2
import numpy as np
import gc
import io

class FontImageUpscaler:
    """
    Advanced Image Upscaler and Font/Text Sharpening Engine.
    Uses edge-preserving computer vision algorithms (Bilateral Filtering, Multi-scale Laplacian,
    Sobel Edge Refinement, CLAHE, and Lanczos-4 Interpolation) to sharpen blurry text and upscale images.
    """

    @staticmethod
    def process_image(
        image_bytes: bytes,
        scale_factor: float = 2.0,
        preset: str = "text_focus",
        sharpness: float = 2.0,
        contrast: float = 1.3,
        denoise: float = 1.0,
        edge_boost: float = 1.8,
        binarize: bool = False
    ) -> bytes:
        """
        Processes image bytes and returns upscaled, sharpened image bytes in PNG format.
        """
        # Load image from bytes
        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_UNCHANGED)
        
        if img is None:
            raise ValueError("Could not decode image file.")

        # Limit maximum output dimension to prevent RAM exhaustion (max 4096px)
        h, w = img.shape[:2]
        if max(w * scale_factor, h * scale_factor) > 4096:
            scale_factor = min(4096.0 / w, 4096.0 / h)

        # Handle alpha channel if present
        has_alpha = False
        alpha = None
        if len(img.shape) == 3 and img.shape[2] == 4:
            has_alpha = True
            alpha = img[:, :, 3]
            img_bgr = img[:, :, :3]
        elif len(img.shape) == 2:
            img_bgr = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
        else:
            img_bgr = img

        # Apply Preset Overrides if selected
        if preset == "text_focus":
            sharpness = max(sharpness, 2.4)
            contrast = max(contrast, 1.35)
            denoise = max(denoise, 1.0)
            edge_boost = max(edge_boost, 2.0)
        elif preset == "hybrid_photo_text":
            sharpness = max(sharpness, 1.6)
            contrast = max(contrast, 1.15)
            denoise = max(denoise, 0.8)
            edge_boost = max(edge_boost, 1.2)
        elif preset == "binarized_text":
            binarize = True
            sharpness = max(sharpness, 2.8)
            contrast = max(contrast, 1.5)

        # Step 1: Pre-Denoising (Edge-preserving noise cleanup to avoid sharpening noise)
        if denoise > 0:
            d_val = max(3, int(4 * denoise))
            sig_color = int(20 * denoise)
            sig_space = int(20 * denoise)
            img_bgr = cv2.bilateralFilter(img_bgr, d=d_val, sigmaColor=sig_color, sigmaSpace=sig_space)

        # Step 2: High Quality Upscaling (Lanczos-4 Interpolation)
        new_w = max(1, int(w * scale_factor))
        new_h = max(1, int(h * scale_factor))
        
        upscaled = cv2.resize(img_bgr, (new_w, new_h), interpolation=cv2.INTER_LANCZOS4)

        if has_alpha:
            alpha = cv2.resize(alpha, (new_w, new_h), interpolation=cv2.INTER_LANCZOS4)

        # Step 3: CLAHE (Contrast Limited Adaptive Histogram Equalization) for font visibility
        if contrast > 1.0:
            lab = cv2.cvtColor(upscaled, cv2.COLOR_BGR2LAB)
            l, a, b = cv2.split(lab)
            
            clip_lim = max(1.5, 2.5 * contrast)
            clahe = cv2.createCLAHE(clipLimit=clip_lim, tileGridSize=(8, 8))
            cl = clahe.apply(l)
            
            weight = min(0.8, (contrast - 1.0) * 0.7)
            l_enhanced = cv2.addWeighted(l, 1.0 - weight, cl, weight, 0)
            
            lab = cv2.merge((l_enhanced, a, b))
            upscaled = cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)

        # Step 4: Font Edge Gradient Boosting (Sobel & Laplacian Multi-scale Sharpener)
        if edge_boost > 0:
            gray = cv2.cvtColor(upscaled, cv2.COLOR_BGR2GRAY)
            
            sobelx = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
            sobely = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
            magnitude = cv2.magnitude(sobelx, sobely)
            norm_mag = cv2.normalize(magnitude, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
            
            _, edge_mask = cv2.threshold(norm_mag, 25, 255, cv2.THRESH_BINARY)
            edge_mask_blur = cv2.GaussianBlur(edge_mask, (3, 3), 0) / 255.0
            edge_mask_3ch = cv2.cvtColor(edge_mask_blur.astype(np.float32), cv2.COLOR_GRAY2BGR)
            
            laplacian = cv2.Laplacian(upscaled, cv2.CV_64F)
            sharpened_edges = cv2.addWeighted(upscaled.astype(np.float64), 1.0, -laplacian, edge_boost * 0.35, 0)
            sharpened_edges = np.clip(sharpened_edges, 0, 255).astype(np.uint8)
            
            upscaled = (upscaled * (1.0 - edge_mask_3ch) + sharpened_edges * edge_mask_3ch).astype(np.uint8)

        # Step 5: Unsharp Masking for General Crisp Typography
        if sharpness > 1.0:
            blur_kernel = (3, 3) if scale_factor <= 2 else (5, 5)
            blurred = cv2.GaussianBlur(upscaled, blur_kernel, 0)
            amount = (sharpness - 1.0) * 1.5
            upscaled = cv2.addWeighted(upscaled, 1.0 + amount, blurred, -amount, 0)
            upscaled = np.clip(upscaled, 0, 255).astype(np.uint8)

        # Step 6: Binarization (Optional high-contrast text cleaning)
        if binarize:
            gray_bin = cv2.cvtColor(upscaled, cv2.COLOR_BGR2GRAY)
            binary = cv2.adaptiveThreshold(
                gray_bin, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 4
            )
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
            binary = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)
            upscaled = cv2.cvtColor(binary, cv2.COLOR_GRAY2BGR)

        # Recombine alpha channel if present
        if has_alpha:
            final_img = cv2.merge((upscaled[:, :, 0], upscaled[:, :, 1], upscaled[:, :, 2], alpha))
        else:
            final_img = upscaled

        # Encode result to PNG bytes
        is_success, buffer = cv2.imencode(".png", final_img)
        if not is_success:
            raise RuntimeError("Failed to encode processed image.")

        result_bytes = buffer.tobytes()

        # Clean memory
        del img, upscaled, buffer, nparr
        gc.collect()

        return result_bytes
