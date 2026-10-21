
from quiz import run_quiz
from file_handler import save_result, show_results


def main():
    while True:
        print("\n===== QUIZ MANAGEMENT SYSTEM =====")
        print("1. Start Quiz")
        print("2. View Previous Results")
        print("3. Exit Program")

        choice = input("Enter your choice (1-3): ").strip()

        if choice == "1":
            student_name, score = run_quiz()
            save_result(student_name, score)

        elif choice == "2":
            show_results()

        elif choice == "3":
            print("Thank you for using Quiz Management System!")
            break

        else:
            print("Invalid choice! Please select 1, 2 or 3.")
            continue


if __name__ == "__main__":
    main()
