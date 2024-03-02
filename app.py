from PIL import Image
import time
from flask import *
import openai
import requests
import json
import random
import os
from moviepy.editor import *

app=Flask(__name__)



openai_api_key = "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"
openai.api_key=openai_api_key

access_key="ElQnB4Ns45hNC02JsLDi8tiZAuFecN0o30a364KszUI"
base_url="https://api.unsplash.com"

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/generate', methods=['POST'])
def generate():
    if request.method == 'POST':
        if 'topic' in request.form:
            topic = request.form['topic']
            paragraph_title_prompt = "act as a professional content writer write a short one minute paragraph in the form of paragraph title = " + topic
            gpt_response_title = chat_with_gpt(paragraph_title_prompt)

            unsplash_keywords_prompt = "i want use stock images from the unsplash. so provide some 5 relevant keyword to find exact same images on unsplash topic =" + topic
            gpt_response_keywords = chat_with_gpt(unsplash_keywords_prompt)

            responses_list = [gpt_response_title] + gpt_response_keywords.split("\n")

            video_url = generate_video(responses_list)

            return render_template('index.html', video_generated=True)
        else:
            return "Error: 'topic' key not found in form data."


@app.route('/download_video')
def download_video():
    video_path = 'output_video.mp4'
    return send_file(video_path, as_attachment=True)


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


def search_images(query, orientation):
    endpoint = '/search/photos'

    params = {
        'query': query,
        'per_page': 30,
        'orientation': orientation,
        'client_id': "ElQnB4Ns45hNC02JsLDi8tiZAuFecN0o30a364KszUI"
    }

    response = requests.get(base_url + endpoint, params=params)
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


def generate_audio_from_text(text):
    url = "https://large-text-to-speech.p.rapidapi.com/tts"
    payload = {"text": text}

    headers = {
        'content-type': "application/json",
        'x-rapidapi-host': "large-text-to-speech.p.rapidapi.com",
        'x-rapidapi-key': "31b1a09714mshffae638e776297cp15ef7ajsn1a146e39819f"
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


def images_to_video(image_folder, video_name, fps):
    images = [img for img in os.listdir(image_folder) if img.endswith(".png")]
    if not images:
        print("No images found in the specified folder.")
        return

    video_clips = []
    for image in images:
        image_path = os.path.join(image_folder, image)

        clip = ImageClip(image_path, duration=5).resize((1920, 1080), resample='bicubic')
        video_clips.append(clip)

    final_clip = concatenate_videoclips(video_clips, method="compose")

    bg_music = AudioFileClip("audio/bg.mp3")

    output_audio = AudioFileClip("audio/output.wav")

    bg_music = bg_music.set_start(0)
    output_audio = output_audio.set_start(0)

    final_audio = CompositeAudioClip([bg_music, output_audio])

    final_clip = final_clip.set_audio(final_audio)

    final_clip.write_videofile(video_name, fps=fps, codec="libx264", audio_codec="aac")


def generate_video(responses_list):

    generate_audio_from_text(responses_list[0])

    image_folder = "images"
    for idx, keyword in enumerate(responses_list[1:]):
        image_url = search_images(keyword, 'landscape')
        if image_url:
            download_image(image_url, f'{image_folder}/{idx}.png')
            print(f"Downloaded image: {image_folder}/{idx}.png")
        else:
            print(f"No matching images found for keyword: {keyword}")

    folder_path = "images"
    video_name = "output_video.mp4"
    fps = 25

    images_to_video(folder_path, video_name, fps)

    print("Video generated.")

    return f'/{video_name}'


if __name__ == '__main__':
    app.run(debug=True)