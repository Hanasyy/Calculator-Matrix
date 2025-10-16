import random

QUIZ_QUESTIONS = [
    {
        "q": "Jika A berordo 3x3 dan B berordo 3x3, maka A + B berordo?",
        "options": ["3x3", "6x6", "Tidak bisa dijumlahkan", "3x1"],
        "answer": "3x3"
    },
    {
        "q": "Hasil dot product dari (1,2,3) dan (4,5,6) adalah?",
        "options": ["32", "22", "30", "28"],
        "answer": "32"
    },
    {
        "q": "Invers matriks hanya bisa dihitung jika determinannya?",
        "options": ["0", "1", "Tidak nol", "Kurang dari 1"],
        "answer": "Tidak nol"
    },
]

def get_random_quiz():
    q = random.choice(QUIZ_QUESTIONS)
    return q["q"], q["options"], q["answer"]
