from cs50 import SQL

db = SQL("sqlite:///trivia.db")

rows = db.execute("SELECT * FROM questions")

for row in rows:
    for col in ["question", "correct_answer", "wrong_answer1", "wrong_answer2", "wrong_answer3"]:
        new_text = row[col].replace("&quot;", "\"")
        new_text = new_text.replace("&#039;", "\'")

        db.execute("UPDATE questions SET :col = :new_text WHERE id = :id", col=col, new_text=new_text, id=row["id"])
