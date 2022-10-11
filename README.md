# Public-Danbooru
Python script for searching artwork on Danbooru.
Danbooru is an image collection/archiving site for anime artwork.
Danbooru also collects nsfw content. When browsing Danbooru, always make sure that "Safe mode" is set to "Yes" on "https://danbooru.donmai.us/settings" to avoid seeing nsfw content.
This script is not intended for nsfw content.

## Usage
Create an account on "https://danbooru.donmai.us/users/new" or login on "https://danbooru.donmai.us/login".
Go to "https://danbooru.donmai.us/profile", at the bottom of the page, click "view" next to "API key".
Confirm your password and copy the API key. Don't share your API key with anyone.
Paste your API key in the "api_key" field and your username in the "username" field.

Right now you can search and retriev artwork by tags, artists, ids, pools, etc. Consult this cheatsheet for more help: "https://danbooru.donmai.us/wiki_pages/help%3Acheatsheet".
You can also retrieve your profile information with "get_profile_info()".
Lastly, you can save your search results in a csv and you can also save the artwork in a folder.

## Requirements
(PIP): requests, csv, random, re, os, PIL