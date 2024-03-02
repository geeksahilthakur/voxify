# gen.py
import openai
import requests
import json
import time
import random
from moviepy.editor import ImageClip, concatenate_videoclips, AudioFileClip
from PIL import Image
import os

openai.api_key = "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"


def chat_with_gpt(prompt):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message['content'].strip()
    except Exception as e:
        print("An error occurred:", str(e))
        return "Sorry, something went wrong."


if __name__ == "__main__":
    topic = input("Enter the topic: ")

    paragraph_title_prompt = "act as a professional content writer write a short one minute paragraph in the form of paragraph title = " + topic
    gpt_response_title = chat_with_gpt(paragraph_title_prompt)

    print("Paragraph Title:", gpt_response_title)

    unsplash_keywords_prompt = "i want use stock images from the unsplash. so provide some 12 relevant keyword to find exact same images on unsplash topic =" + topic
    gpt_response_keywords = chat_with_gpt(unsplash_keywords_prompt)

    unsplash_keywords_list = gpt_response_keywords.split("\n")

    print("Relevant Keywords:")
    for keyword in unsplash_keywords_list:
        print(keyword)

    responses_list = [gpt_response_title] + unsplash_keywords_list
    print("Responses stored in a list:", responses_list)


def generate_audio_from_text(text):
    url = "https://large-text-to-speech.p.rapidapi.com/tts"
    payload = {"text": text}

    headers = {
        'content-type': "application/json",
        'x-rapidapi-host': "large-text-to-speech.p.rapidapi.com",
        'x-rapidapi-key': "6c4c0f51f1msh6f7cc525460af57p173a38jsnfe4ee020f940"
    }

    response = requests.request("POST", url, data=json.dumps(payload), headers=headers)
    print(response.text)

    id = json.loads(response.text)['id']
    eta = json.loads(response.text)['eta']

    print(f'Waiting {eta} seconds for the job to finish...')
    time.sleep(eta)

    response = requests.request("GET", url, headers=headers, params={'id': id})
    while "url" not in json.loads(response.text):
        response = requests.get(url, headers=headers, params={'id': id})
        time.sleep(5)
    if not "error" in json.loads(response.text):
        result_url = json.loads(response.text)['url']
        response = requests.get(result_url)
        with open('audio/output.wav', 'wb') as f:
            f.write(response.content)
        print("File output.wav saved!")
    else:
        print(json.loads(response.text)['error'])



ACCESS_KEY = 'fZ2rZc6HMDHDUgSlvYm_4gj_xkLENBi8fZv7DbM0eg8'
BASE_URL = 'https://api.unsplash.com'


def search_images(query, orientation):
    endpoint = '/search/photos'

    params = {
        'query': query,
        'per_page': 30,
        'orientation': orientation,
        'client_id': ACCESS_KEY
    }

    response = requests.get(BASE_URL + endpoint, params=params)
    data = response.json()

    if 'results' in data:
        image_urls = [result['urls']['full'] for result in data['results']]
        return random.choice(image_urls)
    else:
        return None


def download_image(image_url, filename):
    response = requests.get(image_url)
    if response.status_code == 200:
        with open(filename, 'wb') as f:
            f.write(response.content)
        print(f"Image downloaded successfully as {filename}")
    else:
        print("Failed to download image")


import cv2
import os
from moviepy.editor import VideoFileClip, CompositeAudioClip, AudioFileClip


def images_to_video(image_folder, video_name, fps, delay_between_frames_ms):
    images = [img for img in os.listdir(image_folder) if img.endswith(".png")]
    random.shuffle(images)  # Shuffle the list of images

    if not images:
        print("No images found in the specified folder.")
        return

    frame = cv2.imread(os.path.join(image_folder, images[0]))
    height, width, _ = frame.shape

    video = cv2.VideoWriter(video_name, cv2.VideoWriter_fourcc(*'mp4v'), fps, (width, height))

    for image in images:
        img_path = os.path.join(image_folder, image)
        img = cv2.imread(img_path)
        video.write(img)
        for _ in range(int(fps * delay_between_frames_ms / 1000)):  # Convert milliseconds to frames
            video.write(img)

    cv2.destroyAllWindows()
    video.release()


def add_audio_to_video(video_name, audio_files, output_video_name, volume_percentages):
    video_clip = VideoFileClip(video_name)

    audio_clips = [AudioFileClip(audio) for audio in audio_files]

    for audio_clip, volume_percentage in zip(audio_clips, volume_percentages):
        audio_clip = audio_clip.volumex(volume_percentage)

    composite_audio = CompositeAudioClip(audio_clips)

    video_clip = video_clip.set_audio(composite_audio)

    video_clip.write_videofile(output_video_name, codec="libx264", audio_codec="aac")



if __name__ == "__main__":
    generate_audio_from_text(responses_list[0])

    for idx, keyword in enumerate(responses_list[1:]):
        image_url = search_images(keyword, 'landscape')  # Assuming orientation as landscape
        if image_url:
            download_image(image_url, f'images/{idx}.png')
            print(f"Downloaded image: images/{idx}.png")
        else:
            print(f"No matching images found for keyword: {keyword}")


    def images_to_video(image_folder, video_name, fps):
        images = [img for img in os.listdir(image_folder) if img.endswith(".png")]
        if not images:
            print("No images found in the specified folder.")
            return

        video_clips = []
        for image in images:
            image_path = os.path.join(image_folder, image)
            clip = ImageClip(image_path, duration=5).resize((1920, 1080))  # Adjust size as needed
            video_clips.append(clip)

        final_clip = concatenate_videoclips(video_clips, method="compose")

        bg_music = AudioFileClip("audio/bg.mp3")

        output_audio = AudioFileClip("audio/output.wav")

        bg_music = bg_music.set_start(0)
        output_audio = output_audio.set_start(0)

        final_audio = CompositeAudioClip([bg_music, output_audio])

        final_clip = final_clip.set_audio(final_audio)

        final_clip.write_videofile(video_name, fps=fps, codec="libx264", audio_codec="aac")


    if __name__ == "__main__":
        folder_path = "C:\\Users\\hp\\PycharmProjects\\video gen\\images"
        video_name = "output_video.mp4"
        fps = 25

        images_to_video(folder_path, video_name, fps)