import requests
import os
from flask import Flask, request, jsonify
from datetime import datetime

# Flask app to handle IVR webhooks
app = Flask(__name__)

# Exotel and Sarvam AI credentials
EXOTEL_SID = "sampoornashakti1"
EXOTEL_TOKEN = "6c46d89ea854e0c1a9b5b3b50a589277b51f080923c50866"
EXOTEL_VIRTUAL_NUMBER = "03340838220"
SARVAM_API_KEY = "7313fd8a-a2f8-476f-b88f-b80c6d22bf62"

# Directory to store recordings
RECORDINGS_DIR = "ivr_recordings"
os.makedirs(RECORDINGS_DIR, exist_ok=True)

# Sarvam AI API URL
SARVAM_API_URL = "https://api.sarvam.ai/speech-to-text-translate"

@app.route("/ivr-greeting", methods=["POST"])
def ivr_greeting():
    """Handles the IVR greeting and directs to the menu."""
    response_xml = f"""
    <Response>
        <PlayText>स्वागत है वित्तीय साक्षरता प्रणाली में। कृपया मेनू से एक विकल्प चुनें।</PlayText>
        <Redirect>/ivr-menu</Redirect>
    </Response>
    """
    return response_xml, 200, {'Content-Type': 'text/xml'}

@app.route("/ivr-menu", methods=["POST"])
def ivr_menu():
    """Handles the IVR menu options."""
    pressed_key = request.form.get("Digits")  # Captures the digit pressed by the user

    if pressed_key == "1":
        # Option 1: Continue to Learning
        response_xml = f"""
        <Response>
            <PlayText>आपने सीखना जारी रखने का विकल्प चुना है। हम अब शिक्षण मॉड्यूल पर जाएंगे।</PlayText>
            <Redirect>/ivr-start</Redirect>
        </Response>
        """
    elif pressed_key == "2":
        # Option 2: Support/Query
        response_xml = f"""
        <Response>
            <PlayText>आपने समर्थन या प्रश्न का विकल्प चुना है। कृपया बीप के बाद अपना संदेश छोड़ें।</PlayText>
            <Record finishOnKey="#" maxLength="60" action="/ivr-support-query" method="POST" />
        </Response>
        """
    else:
        # Invalid option
        response_xml = f"""
        <Response>
            <PlayText>अमान्य विकल्प चुना गया है। कृपया पुनः प्रयास करें।</PlayText>
            <Redirect>/ivr-greeting</Redirect>
        </Response>
        """
    return response_xml, 200, {'Content-Type': 'text/xml'}

@app.route("/ivr-support-query", methods=["POST"])
def ivr_support_query():
    """Handles support/query recordings."""
    recording_url = request.form.get("RecordingUrl")

    if not recording_url:
        return "कोई रिकॉर्डिंग प्राप्त नहीं हुई", 400

    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        recording_file = os.path.join(RECORDINGS_DIR, f"support_query_{timestamp}.wav")

        # Download the recording
        response = requests.get(recording_url, stream=True)
        if response.status_code == 200:
            with open(recording_file, 'wb') as f:
                for chunk in response.iter_content(chunk_size=1024):
                    f.write(chunk)
            print(f"Support/Query recording saved to {recording_file}")
        else:
            print("रिकॉर्डिंग डाउनलोड करने में विफल")
            return "रिकॉर्डिंग डाउनलोड करने में विफल", 500

        # Optionally transcribe the query
        transcript = transcribe_audio(recording_file)

        if transcript:
            print(f"Support/Query Transcription: {transcript}")
            return jsonify({"support_query_transcription": transcript}), 200
        else:
            return "प्रतिलिपि बनाने में विफल", 500

    except Exception as e:
        print(f"Support/Query recording processing error: {e}")
        return "आंतरिक सर्वर त्रुटि", 500

@app.route("/ivr-start", methods=["POST"])
def ivr_start():
    """Handles the IVR start by responding with an XML flow."""
    response_xml = f"""
    <Response>
        <PlayText>स्वागत है वित्तीय साक्षरता साक्षात्कार में।</PlayText>
        <PlayText>हम आपसे कुछ प्रश्न पूछेंगे। कृपया बीप के बाद उत्तर दें।</PlayText>
        <Record finishOnKey="#" maxLength="60" action="/ivr-response" method="POST" />
    </Response>
    """
    return response_xml, 200, {'Content-Type': 'text/xml'}

@app.route("/ivr-response", methods=["POST"])
def ivr_response():
    """Handles the recording and transcription of responses."""
    recording_url = request.form.get("RecordingUrl")
    question_id = request.form.get("CustomField")  # Custom question ID (optional)

    if not recording_url:
        return "कोई रिकॉर्डिंग प्राप्त नहीं हुई", 400

    # Download the recording
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        recording_file = os.path.join(RECORDINGS_DIR, f"response_{question_id}_{timestamp}.wav")

        response = requests.get(recording_url, stream=True)
        if response.status_code == 200:
            with open(recording_file, 'wb') as f:
                for chunk in response.iter_content(chunk_size=1024):
                    f.write(chunk)
            print(f"Recording saved to {recording_file}")
        else:
            print("रिकॉर्डिंग डाउनलोड करने में विफल")
            return "रिकॉर्डिंग डाउनलोड करने में विफल", 500

        # Transcribe the audio using Sarvam AI
        transcript = transcribe_audio(recording_file)

        if transcript:
            print(f"Transcription: {transcript}")
            return jsonify({"transcription": transcript}), 200
        else:
            return "प्रतिलिपि बनाने में विफल", 500

    except Exception as e:
        print(f"रिकॉर्डिंग प्रोसेसिंग में त्रुटि: {e}")
        return "आंतरिक सर्वर त्रुटि", 500

def transcribe_audio(audio_file):
    """Uses Sarvam AI to transcribe the audio file."""
    try:
        with open(audio_file, 'rb') as f:
            files = {'file': (os.path.basename(audio_file), f, 'audio/wav')}
            headers = {'api-subscription-key': SARVAM_API_KEY}
            data = {'model': 'saaras:v1'}

            response = requests.post(SARVAM_API_URL, headers=headers, files=files, data=data)

            if response.status_code == 200:
                result = response.json()
                return result.get('transcript', '')
            else:
                print(f"Sarvam AI API Error: {response.status_code} - {response.text}")
                return ''
    except Exception as e:
        print(f"प्रतिलिपि निर्माण में त्रुटि: {e}")
        return ''

if __name__ == "__main__":
    # Run the Flask app
    app.run(debug=True, port=5000)
