from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
db = SQLAlchemy(app)

class InputWord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    word = db.Column(db.String(20), nullable=False)
    synonyms1 = db.Column(db.String(20))
    synonyms2 = db.Column(db.String(20))
    synonyms3 = db.Column(db.String(20))
    synonyms4 = db.Column(db.String(20))
    synonyms5 = db.Column(db.String(20))

    # def __init__(self, word, synonyms1, synonyms2, synonyms3, synonyms4, synonyms5):
    #     self.word = word
    #     self.synonyms1 = synonyms1
    #     self.synonyms2 = synonyms2
    #     self.synonyms3 = synonyms3
    #     self.synonyms4 = synonyms4
    #     self.synonyms5 = synonyms5
        
    def __repr__(self):
        return '<Word %r>' % self.word

@app.route('/', methods = ['POST', 'GET'])
def index():
    if request.method == 'POST':
        input_content = request.form['word']
        # output1 to 5 should be replaced by top 5 most simliarity word which from the working NLP model
        # just return all same word for testing at this time
        output1 = request.form['word']
        output2 = request.form['word']
        output3 = request.form['word']
        output4 = request.form['word']
        output5 = request.form['word']
        # new_task = InputWord(input_content,output1,output2,output3,output4,output5)
        new_task = InputWord(word=input_content, synonyms1=output1, synonyms2=output2, synonyms3=output3, synonyms4=output4, synonyms5=output5)

        db.session.add(new_task)
        db.session.commit()

        return render_template('results.html', new_task=new_task)

    else: 
        return render_template('page.html')


@app.route('/next', methods = ['POST', 'GET'])
def next():
    if request.method == 'POST':
        input_content = request.form['next_word']
        output1 = request.form['next_word']
        output2 = request.form['next_word']
        output3 = request.form['next_word']
        output4 = request.form['next_word']
        output5 = request.form['next_word']
        new_task = InputWord(word=input_content, synonyms1=output1, synonyms2=output2, synonyms3=output3, synonyms4=output4, synonyms5=output5)

        db.session.add(new_task)
        db.session.commit()

        return render_template('results.html', new_task=new_task)

    else: 
        return render_template('page.html')

if __name__ == "__main__":
    app.run(debug = True)