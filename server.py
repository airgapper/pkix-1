from flask import Flask, render_template, Markup

from database import PKIXDatabase

db = PKIXDatabase("mongodb://localhost:27017")
app = Flask(__name__, template_folder=".")

@app.route("/pkix")
def pkix():
    return render_template("pkix.html",
                            members_html=Markup(db.members_html()),
                            ipv4=db.ipv4(),
                            ipv6=db.ipv6()
                           )

app.run("localhost", port=5000, debug=True)
