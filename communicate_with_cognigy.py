import datetime 
import requests
import json
import playsound
from gtts import gTTS
import speech_recognition as sr
import os
from dotenv import load_dotenv
from pydub import AudioSegment
from tqdm import tqdm
import pygame

session_id = datetime.datetime.now().isoformat()
user_id='user'
FOLDER_PATH = os.path.abspath('.')

def send_message_to_cognigy(message_text, session_id, user_id):
    
    endpoint = os.getenv('ENDPOINT')

    response = requests.post(endpoint, 
        json={
            'sessionId': session_id,
            'userId': user_id,
            'text': message_text,
            'data': {}
        }
    )

    response_content = json.loads(response.content)
    response_text_array = []

    for output in response_content['outputStack']:
        
        if not output['text'] == None: 
            response_text_array.append(output['text'])
            continue

        if output['data']['type'] == 'quickReplies':
            response_text_array.append(output['data']['text'][0])
            continue
    
    print (f'Cognigy response: {response_text_array}')
    return response_text_array

#Taken from https://www.thepythoncode.com/article/concatenate-audio-files-in-python
def concatenate_audio_pydub(audio_clip_paths, output_path, verbose=1):
    """
    Concatenates two or more audio files into one audio file using PyDub library
    and save it to `output_path`. A lot of extensions are supported, more on PyDub's doc.
    """
    def get_file_extension(filename):
        """A helper function to get a file's extension"""
        return os.path.splitext(filename)[1].lstrip(".")

    clips = []
    # wrap the audio clip paths with tqdm if verbose
    audio_clip_paths = tqdm(audio_clip_paths, "Reading audio file") if verbose else audio_clip_paths
    for clip_path in audio_clip_paths:
        # get extension of the audio file
        extension = get_file_extension(clip_path)
        print('####################################')
        
        print (clip_path)
        print(extension)
        # load the audio clip and append it to our list
        clip = AudioSegment.from_file(clip_path, extension)
        clips.append(clip)

    final_clip = clips[0]
    range_loop = tqdm(list(range(1, len(clips))), "Concatenating audio") if verbose else range(1, len(clips))
    for i in range_loop:
        # looping on all audio files and concatenating them together
        # ofc order is important
        final_clip = final_clip + clips[i]
    # export the final clip
    final_clip_extension = get_file_extension(output_path)
    if verbose:
        print(f"Exporting resulting audio file to {output_path}")
    final_clip.export(output_path, format=final_clip_extension)


def text_to_speech(text, filename='voice.mp3'):
    print(f'Saying: {text}')
    tts = gTTS(text=text, lang='en')
    filename = FOLDER_PATH + f'/output/{filename}'
    tts.save(filename)
    playsound.playsound(filename)

    return filename

def multiple_text_to_speech(text_array):

    index = 0
    temp_files = []

    for text in text_array:
        filename = text_to_speech(text, filename=f'{index}.mp3')
        
        temp_files.append(filename)
        index += 1
    

# Read for more background on different choices of using STT in Py
# https://www.thepythoncode.com/article/using-speech-recognition-to-convert-speech-to-text-python
def speech_to_text(retry_on_no_result=True, retry_count=0):
    print('Listening...')
    r = sr.Recognizer()
    
    with sr.Microphone() as source:
        audio = r.listen(source)
        said = ''
        try:
            said = r.recognize_google(audio)
            print(f'Heard: {said}') 
            
        except sr.UnknownValueError as e:
            print('I didn\'t understand what you\'re saying. Try speaking closer to the microphone, talk more clearly, or tweak the language settings.\nError message:' + str(e))  
            if retry_on_no_result:
                speech_to_text(retry_count=retry_count+1) 

        except sr.WaitTimeoutError as e: 
            print('Timeout has been reached. \nError message:' + str(e)) 

    return said




if __name__ == '__main__':
    load_dotenv()

    print ('Conversation initiated. Say "stop" or press ctrl + C to end conversation.')
    text_to_speech ('Hi.')

    while True: 
        user_input = speech_to_text()

        if 'stop' in user_input:
            print ('Goodbye!')
            text_to_speech ('Goodbye!')
            break

        response_text_array = send_message_to_cognigy(user_input, session_id, user_id)

        print (response_text_array)

        multiple_text_to_speech(response_text_array)

        


        




# curl -X POST https://endpoint-trial.cognigy.ai/70788815608734c377059faba978ea86118bdbf6def151e0664772c4cb529067
#    -H 'Content-Type: application/json'
#    -d '{
#   'userId':'userId',
#   'sessionId': 'someUniqueId',
#   'text':'yes',
#   'data': {
#   }
# }'  
   
   