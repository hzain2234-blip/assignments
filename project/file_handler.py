
def save_result(student_name, score):
    try:
        with open("results.txt", "a", encoding="utf-8") as file:
            file.write(f"{student_name} | Score: {score}/5\n")

        print("Result saved successfully!")

    except OSError as error:
        print("Error saving result:", error)


def show_results():
    try:
        with open("results.txt", "r", encoding="utf-8") as file:
            results = file.readlines()

        print("\n===== PREVIOUS RESULTS =====")

        if not results:
            print("No previous results found.")
            return

        for result in results:
            print(result.strip())

    except FileNotFoundError:
        print("Results file not found. Complete a quiz first.")

    except OSError as error:
        print("Error reading results:", error)
