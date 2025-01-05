import requests
import io
import os
import time
from gtts import gTTS
import sounddevice as sd
import soundfile as sf
import numpy as np
from datetime import datetime
import json


# Function to play text-to-speech using gTTS and block until completion
def speak(text, language='hi'):
    print(f"Speaking: {text}")  # Log the text being spoken
    try:
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        temp_file_name = f"temp_audio_{timestamp}.mp3"

        tts = gTTS(text=text, lang=language, slow=False)
        tts.save(temp_file_name)

        # Use the default Windows media player to play the audio
        os.system(f"start {temp_file_name}")

        time.sleep(1)  # Adjust as needed
        print("Speech started. You can terminate playback manually.")

        input("Press Enter to stop the playback manually...")

        # Clean up by removing the temporary audio file
        os.remove(temp_file_name)

        print("Speech finished and file removed.")
    except Exception as e:
        print(f"Error in speech: {e}")


# Class to interact with Sarvam API and conduct the interview
class DairyFarmIVR:
    def __init__(self, sarvam_api_key):
        self.api_key = sarvam_api_key
        self.base_url = "https://api.sarvam.ai"
        self.recordings_dir = "patient_recordings"
        if not os.path.exists(self.recordings_dir):
            os.makedirs(self.recordings_dir)

    def verify_audio_file(self, file_path):
        try:
            if not os.path.exists(file_path):
                print(f"Audio file not found: {file_path}")
                return False

            file_size = os.path.getsize(file_path)
            if file_size == 0:
                print(f"Audio file is empty: {file_path}")
                return False

            with sf.SoundFile(file_path) as f:
                if f.frames == 0:
                    print(f"Audio file has no frames: {file_path}")
                    return False

            return True
        except Exception as e:
            print(f"Error verifying audio file: {str(e)}")
            return False

    def record_response(self, question_number, duration=5):
        print(f"\nRecording will start in 3 seconds... You will have {duration} seconds to respond.")

        for i in range(3, 0, -1):
            print(f"{i}...")
            time.sleep(1)

        print("Recording started... Speak now.")

        sample_rate = 16000
        recording = sd.rec(
            int(duration * sample_rate),
            samplerate=sample_rate,
            channels=1,
            dtype='float32'
        )
        sd.wait()
        print("Recording completed.")

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = os.path.join(
            self.recordings_dir,
            f"response_{question_number}_{timestamp}.wav"
        )

        recording = recording / np.max(np.abs(recording))
        sf.write(filename, recording, sample_rate)

        print(f"Response saved as: {filename}")
        return filename

    def transcribe_audio(self, audio_file, source_language='hi-IN'):
        if not self.verify_audio_file(audio_file):
            print("Audio file verification failed")
            return ''

        try:
            print(f"Transcribing audio file: {audio_file}")

            url = "https://api.sarvam.ai/speech-to-text-translate"

            # Format headers with API key
            headers = {
                'api-subscription-key': self.api_key,
                # 'Content-Type': 'multipart/form-data'
            }

            # Prepare request payload
            payload = {
                'model': 'saaras:v1',
                'prompt': '',
                # 'language': language_code
            }

            # Open and prepare file
            with open(audio_file, 'rb') as f:
                files = [
                    ('file', (os.path.basename(audio_file), f, 'audio/wav'))
                ]

                # Send request with detailed error handling
                print("Sending request to Sarvam AI API...")
                response = requests.request(
                    "POST",
                    url,
                    headers=headers,
                    data=payload,
                    files=files
                )

                # Debug logging
                print(f"Response Text: {response.text}")
                print(f"Request URL: {url}")
                print(f"Response Status: {response.status_code}")
                print(f"Response Headers: {response.headers}")

                if response.status_code == 200:
                    result = response.json()
                    if "transcript" in result:
                        return result['transcript']
                    print(f"Unexpected response format: {result}")
                    return ''

                else:
                    print(f"API Error: {response.status_code}")
                    print(f"Error Details: {response.text}")
                    return ''

        except Exception as e:
            print(f"Exception during transcription: {str(e)}")
            # traceback.print_exc()
            return ''


    def introduction(self):
        speak(
            "नमस्कार! डेयरी फार्म शुरू करने के लिए वित्तीय सलाह सेवा में आपका स्वागत है। हम आपको व्यक्तिगत सलाह देने के लिए यहां हैं। कृपया कुछ आसान सवालों का जवाब दें, ताकि हम आपकी जरूरतों को समझ सकें। यह कुछ मिनटों में पूरा हो जाएगा।")
        print(
            "नमस्कार! डेयरी फार्म शुरू करने के लिए वित्तीय सलाह सेवा में आपका स्वागत है। हम आपको व्यक्तिगत सलाह देने के लिए यहां हैं। कृपया कुछ आसान सवालों का जवाब दें, ताकि हम आपकी जरूरतों को समझ सकें। यह कुछ मिनटों में पूरा हो जाएगा।")

    def gather_demographic_info(self):
        speak("हम शुरुआत करते हैं। कृपया अपना नाम बताएं।")
        print("हम शुरुआत करते हैं। कृपया अपना नाम बताएं।")
        name = self.record_response(1)
        name_transcribed = self.transcribe_audio(name)

        speak(f"आपका नाम है: {name_transcribed}")
        print(f"आपका नाम है: {name_transcribed}")

        speak("धन्यवाद। आपकी उम्र कितनी है?")
        print("धन्यवाद। आपकी उम्र कितनी है?")
        age = self.record_response(2)
        age_transcribed = self.transcribe_audio(age)

        speak(f"आपकी उम्र है: {age_transcribed}")
        print(f"आपकी उम्र है: {age_transcribed}")

        speak("आपकी वर्तमान नौकरी क्या है?")
        print("आपकी वर्तमान नौकरी क्या है?")
        occupation = self.record_response(3)
        occupation_transcribed = self.transcribe_audio(occupation)

        speak(f"आपकी नौकरी है: {occupation_transcribed}")
        print(f"आपकी नौकरी है: {occupation_transcribed}")

        speak("क्या आपको खेती या व्यवसाय का कोई अनुभव है? कृपया हाँ या नहीं में उत्तर दें।")
        print("क्या आपको खेती या व्यवसाय का कोई अनुभव है? कृपया हाँ या नहीं में उत्तर दें।")
        farming_experience = self.record_response(4)
        farming_experience_transcribed = self.transcribe_audio(farming_experience)

        speak(f"आपके पास खेती का अनुभव है: {farming_experience_transcribed}")
        print(f"आपके पास खेती का अनुभव है: {farming_experience_transcribed}")

        speak("आपकी आय का स्रोत क्या है? कृपया इनमें से एक विकल्प चुनें: वेतन, व्यवसाय, अन्य।")
        print("आपकी आय का स्रोत क्या है? कृपया इनमें से एक विकल्प चुनें: वेतन, व्यवसाय, अन्य।")
        income_source = self.record_response(5)
        income_source_transcribed = self.transcribe_audio(income_source)

        speak(f"आपकी आय का स्रोत है: {income_source_transcribed}")
        print(f"आपकी आय का स्रोत है: {income_source_transcribed}")

        return {
            'name': name_transcribed,
            'age': age_transcribed,
            'occupation': occupation_transcribed,
            'farming_experience': farming_experience_transcribed,
            'income_source': income_source_transcribed
        }

    def financial_assessment(self):
        speak("क्या आपके पास इस व्यवसाय को शुरू करने के लिए कुछ बचत है? कृपया हाँ या नहीं में उत्तर दें।")
        print("क्या आपके पास इस व्यवसाय को शुरू करने के लिए कुछ बचत है? कृपया हाँ या नहीं में उत्तर दें।")
        savings = self.record_response(6)
        savings_transcribed = self.transcribe_audio(savings)

        speak(f"आपके पास बचत है: {savings_transcribed}")
        print(f"आपके पास बचत है: {savings_transcribed}")

        speak("क्या आप लोन या सरकारी सहायता योजनाओं के बारे में जानना चाहेंगे?")
        print("क्या आप लोन या सरकारी सहायता योजनाओं के बारे में जानना चाहेंगे?")
        loan_interest = self.record_response(7)
        loan_interest_transcribed = self.transcribe_audio(loan_interest)

        speak(f"आपको लोन या सहायता योजनाओं में रुचि है: {loan_interest_transcribed}")
        print(f"आपको लोन या सहायता योजनाओं में रुचि है: {loan_interest_transcribed}")

        return {
            'savings': savings_transcribed,
            'loan_interest': loan_interest_transcribed
        }

    def conduct_interview(self):
        self.introduction()
        demographic_info = self.gather_demographic_info()
        financial_info = self.financial_assessment()

        # Store the collected data in a JSON file
        interview_data = {**demographic_info, **financial_info}
        with open('interview_data.json', 'w', encoding='utf-8') as json_file:
            json.dump(interview_data, json_file, ensure_ascii=False, indent=4)

        speak("साक्षात्कार समाप्त! आपकी जानकारी संकलित की गई है:")
        print("साक्षात्कार समाप्त! आपकी जानकारी संकलित की गई है:")
        print(interview_data)

        return interview_data


# Example usage
SARVAM_API_KEY = '7313fd42479e4f51998c92edb08be4e2'
ivr_system = DairyFarmIVR(SARVAM_API_KEY)
ivr_system.conduct_interview()
