import json
import os

import requests
import typer
from requests import Response

## Declare and initialize a set representing the tag sets that the downloader
# should download content with.
tag_sets: set = {}

def read_tag_sets() -> set:
    """Reads the provided tag_sets.txt file to gain a reference for the tag
    sets to download against.

    ## Notes
    - A potential enhancement being considered is to provide the user an option
    to specify a custom tag sets file (rather than using the default
    tag_sets.txt file that the tool provides). However, this option is not
    currently available.
    - Another potential enhancement being considered is to provide the user an
    option to *not* sort the tag set list. The sorting behavior included in the
    logic at present is included more as a convenience (it can provide users a
    reference for how far in their tag set list the tool is when running), but
    isn't necessary for the tool to run. In addition, the sorting behavior
    could create performance issues when reading in tag set lists for extremely
    large lists (though this is likely more of an edge case than something that
    the typical user would experience).
    """
    # Declare and initialize a localized version of tag_sets that can be
    # manipulated independent of the "main" set of tag sets.
    tag_sets: set = {}

    # Try to open the tag sets file (tag_sets.txt by default), read its
    # contents in as a set, clean the values read into the set, and sort the
    # set to prepare it for use by the core downloader logic. If the tag sets
    # file does not exist, create it. This file is necessary to provide the
    # tool context for what to download.
    try:
        with open('tag_sets.txt', 'r') as tag_sets_file:
            # Read the tag set file's contents in as a set.
            tag_sets = set(tag_sets_file.readlines())

            # Clean the values in the tag sets set by removing newlines. This will
            # make it easier to use these values in the core downloader logic.
            for tag_set in tag_sets:
                # Remove the raw value from the set.
                tag_sets.remove(tag_set)

                # Replace any escaped newlines with the empty string in the tag
                # set.
                tag_set = tag_set.replace('\n', '')

                # Added the cleaned version of the tag set back to tag_sets for
                # further processing.
                tag_sets.add(tag_set)

            # Sort the set of tag sets.
            tag_sets = sorted(tag_sets)
    except FileNotFoundError:
        with open('tag_sets.txt', 'w') as tag_sets_file:
            tag_sets_file.write()

    return tag_sets
        
def download_posts(tag_set: str) -> None:
    """Downloads posts associated with a provided tag set.

    ## Arguments
    - `tag_set`: A string representing the set of tags to use to search for
    posts. The format of this string matches what a user would enter if
    searching for posts directly on e621.

    ## Notes
    - A potential enhancement being considered is to provide the user an option
    to download posts without specifying any tags, which would effectively
    download the latest posts on e621, regardless of how they're tagged.
    - Another potential enhancement being considered is to provide the user an
    option to specify a custom download location (where downloaded posts are
    stored on the local machine).
    """
    # Check whether a "downloads" folder exists in the current working
    # directory and create it if it doesn't. This directory needs to be present
    # before downloading post data to avoid an error being thrown while
    # downloading(in the event that the directory doesn't exist).
    if not os.path.exists(os.path.join(os.getcwd(), 'downloads')):
        os.mkdir('downloads')

    # Replace spaces in the tag set with the URL encoded version of the space
    # character. While this isn't necessarily necessary, it makes requests to
    # the e621 API more proper.
    tag_set_string: str = tag_set.replace(' ', '%20')

    # Declare and initialize variable to track which page of posts the
    # downloader is requesting content from and whether there are more posts to
    # process. These are necessary because the e621 API returns content data in
    # pages rather than all at once, and does not indicate whether there is a
    # "next" page.
    page_number: int = 1
    more_posts_available: bool = True

    # Decare and initialize a dictionary of headers to include with the content
    # request to e621. This *should* just be the user agent that identifies the
    # tool to e621 (per e621's requirement for user agent information for API
    # requests).
    headers: dict = {'User-Agent': 'darkroastcreative/e621-content-collector'}

    # Process the request, paging through the set of available posts until
    # either the page limit is reached or the tool detects that there are no
    # more posts available for the specified tag set.
    while page_number < 751 and more_posts_available:
        # Submit a request to the e621 API for posts matching the provided tag set and page number.
        response: Response = requests.get(url=f'https://e621.net/posts.json?tags={tag_set_string}&page={page_number}', headers=headers)

        # Process the response from the e621 API.
        if response.status_code == 200:
            # Parse the response JSON from the e621 API to a Python object for
            # processing. This line grabs justs the content of the "posts" property
            # of the response because that's the part needed to parse and download
            # the posts referenced in the response.
            posts = json.loads(response.content)['posts']

            if len(posts) > 0:
                more_posts_available = True
            else:
                more_posts_available = False

            # Iterate over the set of posts, extracting post metadata (ID, URL, tag
            # information) and downloading each post.
            for post in posts:
                # Extract post ID. This will be used to name the downloaded file.
                id: int = post['id']

                # Extract the URL for the source content (image, video, animation,
                # etc.). The content at this URL will be the content downloaded to
                # represent the post.
                url: str = post['file']['url']

                # Extract tag information. This doesn't have an immediate purpose,
                # as posts returned by the API match the provided tag sets, but
                # will be used to filter out posts in later versions of this tool. 
                tags_general = post['tags']['general']
                tags_artist = post['tags']['artist']
                tags_contributor = post['tags']['contributor']
                tags_copyright = post['tags']['copyright']
                tags_character = post['tags']['character']
                tags_species = post['tags']['species']
                tags_meta = post['tags']['meta']
                tags_lore = post['tags']['lore']

                # Check whether the URL value is null and proceed to download
                # the post content if not. This logic is present to account for
                # an oddity with the e621 API in which sometimes posts are
                # included without URL values.
                if url is not None:
                    # Get the file extension for the post. This will be used to
                    # determine which file extension to use when downloading/saving
                    # the post content locally.
                    file_extension: str = url.split('.')[-1]

                    # Get the post data. This will be written to the local machine.
                    post_data: bytes = requests.get(url).content

                    # Write the post file to the local machine.
                    with open(os.path.join(os.getcwd(), 'downloads', f'{id}.{file_extension}'), 'wb') as post_file:
                        post_file.write(post_data)

            # Increment the page number variable so the tool can proceed to
            # check for the next page of posts.
            page_number += 1

def run_download() -> None:
    """Reads in the contents of tag_sets.txt and proceeds to download posts
    matching each provided tag set.

    ## Notes
    - Options will likely be added to this method at a later time to allow the
    user more control over download behavior.
    """
    # Read the set of tag sets to download against from tag_sets.txt.
    tag_sets = read_tag_sets()

    # For each tag set, download the posts matching the tag set.
    for tag_set in tag_sets:
        download_posts(tag_set=tag_set)