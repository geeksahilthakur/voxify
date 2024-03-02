import os
from moviepy.editor import ImageClip, concatenate_videoclips, AudioFileClip, CompositeAudioClip

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
