
questions = [
    {
        "question": "1. Which language is used for Python programming?",
        "options": ["A. HTML", "B. Python", "C. CSS", "D. SQL"],
        "answer": "B"
    },
    {
        "question": "2. Which keyword is used to define a function?",
        "options": ["A. loop", "B. class", "C. def", "D. import"],
        "answer": "C"
    },
    {
        "question": "3. Which data type stores True or False?",
        "options": ["A. int", "B. str", "C. list", "D. bool"],
        "answer": "D"
    },
    {
        "question": "4. Which loop is used to iterate over a list?",
        "options": ["A. for", "B. if", "C. def", "D. try"],
        "answer": "A"
    },
    {
        "question": "5. Which function displays output in Python?",
        "options": ["A. input()", "B. print()", "C. open()", "D. read()"],
        "answer": "B"
    }
]


def calculate_score(score, answer, correct_answer):
    if answer == correct_answer:
        return score + 1
    return score


def run_quiz():
    while True:
        student_name = input("Enter student name: ").strip()

        if not student_name:
            print("Error: Student name cannot be empty!")
            continue

        break

    score = 0

    print("\n===== QUIZ STARTED =====")

    for item in questions:
        print("\n" + item["question"])

        for option in item["options"]:
            print(option)

        while True:
            answer = input("Enter answer (A/B/C/D): ").strip().upper()

            if answer not in ["A", "B", "C", "D"]:
                print("Invalid answer! Please enter A, B, C or D.")
                continue

            break

        score = calculate_score(
            score, answer, item["answer"]
        )

    print("\n===== QUIZ RESULT =====")
    print("Student:", student_name)
    print("Score:", score, "/", len(questions))

    return student_name, score
