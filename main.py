import os
from PIL import Image
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from fpdf import FPDF
import shutil

manga_url = input("Введите ссылку на мангу:")
start_chapter = int(input("Введите начальную главу: "))
end_chapter = int(input("Введите конечную главу: "))


IMAGES_DIR = "manga_images"
os.makedirs(IMAGES_DIR, exist_ok=True)


options = Options()
options.add_argument("--headless")
service = Service("./chromedriver")


def download_images(url, chapter):
    driver = webdriver.Chrome(service=service, options=options)
    driver.get(url)
    driver.implicitly_wait(10)
    elements = driver.find_elements(By.CLASS_NAME, "mx-auto")

    chapter_dir = os.path.join(IMAGES_DIR, f"chapter_{chapter}")
    os.makedirs(chapter_dir, exist_ok=True)

    image_paths = []
    for i, element in enumerate(elements):
        img_url = element.get_attribute("src")
        if img_url:
            response = requests.get(img_url, stream=True)
            image_path = os.path.join(chapter_dir, f"image_{i + 1}.jpeg")
            with open(image_path, "wb") as file:
                for chunk in response.iter_content(1024):
                    file.write(chunk)
            if os.path.getsize(image_path) > 0:
                image_paths.append(image_path)
            else:
                print(f"Файл пустой: {image_path}")

    driver.quit()
    return image_paths


def preprocess_images(image_paths):
    processed_paths = []
    for image_path in image_paths:
        try:
            with Image.open(image_path) as img:
                rgb_image = img.convert("RGB")
                processed_path = image_path.replace(".jpeg", "_processed.jpeg")
                rgb_image.save(processed_path, "JPEG")
                processed_paths.append(processed_path)
        except Exception as e:
            print(f"Ошибка обработки изображения {image_path}: {e}")
    return processed_paths


def create_pdf(image_paths, output_pdf):
    pdf = FPDF()
    for image_path in image_paths:
        pdf.add_page()
        pdf.image(image_path, x=0, y=0, w=210, h=297)
    pdf.output(output_pdf)


if __name__ == "__main__":
    for chapter in range(start_chapter, end_chapter + 1):
        url = f"{manga_url}/chapter/{chapter}"
        image_paths = download_images(url, chapter)
        processed_paths = preprocess_images(image_paths)
        pdf_name = f"manga_chapter_{chapter}.pdf"
        create_pdf(processed_paths, pdf_name)
    shutil.rmtree(IMAGES_DIR)
    print("Все главы успешно скачаны и сохранены в PDF!")
