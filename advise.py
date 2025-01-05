from langdetect import detect  # For language detection
#from googletrans import Translator  # For translation (optional)
from openai import OpenAI

client = OpenAI(
  api_key="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"
)

completion = client.chat.completions.create(
  model="gpt-4o-mini",
  store=True,
  messages=[
    {"role": "user", "content": "write a haiku about ai"}
  ]
)

print(completion.choices[0].message);

class FinancialLiteracyClassroom:
    def __init__(self):
        self.user_level = None  # Tracks user level: beginner, intermediate, advanced
        self.conversation_context = []  # Tracks the flow of conversation
        self.lesson_index = 0  # Tracks progress in the lesson

    def greet_user(self):
        """Initial greeting and user level setup."""
        print("नमस्ते! वित्तीय शिक्षा प्रणाली में आपका स्वागत है।")
        print("कृपया अपना स्तर चुनें:")
        print("1. यदि आप नए हैं।")
        print("2. यदि आपको थोड़ा ज्ञान है।")
        print("3. यदि आप उन्नत स्तर पर हैं।")
        level = input("अपना स्तर दर्ज करें (1/2/3): ").strip()
        self.set_user_level(level)

    def set_user_level(self, level):
        """Set the user's knowledge level based on their input."""
        levels = {"1": "beginner", "2": "intermediate", "3": "advanced"}
        self.user_level = levels.get(level, "beginner")
        print(f"आपके लिए स्तर सेट कर दिया गया है: {self.user_level.capitalize()}।")

    def generate_lesson(self):
        """Generate a paragraph for the current lesson dynamically using GPT."""
        try:
            system_prompt = (
                f"You are a financial literacy expert teaching in Hindi. "
                f"The user is at a {self.user_level} level. "
                f"Explain one concept at a time in a simple and clear manner. "
                f"After each explanation, pause and wait for user confirmation before proceeding."
            )

            # GPT-4 API call
            response = OpenAI.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": system_prompt},
                    *self.conversation_context,  # Include conversation history
                    {"role": "user", "content": "Please explain the next concept."},
                ],
            )
            lesson = response["choices"][0]["message"]["content"]
            # Append the lesson to conversation context
            self.conversation_context.append({"role": "assistant", "content": lesson})
            return lesson
        except Exception as e:
            print(f"Error: {e}")
            return "मुझे क्षमा करें, मैं अभी इस प्रश्न का उत्तर देने में असमर्थ हूँ।"

    def teach_lesson(self):
        """Teach dynamically generated lessons and check for understanding."""
        while True:
            # Generate the next lesson
            lesson = self.generate_lesson()
            print("\nपाठ:", lesson)

            # Ask if the user has understood
            user_feedback = input("\nक्या आपको यह समझ में आया? (हां/नहीं): ").strip().lower()
            if user_feedback in ["हां", "yes"]:
                print("बहुत बढ़िया! अगले पाठ पर चलते हैं।")
            elif user_feedback in ["नहीं", "no"]:
                print("कोई बात नहीं, इसे फिर से समझाने की कोशिश करते हैं।")
                continue  # Regenerate the lesson
            else:
                print("कृपया केवल 'हां' या 'नहीं' में उत्तर दें।")

            # Break if user wants to stop
            proceed = input("क्या आप जारी रखना चाहते हैं? (हां/नहीं): ").strip().lower()
            if proceed in ["नहीं", "no"]:
                print("धन्यवाद! सीखते रहें।")
                break

    def start_class(self):
        """Start the classroom session."""
        self.greet_user()
        print("अब हम वित्तीय शिक्षा का पाठ शुरू करेंगे।")
        self.teach_lesson()


# Run the classroom system
if __name__ == "__main__":
    classroom = FinancialLiteracyClassroom()
    classroom.start_class()
