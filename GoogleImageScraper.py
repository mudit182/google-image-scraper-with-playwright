from typing import List, Tuple
import os
import io

import httpx
from PIL import Image
from playwright.async_api._generated import Locator
from playwright.async_api import async_playwright

def google_images_url(search_key):
    return f'https://www.google.com/search?q={search_key}&source=lnms&tbm=isch&sa=X&ved=2ahUKEwie44_AnqLpAhUhBWMBHUFGD90Q_AUoAXoECBUQAw&biw=1920&bih=947'
    
async def find_image_urls(
    search_key='cat',
    number_of_images=1,
    max_missed=10,
    headless=False,
):
    """
        This function searches and return a list of image urls based on the search key.

        Example:
            image_urls = find_image_urls(image_path,search_key,number_of_photos)
    """
    print(f'[INFO] Gathering image links for {search_key}')
    image_urls=[]

    # Open playwright browser
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(
            headless=headless
        )
        page = await browser.new_page()

        # Open google images page with search query
        await page.goto(google_images_url(search_key))
        # Wait for images to load and get list of all image thumbnails
        image_thumbnail_css_selector = '[jsname="Q4LuWd"]'
        await page.locator(image_thumbnail_css_selector).first.wait_for(timeout=10_000, state='visible')
        candidate_images: List[Locator] = await page.locator(image_thumbnail_css_selector).all()

        images_checked_count = 0
        failed_images_count = 0
        is_image_open = False
        is_image_url_found = False

        while len(image_urls) < number_of_images and failed_images_count < max_missed and images_checked_count < len(candidate_images):
            # Scroll down
            load_more_images_button_selector = '[jsaction="Pmjnye"]'
            if await page.query_selector(load_more_images_button_selector):
                scroll_button: Locator = page.locator(load_more_images_button_selector).first
                if await scroll_button.is_visible():
                    await scroll_button.click(timeout=10_000)
                    await page.wait_for_timeout(3000)
                    candidate_images = await page.locator(image_thumbnail_css_selector).all()

            try:
                # Click on image thumbnail to show real image
                candidate_thumbnail = candidate_images[images_checked_count]
                await candidate_thumbnail.scroll_into_view_if_needed(timeout=10_000)
                await candidate_thumbnail.click(timeout=10_000)
                is_image_open = True
                # Wait for actual image to load
                actual_image_selectors_candidates = ['.n3VNCb','.iPVvYb','.r48jcc','.pT0Scc']
                loc = page.locator(actual_image_selectors_candidates[0])
                for actual_image_selector in actual_image_selectors_candidates[1:]:
                    loc = loc.or_(page.locator(actual_image_selector))
                try:
                    await loc.wait_for(timeout=10_000, state='visible')
                except Exception as e:
                    if not 'strict mode violation' in e.message:
                        raise e
                await page.wait_for_timeout(1000) # Comment out this step for faster url retrieval but higher failure rate
                actual_image_candidates = await loc.all()
                for actual_image_candidate in actual_image_candidates:
                    image_src = await actual_image_candidate.get_attribute('src', timeout=1000)
                    if image_src and 'http' in image_src and (not 'encrypted' in image_src):
                        image_urls.append(image_src)
                        is_image_url_found = True
                        break
            except Exception as e:
                print('[ERROR] Unexpected error:')
                print(e)

            # Reset loop states
            # Log error if url not found
            if is_image_url_found:
                is_image_url_found = False
            else:
                failed_images_count += 1
                print(f'[ERROR] Failed to retrieve url of {search_key} image {images_checked_count + 1}')
            # Close image if thumbnail was opened - needed until image_thumbnail_css_selector is improved to only select main images thumbnails
            if is_image_open:
                await candidate_thumbnail.click(timeout=10_000)
                is_image_open = False
            # Update image thumbnail count
            images_checked_count += 1
            # Get new count of loaded images after auto load
            candidate_images = await page.locator(image_thumbnail_css_selector).all()

        # await page.pause()
        await page.close()
        print(f'[INFO] Google search ended for {search_key}. Found {len(image_urls)} image urls.')
        return image_urls

async def save_images(
        image_urls: List[str],
        image_save_format='jpg',
        images_dir_path='photos',
        keep_filenames = False,
        image_file_prefix = 'image',
        min_resolution=(0, 0),
        max_resolution=(1920, 1080),
    ):
    #save images into file directory
    """
        This function takes in an array of image urls and saves it into the given image path/directory.
        Example:
            image_urls=['https://example_1.jpg','https://example_2.jpg']
            save_images(image_urls)

    """
    if not os.path.exists(images_dir_path):
        print(f'[INFO] Image dir path {images_dir_path} not found. Creating a new folder.')
        os.makedirs(images_dir_path)

    print(f'[INFO] Saving {image_file_prefix} images, please wait...')
    for index, image_url in enumerate(image_urls):
        image_resp = await download_image(image_url)
        if not image_resp:
            continue
        try:
            with Image.open(io.BytesIO(image_resp.content)) as image_from_web:
                is_image_resolution_valid = check_if_image_resolution_valid(image_from_web, min_resolution, max_resolution)
                if not is_image_resolution_valid:
                    print(f'[INFO] Skipping image as resolution is {image_from_web.size}')
                    continue
                image_name = f'{image_file_prefix}-{index}'
                image_path = save_image(image_from_web, images_dir_path, image_name, save_format=image_save_format)
                print(f'[INFO] {image_file_prefix} \t {index} \t Image saved at: {image_path}')
                image_from_web.close()
        except Exception as e:
            print(f'[ERROR] Failed to save downloaded image with url {image_url}. Error: ', e)
    print('--------------------------------------------------')
    print(f'[INFO] Downloading and saving {image_file_prefix} images completed. Please note that some photos may not have been downloaded as they were not in the correct format (e.g. jpg, jpeg, png)')


async def download_image(image_url: str):
    try:
        async with httpx.AsyncClient() as client:
            image_resp = await client.get(image_url, timeout=5)
            if image_resp.status_code == 200:
                return image_resp
            else:
                image_resp.raise_for_status()
    except Exception as e:
        print(f'[ERROR] Image download failed for url {image_url}. Error: ', e)
    return None


def check_if_image_resolution_valid(image: Image.Image, min_resolution: Tuple[int, int], max_resolution: Tuple[int, int]):
    image_resolution = image.size
    if image_resolution:
        if (
            image_resolution[0] >= min_resolution[0]and
            image_resolution[0] <= max_resolution[0] and
            image_resolution[1] >= min_resolution[1] and
            image_resolution[1] <= max_resolution[1]
        ):
            return True
    return False


def save_image(image: Image.Image, images_dir_path: str, image_name: str, save_format: str = None):
    image_original_format = image.format.lower()
    if not save_format or (save_format not in ['jpg', 'png', 'jpeg']):
        save_format = image_original_format
    image_filename = f'{image_name}.{save_format}'
    image_path = os.path.join(images_dir_path, image_filename)
    try:
        if image_original_format != save_format:
            image = image.convert('RGB')
    except Exception as e:
        image = image.convert('RGB')
    image.save(image_path)
    return image_path
