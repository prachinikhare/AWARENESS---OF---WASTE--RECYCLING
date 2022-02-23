from flask import Flask, request, render_template, redirect, jsonify, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_jsglue import JSGlue # this is use for url_for() working inside javascript which is help us to navigate the url
import util
import os
from werkzeug.utils import secure_filename

application = Flask(__name__ , template_folder='templates',instance_relative_config=True, static_url_path = "/static", static_folder = "static")
application.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///feedback.db"
application.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(application)

class FEEDBACKPAGE(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(500), nullable=False)
    message = db.Column(db.String(500), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

# JSGlue is use for url_for() working inside javascript which is help us to navigate the url
jsglue = JSGlue() # create a object of JsGlue
jsglue.init_app(application) # and assign the app as a init app to the instance of JsGlue

util.load_artifacts()
#home page
@application.route('/')
@application.route('/index.html')
def home():
    return render_template("index.html")

@application.route('/about')
@application.route("/about.html")
def about():
    return render_template("about.html")

@application.route("/")
def index():
    feedbacksection = FEEDBACKPAGE.query.order_by(FEEDBACKPAGE.date_created.desc()).all()
    return render_template('about.html', feedbacksection=feedbacksection)

@application.route('/feedbacks/<int:feedbacks_id>')
def feedbacks(feedbacks_id):
    feedbacks = FEEDBACK.query.filter_by(id=feedbacks_id).one()
    return render_template('feedback.html', feedbacks=feedbacks)

@application.route('/feedback')
@application.route("/feedback.html")
def feedback():
    return render_template("feedback.html")

@application.route('/Feedback', methods=['POST'])
def Feedback():
    name = request.form['name']
    email = request.form['email']
    message  = request.form['message']
    feedbacksection = FEEDBACK(name=name, email=email, message = message, date_created=datetime.now())
    db.session.feedback(feedbacksection)
    db.session.commit()
    return redirect(url_for('about'))

#classify waste
@application.route('/')
@application.route('/classify.html')
def classify():
    return render_template("classify.html")

#classify waste
@application.route("/classifywaste", methods = ["POST"])
def classifywaste():
    image_data = request.files["file"]
    #save the image to upload
    basepath = os.path.dirname(__file__)
    image_path = os.path.join(basepath, "uploads", secure_filename(image_data.filename))
    image_data.save(image_path)

    predicted_value, details, video1, video2 = util.classify_waste(image_path)
    os.remove(image_path)
    return jsonify(predicted_value=predicted_value, details=details, video1=video1, video2=video2)

# here is route of 404 means page not found error
@application.errorhandler(404)
def page_not_found(e):
    # here i created my own 404 page which will be redirect when 404 error occured in this web app
    return render_template("404.html"), 404

if __name__ == '__main__':
    application.debug = True
    application.run()
