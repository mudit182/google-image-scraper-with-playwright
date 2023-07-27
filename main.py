import os

import asyncio

from GoogleImageScraper import find_image_urls, save_images

async def scrape_task(
        search_key: str,
        number_of_images: int,
        max_missed: int,
        headless: bool,
        min_resolution,
        max_resolution,
        keep_filenames,
    ):
    image_urls = await find_image_urls(
        search_key,
        number_of_images,
        max_missed,
        headless
    )
    await save_images(
        image_urls,
        image_save_format='jpg',
        images_dir_path=os.path.join('photos', search_key),
        keep_filenames=keep_filenames,
        image_file_prefix=search_key,
        min_resolution=min_resolution,
        max_resolution=max_resolution
    )

#Run each search_key in a separate async task
async def main():
    #Define file path
    images_dir_path = os.path.normpath(os.path.join(os.getcwd(), 'photos'))

    #Removes duplicate strings from search_keys
    #Add new search key into array ['cat','t-shirt','apple','orange','pear','fish']
    search_keys = list(set(['lettuce', 'spinach']))

    #Parameters
    number_of_images = 10                # Desired number of images
    min_resolution = (0, 0)             # Minimum desired image resolution
    max_resolution = (9999, 9999)       # Maximum desired image resolution
    max_missed = 10                     # Max number of failed images before exit
    headless = True                     # True = No Chrome GUI
    number_of_workers = 1               # Number of workers used
    keep_filenames = False              # Keep original URL image filenames

    # await scrape_task(
    #     search_keys[0],
    #     number_of_images,
    #     max_missed,
    #     headless,
    #     min_resolution,
    #     max_resolution,
    #     keep_filenames
    # )

    tasks = [
        scrape_task(
            search_key,
            number_of_images,
            max_missed,
            headless,
            min_resolution,
            max_resolution,
            keep_filenames
        ) for search_key in search_keys
    ]
    # # waits for all tasks to finish
    results = await asyncio.gather(*tasks)
    return results

if __name__ == '__main__':
    asyncio.run(main())