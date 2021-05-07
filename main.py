import logging
from flask import Flask, render_template

app = Flask(__name__, template_folder="app/templates", static_folder='app/templates')

app.config['DEBUG'] = True


@app.route("/")
def home():
    return render_template("index.html")

@app.route("/trafikaltgrunnkurs")
def trafikaltgrunnkurs():
	return render_template("trafikaltgrunnkurs/index.html")

@app.route("/about")
def about():
	return render_template("about/index.html")

@app.route("/contact")
def contact():
	return render_template("contact/index.html")

    
if __name__ == "__main__":
    app.run(debug=True)


if __name__ != '__main__':
    gunicorn_logger = logging.getLogger('gunicorn.error')
    app.logger.handlers = gunicorn_logger.handlers
    app.logger.setLevel(gunicorn_logger.level)