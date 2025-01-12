import requests
import sounddevice as sd
import soundfile as sf
import numpy as np
import json
import os
from datetime import datetime
import time
import streamlit as st



class InterviewSystem:
    def __init__(self, sarvam_api_key):
        self.api_key = sarvam_api_key
        self.base_url = "https://api.sarvam.ai"


        # Sarvam AI supported languages
        self.supported_languages = {
            '1': {'code': 'as', 'name': 'অসমীয়া'}, #assamese
            '2': {'code': 'bn', 'name': 'বাংলা'}, #Bengali
            '3': {'code': 'en', 'name': 'English'},
            '4': {'code': 'gu', 'name': 'ગુજરાતી'}, #gujarati
            '5': {'code': 'hi', 'name': 'हिंदी'}, #hindi
            '6': {'code': 'kn', 'name': 'ಕನ್ನಡ'},#kannada
            '7': {'code': 'ml', 'name': 'മലയാളം'},#malayalam
            '8': {'code': 'mr', 'name': 'मराठी'},#marathi
            '9': {'code': 'or', 'name': 'ଓଡ଼ିଆ'},#odia
            '10': {'code': 'pa', 'name': 'ਪੰਜਾਬੀ'},#punjabi_gurmukhi
            '11': {'code': 'ta', 'name': 'தமிழ்'},#tamil
            '12': {'code': 'te', 'name': 'தெலுங்கு'},#telugu
            '13': {'code': 'ur', 'name': 'اردو'}#urdu
        }

        # Create directory for storing recordings if it doesn't exist
        self.recordings_dir = "customer_recordings"
        if not os.path.exists(self.recordings_dir):
            os.makedirs(self.recordings_dir)


    def record_response(self, question_number, duration=10):
        st.write(f"\nRecording will start in 3 seconds...")
        st.write(f"You will have {duration} seconds to respond.")

        # Progress bar for 3-second timer
        progress_bar = st.progress(0)
        for i in range(3):
            progress_bar.progress((i + 1) / 3)
            time.sleep(1)

        st.write("Recording started... Speak now.")

        # Record audio
        sample_rate = 16000
        recording = sd.rec(
            int(duration * sample_rate),
            samplerate=sample_rate,
            channels=1,
            dtype='float32'
        )
        sd.wait()
        st.write("Recording completed.")

        # Generate unique filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = os.path.join(
            self.recordings_dir,
            f"response_{question_number}_{timestamp}.wav"
        )

        # Save recording
        recording = recording / np.max(np.abs(recording))
        sf.write(filename, recording, sample_rate)

        st.write(f"Response saved")
        return filename

    def transcribe_audio(self, audio_file, language_code):
        if not os.path.exists(audio_file):
            st.write("Audio file not found!")
            return ""

        try:
            st.write(f"Transcribing audio file: {audio_file}")

            url = "https://api.sarvam.ai/speech-to-text-translate"
            headers = {'api-subscription-key': self.api_key}

            payload = {
                'model': 'saaras:v1',
                'prompt': ''
            }

            with open(audio_file, 'rb') as f:
                files = [('file', (os.path.basename(audio_file), f, 'audio/wav'))]
                response = requests.post(url, headers=headers, data=payload, files=files)

            if response.status_code == 200:
                result = response.json()
                return result.get('transcript', "")
            else:
                st.write(f"Error during transcription: {response.text}")
                return ""

        except Exception as e:
            st.write(f"Exception during transcription: {str(e)}")
            return ""

    def conduct_interview(self, language_code, questions):
        responses = []
        audio_files = []

        for i, question in enumerate(questions, 1):
            st.write(f"\nQuestion {i}: {question}")


            # Record response
            audio_file = self.record_response(i)
            audio_files.append(audio_file)

            # Transcribe response
            transcribed_text = self.transcribe_audio(audio_file, language_code)

            if transcribed_text:
                responses.append(transcribed_text)
                st.write(f"\nTranscribed response: {transcribed_text}")
            else:
                st.write("Failed to transcribe response")

        # Prepare result
        result = {
            'interview_date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'language': language_code,
            'questions': questions,
            'responses': responses,
            'audio_files': audio_files
        }
        return result



def main():
    SARVAM_API_KEY = '7313fd8a-a2f8-476f-b88f-b80c6d22bf62'
    interview_system = InterviewSystem(SARVAM_API_KEY)

    st.title("Welcome to Sampoorna Shakti Interview")
    st.markdown("Helping you with financial literacy and personalized advice.")

    # Move language selection to sidebar
    language_options = {lang['name']: lang['code'] for lang in interview_system.supported_languages.values()}
    selected_language_name = st.sidebar.selectbox("Select your preferred language:", list(language_options.keys()),placeholder="Select your preferred language")
    selected_language_code = language_options[selected_language_name]



    # Questions in different languages
    questions = {
        'en': ["What is your name?", "How old are you?", "What is your current occupation?", "What is your monthly income?",
               "Do you currently have any savings or investments?", "Are you familiar with financial terms like budgeting, loans, and insurance?"],
        'hi': ["आपका नाम क्या है?", "आपकी उम्र क्या है?", "आपका वर्तमान व्यवसाय क्या है?", "आपकी मासिक आय कितनी है?",
               "क्या आपके पास वर्तमान में कोई बचत या निवेश है?", "क्या आप बजट, ऋण और बीमा जैसे वित्तीय शब्दों से परिचित हैं?"],
        'as': ["আপোনাৰ নাম কি?",
            "আপোনাৰ বয়স কিমান?",
            "আপোনাৰ বৰ্তমান পেচা কি?",
            "আপোনাৰ মাহিলী আয় কিমান?",
            "আপোনাৰ বৰ্তমান কোনো সঞ্চয় বা বিনিয়োগ আছে নেকি?",
            "আপুনি কি বাজেটিং, ঋণ আৰু বীমাৰ দৰে বিত্তীয় শব্দৰ বিষয়ে জানেনে?"],
        'bn': [
            "আপনার নাম কী?",
            "আপনার বয়স কত?",
            "আপনার বর্তমান পেশা কী?",
            "আপনার মাসিক আয় কত?",
            "আপনার বর্তমানে কোন সঞ্চয় বা বিনিয়োগ আছে কি?",
            "আপনি কি বাজেটিং, ঋণ এবং বীমার মতো আর্থিক শব্দ জানেন?"
        ],
        'gu': [
            "તમારું નામ શું છે?",
            "તમારી ઉમર કેટલાય છે?",
            "તમારો વર્તમાન વ્યવસાય શું છે?",
            "તમારી માસિક આવક કેટલાય છે?",
            "શું તમારી પાસે હાલમાં કોઈ બચત અથવા રોકાણ છે?",
            "શું તમે બજેટિંગ, લોન અને બિમા જેવા નાણાકીય શબ્દોથી પરિચિત છો?"
        ],
        'kn': [
            "ನಿಮ್ಮ ಹೆಸರೇನು?",
            "ನಿಮ್ಮ ವಯಸ್ಸೇನು?",
            "ನಿಮ್ಮ ಪ್ರಸ್ತುತ ಉದ್ಯೋಗವೇನು?",
            "ನಿಮ್ಮ ಮಾಸಿಕ ಆದಾಯವೇನು?",
            "ನೀವು ಈಗ ಯಾವುದೇ ಉಳಿತಾಯ ಅಥವಾ ಹೂಡಿಕೆಗಳನ್ನುವೆ? ",
            "ನೀವು ಬಜೆಟಿಂಗ್, ಸಾಲ ಮತ್ತು ವಿಮಾ ಮುಂತಾದ ಆರ್ಥಿಕ ಪದಗಳನ್ನು ಪರಿಚಯಿಸುತ್ತಿದ್ದೀರಾ?"
        ],
        'ml': [
            "നിന്റെ പേര് എന്താണ്?",
            "നിന്റെ പ്രായം എത്ര?",
            "നിന്റെ നിലവിലെ ജോലി എന്താണ്?",
            "നിന്റെ മാസിക വരുമാനം എത്ര?",
            "നിന്റെ നിലവിലെ എന്തെങ്കിലും പോർചയം അല്ലെങ്കിൽ നിക്ഷേപങ്ങൾ ഉണ്ടോ?",
            "നിനക്ക് ബജറ്റിങ്ങ്, വായ്പ, ഇൻഷുറൻസ് പോലുള്ള സാമ്പത്തിക പദങ്ങൾ അറിയാമോ?"
        ],
        'mr': [
            "तुमचं नाव काय आहे?",
            "तुम्ही किती वयाचे आहात?",
            "तुमचं सध्या काय काम आहे?",
            "तुमची मासिक उत्पन्न किती आहे?",
            "तुमच्याकडे सध्या काही बचत किंवा गुंतवणूक आहे का?",
            "तुम्ही बजेटिंग, कर्ज आणि विमा या आर्थिक शब्दांशी परिचित आहात का?"
        ],
        'or': [
            "ଆପଣଙ୍କର ନାମ କଣ?",
            "ଆପଣଙ୍କର ବୟସ କେତେ?",
            "ଆପଣଙ୍କର ବର୍ତ୍ତମାନ ଅଧିକାର କଣ?",
            "ଆପଣଙ୍କର ମାସିକ ଆୟ କେତେ?",
            "ଆପଣଙ୍କର ବର୍ତ୍ତମାନ କିଛି ସଞ୍ଚୟ ବା ନିବେଶ ଅଛି କି?",
            "ଆପଣ ବଜେଟିଂ, ଋଣ ଏବଂ ବୀମା ପରି ଆର୍ଥିକ ଶବ୍ଦରେ ପରିଚିତ ଅଛନ୍ତି କି?"
        ],
        'pa': [
            "ਤੁਹਾਡਾ ਨਾਮ ਕੀ ਹੈ?",
            "ਤੁਹਾਡੀ ਉਮਰ ਕਿੰਨੀ ਹੈ?",
            "ਤੁਹਾਡਾ ਮੌਜੂਦਾ ਪੇਸ਼ਾ ਕੀ ਹੈ?",
            "ਤੁਹਾਡੀ ਮਹੀਨੇ ਦੀ ਆਮਦਨ ਕਿੰਨੀ ਹੈ?",
            "ਕੀ ਤੁਹਾਡੇ ਕੋਲ ਮੌਜੂਦਾ ਸਮੇਂ ਵਿੱਚ ਕੋਈ ਬਚਤ ਜਾਂ ਨਿਵੇਸ਼ ਹੈ?",
            "ਕੀ ਤੁਸੀਂ ਬਜਟਿੰਗ, ਕਰਜ਼ਾ ਅਤੇ ਬੀਮਾ ਜਿਹੇ ਆਰਥਿਕ ਸ਼ਬਦਾਂ ਨਾਲ ਪਰਿਚਿਤ ਹੋ?"
        ],
        'ta': [
            "உங்கள் பெயர் என்ன?",
            "உங்களின் வயது எவ்வளவு?",
            "நீங்கள் தற்போது என்ன தொழிலில் செயல்பட்டுள்ளீர்கள்?",
            "உங்களின் மாத வருமானம் என்ன?",
            "நீங்கள் தற்போது எதுவும் சேமிப்புகள் அல்லது முதலீடுகள் உள்ளதா?",
            "நீங்கள் பட்ஜெட்டிங், கடன் மற்றும் காப்பீடு போன்ற நிதி வார்த்தைகளுக்கு அறிந்திருக்கிறீர்களா?"
        ],
        'te': [
            "మీ పేరు ఏమిటి?",
            "మీ వయసు ఎంత?",
            "మీ ప్రస్తుత ఉద్యోగం ఏమిటి?",
            "మీ నెలవారీ ఆదాయం ఎంత?",
            "మీకు ప్రస్తుతం ఏవైనా ఆదా లేదా పెట్టుబడులు ఉన్నాయా?",
            "మీరు బడ్జెటింగ్, రుణాలు మరియు బీమా వంటి ఆర్థిక పదాలను తెలుసా?"
        ],
        'ur': [
            "آپ کا نام کیا ہے؟",
            "آپ کی عمر کتنی ہے؟",
            "آپ کا موجودہ پیشہ کیا ہے؟",
            "آپ کی ماہانہ آمدنی کتنی ہے؟",
            "کیا آپ کے پاس موجودہ وقت میں کوئی بچت یا سرمایہ کاری ہے؟",
            "کیا آپ بجٹ سازی، قرض اور انشورنس جیسے مالی اصطلاحات سے واقف ہیں؟"
        ]
        # Add other language questions here...
    }

    # Get selected questions
    current_questions = questions.get(selected_language_code, questions['hi'])

    if st.button("Start Interview"):
        result = interview_system.conduct_interview(selected_language_code, current_questions)

        # Save results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        result_file = f"interview_result_{timestamp}.json"

        with open(result_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)

        # Display results
        st.write("\n### Interview Results")
        st.write(f"**Language:** {selected_language_name}")
        st.write("#### Responses:")
        for i, response in enumerate(result['responses'], 1):
            st.write(f"**Question {i}:** {response}")

        st.success(f"Results saved to: {result_file}")


if __name__ == "__main__":
    main()
