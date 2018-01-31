# This is a script we ran one time to improve how our questions and answers are displayed.
# It converts from encoding (like "&quot;") to the actual characters (like quotation marks).

from cs50 import SQL

db = SQL("sqlite:///trivia.db")

rows = db.execute("SELECT * FROM questions")

# iterate over each question/answers row
for row in rows:
    # iterate over each cell of the row
    for col in ["question", "correct_answer", "wrong_answer1", "wrong_answer2", "wrong_answer3"]:
        # replace encoding with corresponding characters
        new_text = row[col].replace("&quot;", "\"")
        new_text = new_text.replace("&#039;", "\'")

        # update db
        db.execute("UPDATE questions SET :col = :new_text WHERE id = :id", col=col, new_text=new_text, id=row["id"])
