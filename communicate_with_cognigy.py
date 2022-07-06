import datetime 
import requests
import json
import playsound
from gtts import gTTS
import speech_recognition as sr
import os

def send_message_to_cognigy(message_text, session_id):
    response = requests.post('https://endpoint-trial.cognigy.ai/70788815608734c377059faba978ea86118bdbf6def151e0664772c4cb529067', 
        json={
            'userId':'userId',
            'sessionId': session_id,
            'text': message_text,
            'data': {}
        }
    )
    return response

def speak(text):
    tts = gTTS(text=text, lang='en')
    filename = os.path.abspath('voice.mp3')
    tts.save(filename)
    playsound.playsound(filename)

def get_audio():
    r = sr.Recognizer()
    
    with sr.Microphone() as source:
        audio = r.listen(source)
        said = ''
        try:
            said = r.recognize_google(audio)
            print(said) 
            
        except Exception as e:
            print('Exception: ' + str(e))   

    return said

if __name__ == '__main__':
    session_id = datetime.datetime.now().isoformat()
    # print ('Communicate with Cognigy by writing your message.')
    speak ('Hi.')

    

    while True: 
        user_input = get_audio()

        if 'end' in user_input:
            print ('Goodbye!')
            break

        response = send_message_to_cognigy(user_input, session_id)

        response_content = json.loads(response.content)

        speak(response_content['text'])


        




# curl -X POST https://endpoint-trial.cognigy.ai/70788815608734c377059faba978ea86118bdbf6def151e0664772c4cb529067
#    -H 'Content-Type: application/json'
#    -d '{
#   'userId':'userId',
#   'sessionId': 'someUniqueId',
#   'text':'yes',
#   'data': {
#   }
# }'  
   
   