def extract_text(frames, ocr):
    full_text = ""

    for frame in frames:
        try:
            result = ocr.ocr(frame)
            if result and result[0]:
                for line in result[0]:
                    if len(line) > 1 and line[1] and len(line[1]) > 0:
                        text_line = line[1][0].strip()
                        if text_line:  # Only add non-empty lines
                            full_text += text_line + "\n"
        except Exception as e:
            print(f"OCR error on frame {frame}: {e}")
            continue

    # Clean up the text
    full_text = full_text.strip()

    # If no text was extracted, return a message
    if not full_text:
        return "No text could be extracted from the video frames. Please ensure the video contains clear, readable text."

    return full_text
