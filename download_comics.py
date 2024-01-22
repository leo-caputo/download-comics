import requests
import os
import argparse
from natsort import os_sorted
from selenium import webdriver
from selenium.common import WebDriverException
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from PIL import Image


def parse_args():
    parser = argparse.ArgumentParser(prog='download_comics.py', description='Download Comics from specific website')
    parser.add_argument('-n', '--name', help='Name of the comic', required=True)
    parser.add_argument('-o', '--output', required=True, help='Destination path, full path')
    return parser.parse_args()


def get_editions_path(url, comics_name):
    """Find the name of each comic edition and their respective path."""
    r = requests.get(url)
    response = r.text.split('\n')
    comics_path = []
    for line in response:
        if f'/Comic/{comics_name}/TPB' in line:
            start = line.find('/T') + 1
            # end = line.find('">')
            end = line.find('?')
            comics_path.append(line[start:end])

    return comics_path


def download_pages(url, output, comics_name):
    """Download the pages of the comic as .png files.
    url: The url of the comic without the path to the specific edition.
    output: Local path to save the files.
    comic_name: Name of the comic.
    """

    edition_path = get_editions_path(url, comics_name)

    cookie = {'name': 'rco_readType',
              'value': '1',
              'domain': 'readcomiconline.li', }

    try:
        options = webdriver.ChromeOptions()
        options.add_argument('headless')
        driver = webdriver.Chrome(options=options)

    except WebDriverException:
        print(f"Web drive for Chrome not found, please install it.")
    else:
        driver.get(url)
        driver.add_cookie(cookie)

        for i in range(len(edition_path)):
            print(f'Downloading: {edition_path[i]}...')
            full_url = f'{url}/{edition_path[i]}?s=&quality=hq'
            driver.get(full_url)
            html_content = driver.page_source.split('\n')
            urls = []

            for line in html_content:
                if "https://2.bp.blogspot.com" in line:
                    start = line.find('https')
                    end = line.find('" onerror')
                    urls.append(line[start:end])

            # Create the directory with the comics edition name
            new_dir = f"{output}/{edition_path[i]}"
            try:
                os.makedirs(new_dir)
                os.chdir(new_dir)
            except FileExistsError:
                os.chdir(new_dir)

            for j in range(len(urls)):
                response = requests.get(urls[j])
                # end = path[i].find('?')
                file_name = f'tpb-{j}.png'

                if os.path.exists(file_name):
                    pass
                else:
                    with open(file_name, 'wb') as file:
                        file.write(response.content)

        driver.quit()


def get_local_files(path):
    """List the comics pages on the local dir."""
    # Specify the directory path you want to enumerate
    # directory_path = f'{dir_path}'

    # Use os.listdir() to get a list of all files and subdirectories in the directory
    os.chdir(path)
    dirs = os_sorted(os.listdir())

    files = []
    i = 0
    for dir in dirs:
        files.append(os.listdir(dir))
        files[i] = os_sorted(files[i])
        i += 1

    return dirs, files


def create_pdf(output):
    """The PDF file name will be the same as the directory's name.
    dir_name: The specific directory name, not the full path.
    """
    os.chdir(output)
    local_dirs, image_paths = get_local_files(output)

    print(f'Sub directories: {local_dirs}')

    for i in range(len(local_dirs)):
        os.chdir(f'{output}/{local_dirs[i]}')
        print(f'Image paths: {image_paths[i]}')

        output_pdf = f'{local_dirs[i]}.pdf'

        c = canvas.Canvas(output_pdf, pagesize=letter)

        try:
            # Loop through image paths and add each image to the PDF
            for image_path in image_paths[i]:
                # Open the image
                img = Image.open(image_path)

                # Get the original image dimensions
                img_width, img_height = img.size

                # Define the maximum dimensions for the PDF (adjust as needed)
                max_width, max_height = letter

                # Calculate the scaling factor to fit the image within the page
                scaling_factor = min(max_width / img_width, max_height / img_height)

                # Calculate the new dimensions
                new_width = img_width * scaling_factor
                new_height = img_height * scaling_factor

                # Draw the image on the canvas
                c.drawImage(image_path, 0, 0, width=new_width, height=new_height)

                # Add a new page for the next image (optional)
                c.showPage()

            # Save the PDF file
            c.save()

            print(f'PDF created: {output_pdf}')

        except Exception as e:
            print(f'Error: {e}')


if __name__ == '__main__':

    args = parse_args()
    comics_name = args.name
    output = args.output
    url = f'https://readcomiconline.li/Comic/{comics_name}'

    download_pages(url, output, comics_name)
    create_pdf(output)
