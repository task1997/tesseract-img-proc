import cv2
import pyautogui
import numpy as np
import pytesseract
from PIL import Image, ImageEnhance, ImageFilter
import time

# Update with your Tesseract path if needed
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'


def preprocess_image(image, new_size=None):
    pil_image = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))

    # Enhance contrast
    enhancer = ImageEnhance.Contrast(pil_image)
    pil_image = enhancer.enhance(2)

    # Convert to grayscale
    pil_image = pil_image.convert('L')

    # Apply a filter to sharpen the image
    pil_image = pil_image.filter(ImageFilter.SHARPEN)

    # Resize image if new_size is provided
    if new_size:
        pil_image = pil_image.resize(new_size, Image.LANCZOS)  # Use "LANCZOS" directly

    # Convert back to OpenCV format
    processed_image = cv2.cvtColor(np.array(pil_image), cv2.COLOR_GRAY2BGR)
    return processed_image


def capture_screen(region=None):
    screenshot = pyautogui.screenshot(region=region)
    screenshot = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
    return screenshot


def extract_question(screenshot):
    processed_image = preprocess_image(screenshot, new_size=(120, 30))

    # Display the preprocessed image for debugging
    cv2.imshow('Preprocessed Question Image', processed_image)
    cv2.waitKey(1)  # Add a short delay to update the window

    config = '--psm 6'
    text = pytesseract.image_to_string(processed_image, config=config)
    return text


def extract_answer(screenshot, index):
    print(f"Extracting answer from region {index}")
    processed_image = preprocess_image(screenshot, new_size=(120, 30))

    # Display the preprocessed image for debugging
    window_name = f'Preprocessed Answer Image {index}'
    cv2.imshow(window_name, processed_image)
    cv2.waitKey(1)  # Add a short delay to update the window

    config = '--psm 6'
    text = pytesseract.image_to_string(processed_image, config=config)
    return text


def solve_addition(question):
    parts = question.split('+')
    try:
        num1 = int(parts[0].strip())
        num2 = int(parts[1].split('=')[0].strip())
        return num1 + num2
    except (ValueError, IndexError):
        return None


def find_and_click_answer(answer, answer_regions):
    answer_str = str(answer)
    for i, region in enumerate(answer_regions):
        print(f"Capturing answer region {i + 1}: {region}")
        button_screenshot = capture_screen(region=region)

        # Display the captured region for debugging
        cv2.imshow(f'Captured Answer Region {i + 1}', button_screenshot)
        cv2.waitKey(1)

        text = extract_answer(button_screenshot, i + 1)
        print(f"Extracted button text {i + 1}: {text.strip()}")
        if answer_str in text:
            left, top, width, height = region
            pyautogui.click(left + width / 2, top + height / 2, button='left')  # Ensure left button is used
            print(f"Clicked on the answer: {answer_str}")
            return
    else:
        print(f"Answer {answer_str} not found in provided regions")


def main_loop():
    while True:
        question_region = (860, 450, 120, 30)  # Updated to the correct question coordinates
        answer_regions = [
            (860, 480, 120, 30),  # First answer button
            (860, 510, 120, 30),  # Second answer button
            (860, 540, 120, 30)  # Third answer button
        ]

        question_screenshot = capture_screen(region=question_region)

        # Show the captured question region for testing
        cv2.imshow('Captured Question Region', question_screenshot)

        question = extract_question(question_screenshot)
        print(f"Extracted question: {question.strip()}")
        if '+' in question:
            answer = solve_addition(question)
            if answer is not None:
                find_and_click_answer(answer, answer_regions)
        time.sleep(1)  # Adjust the delay as needed

    cv2.destroyAllWindows()


if __name__ == "__main__":
    main_loop()
