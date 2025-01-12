import sounddevice as sd
import soundfile as sf
import numpy as np
import wave
import os
from pydub import AudioSegment
from pydub.playback import play
import time

class IVRSystem:
    def __init__(self, audio_folder="IVR Audio 2"):
        self.audio_folder = audio_folder
        self.sample_rate = 44100
        self.channels = 1
        self.silence_threshold = 0.01
        self.silence_duration = 2  # seconds

    def play_audio(self, audio_file):
        try:
            audio = AudioSegment.from_file(os.path.join(self.audio_folder, audio_file))
            play(audio)
        except Exception as e:
            print(f"Error playing audio: {str(e)}")
            return False
        return True

    def record_response(self, output_filename, max_duration=30):
        frames = []  # Move frames list outside callback
        is_recording = True
        silent_count = 0
        
        def audio_callback(indata, frame_count, time_info, status):
            nonlocal silent_count, is_recording
            if status:
                print(f"Status: {status}")
            
            if is_recording:
                frames.append(indata.copy())
                volume = np.abs(indata).mean()
                print(f"\rVolume: {volume:.3f} | Time: {len(frames)/self.sample_rate:.1f}s", end="")
                
                # Silence detection
                if volume < 0.01:
                    silent_count += 1
                else:
                    silent_count = 0
                    
                if silent_count > int(self.sample_rate * 2 / 1024):  # 2 seconds silence
                    is_recording = False
                    raise sd.CallbackStop()

        try:
            with sd.InputStream(
                channels=1,
                samplerate=self.sample_rate,
                callback=audio_callback,
                blocksize=1024
            ) as stream:
                print("\nSpeak now (recording will stop after 2 seconds of silence)")
                timeout = time.time() + max_duration
                while is_recording and time.time() < timeout:
                    sd.sleep(100)

            if len(frames) > 0:
                audio_data = np.concatenate(frames, axis=0)
                sf.write(output_filename, audio_data, self.sample_rate)
                print(f"\nRecording saved to {output_filename}")
                return True
                
        except Exception as e:
            print(f"\nError recording audio: {str(e)}")
            return False

        return False

    def process_ivr_sequence(self, audio_sequence):
        for i, audio_file in enumerate(audio_sequence):
            print(f"\nPlaying prompt {i+1}: {audio_file}")
            
            if not self.play_audio(audio_file):
                print(f"Failed to play {audio_file}, skipping to next prompt")
                continue
            
            response_file = f"response_{i+1}.wav"
            print(f"Recording response to {audio_file}")
            
            if not self.record_response(response_file):
                print(f"Failed to record response for {audio_file}")
                continue
                
            print(f"Response saved as {response_file}")

def main():
    # Example usage
    ivr = IVRSystem()
    ivr.play_audio("Greet message.wav")
    audio_sequence = [
        "1.QNA start + Name.wav",
        "2.Age.mp3",
        "3.salary amount.wav",
        "4.any savings or investment.wav",
        "5. Budgeting + loan or insurance.wav",
    ]
    
    try:
        ivr.process_ivr_sequence(audio_sequence)
        ivr.play_audio("Thank you your response is submitted.wav")
    except Exception as e:
        print(f"Error in IVR sequence: {str(e)}")


if __name__ == "__main__":
    main()