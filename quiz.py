class FinancialLiteracyQuiz:
    def __init__(self):
        # Define the questions and answers
        self.questions = [
            {
                "question": "What will be the simple interest on ₹2000 for 3 years at an interest rate of 4%?",
                "options": ["a) ₹180", "b) ₹240", "c) ₹280", "d) ₹300"],
                "answer": "b"
            },
            {
                "question": "What is the compound interest on ₹5000 for 2 years at an interest rate of 6% per annum, compounded annually?",
                "options": ["a) ₹612", "b) ₹630", "c) ₹636", "d) ₹650"],
                "answer": "c"
            },
            {
                "question": "Which of the following is the correct formula for calculating Simple Interest (SI)?",
                "options": ["a) SI = (P * R * T) / 100", "b) SI = P * R * T", "c) SI = P + R + T", "d) SI = (P + R + T) / 100"],
                "answer": "a"
            },
            {
                "question": "Which of the following is true about Compound Interest (CI) compared to Simple Interest (SI)?",
                "options": ["a) Compound Interest is always less than Simple Interest.", "b) Simple Interest is calculated only on the initial principal amount.",
                             "c) Compound Interest is calculated only on the principal amount.", "d) Compound Interest does not grow over time."],
                "answer": "b"
            },
            {
                "question": "What is the correct formula to calculate Compound Interest (CI)?",
                "options": ["a) CI = P * (1 + R / 100)^T - P", "b) CI = P * T * R", "c) CI = P + R + T", "d) CI = (P * R * T) / 100"],
                "answer": "a"
            }
        ]

    def start_quiz(self):
        score = 0
        print("Welcome to the Financial Literacy Quiz!")
        print("Answer the following questions:\n")

        # Iterate through each question
        for i, question in enumerate(self.questions):
            print(f"Question {i + 1}: {question['question']}")
            for option in question['options']:
                print(option)

            # Get user's answer
            user_answer = input("\nYour answer (a/b/c/d): ").strip().lower()

            # Check if the answer is correct
            if user_answer == question['answer']:
                print("Correct!\n")
                score += 1
            else:
                print(f"Wrong! The correct answer was: {question['answer']}\n")

        # Show final score
        print(f"Quiz completed! Your score is: {score}/{len(self.questions)}")
        if score == len(self.questions):
            print("Excellent! You have great financial literacy knowledge.")
        elif score >= len(self.questions) // 2:
            print("Good job! But there's room for improvement.")
        else:
            print("You might want to brush up on your financial knowledge.")

# Run the quiz
if __name__ == "__main__":
    quiz = FinancialLiteracyQuiz()
    quiz.start_quiz()
