from cs50 import SQL
import json
import requests

db = SQL("sqlite:///trivia.db")

url = "https://opentdb.com/api.php?amount=50&type=multiple"
r = requests.get(url)

output = r.json()

for i in range(len(output['results'])):
    result = output['results'][i]
    question = result['question']
    correct_answer = result['correct_answer']
    wrong_answer1 = result['incorrect_answers'][0]
    wrong_answer2 = result['incorrect_answers'][1]
    wrong_answer3 = result['incorrect_answers'][2]

    db.execute("INSERT INTO questions (question, correct_answer, wrong_answer1, wrong_answer2, wrong_answer3) VALUES (:question, :correct_answer, :wrong_answer1, :wrong_answer2, :wrong_answer3)", question=question, correct_answer=correct_answer, wrong_answer1=wrong_answer1, wrong_answer2=wrong_answer2, wrong_answer3=wrong_answer3)

