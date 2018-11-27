import glob
import uuid

import boto3
import spotipy
from selenium import webdriver

BUCKET_NAME = 'reverse-image'
GOOGLE_IMAGE_ENDPOINT = 'https://images.google.com/searchbyimage?image_url='
S3_ENDPOINT = 's3.us-east-2.amazonaws.com/reverse-image/'

def main():
    # Global resources
    sp = spotipy.Spotify(open('spotify_token').read().strip())
    s3 = boto3.resource('s3')
    bucket = s3.Bucket(BUCKET_NAME)
    browser = webdriver.Firefox()

    # Albums to add
    albums = []

    # Iterate through images and add to library
    for filename in glob.glob('images/*'):
        # Create UUID and upload to S3 bucket
        key = uuid.uuid4().hex
        print "Uploading:", filename
        bucket.upload_file(filename, key, ExtraArgs={'ACL':'public-read'})
        
        # Search on Google images
        search_url = GOOGLE_IMAGE_ENDPOINT + S3_ENDPOINT + key
        print "Search URL:", search_url
        browser.get(search_url)
        # TODO: scrape from side bar if available
        element = browser.find_elements_by_xpath("//a[@class='fKDtNb']")

        try:
            text = element[0].text
            print "Image search result:", text
            result = text.replace('cover', '').replace('album', '').replace('vinyl', '').replace('lyrics', '').replace('lp', '').replace('couldn t', "couldn't").replace('deluxe', '').replace('cd', '').replace('-', '')
            print "Found album:", result
            
            # Search for album on Spotify
            music = sp.search(q=result, limit=1, type='album')
            if music['albums']['items'] != []:
                print music
                artists = [artist['name'] for artist in music['albums']['items'][0]['artists']]
                print "Artists:", ', '.join(artists)
                print "Album:", music['albums']['items'][0]['name']
                album = music['albums']['items'][0]['id']
                albums.append(album)
            else:
                music = sp.search(q=result, limit=1)
                print music
                artists = [artist['name'] for artist in music['tracks']['items'][0]['album']['artists']]
                print "Artists:", ', '.join(artists)
                print "Album:", music['tracks']['items'][0]['album']['name']
                album = music['tracks']['items'][0]['album']['id']
                albums.append(album)
        except IndexError:
            print "Could not find match:" + filename

        print

    # Add Spotify tracks to playlist
    # playlist = sp.user_playlist_create('1242456154', 'SpotRex', public=False)
    # sp.user_playlist_add_tracks('me', playlist_id, tracks, position=None)
    # user_playlist_add_tracks(
    sp.current_user_saved_albums_add(albums)

    browser.quit()

if __name__ == '__main__':
    main()
