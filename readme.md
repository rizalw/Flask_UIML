# Flask UIML
Flask UIML (User Interface Machine Learning) is a website that can create, train, and deploy your own ML model using just user interface. This website is also serve as my personal portfolio website. If you guys are the recruiters or someone who just curious about my skill, you could just read this readme or explore the repository. This is my Linkedin [profile](https://www.linkedin.com/in/rizal-widyananda/).
### If it's for my personal website portfolio, why didn't I deploy it to a hosting provider?
Based on some of the hosting providers that I tried, I can't do it for free because of the file size limit (nearly 500 mb) and/or file count limit (above 1000 files). Unless I found some hosting platform that can do it for free with that amount of file size & file count or maybe I just want to burn some money for a while, I will not deploy it.

## Released Features
1. Create your own model just by picking available algorithm and dataset in the website
2. Customize your own parameters, or you could just use the default value that already given in the website
3. Choose your own train:test ratio
4. Train your own model
5. Download the model to your own device for your deployment purposes
6. Doing prediction using your inputted data
## Limitation
1. This web app still only using Scikit-learn so no deep learning yet
2. User still can't upload their own dataset yet, that features can only be done on the admin side
3. User still can't use their own CSV file for doing prediction
## Future Possibilities
1. Implementing deep learning algorithm (Tensorflow or PyTorch)
2. User can upload their own dataset
3. User can upload their own CSV file for doing prediction
4. Visualize all available datasets
## What's the tools that I used?
I'm gonna detailing all of the programming languange, tools, and library that I used to make this website.
### Language
1. [Python](https://www.python.org/downloads/release/python-3131/)
2. HTML
3. CSS
### Backend
1. [Flask](https://flask.palletsprojects.com/en/stable/) (For main back-end framework)
2. [Flask-login](https://flask-login.readthedocs.io/en/latest/) (For user authentication)
3. [Flask-wtf](https://flask-wtf.readthedocs.io/en/1.2.x/) (Use with Flask-login for user registration and login)
4. [Flask-bcrypt](https://flask-bcrypt.readthedocs.io/en/1.0.1/) (For encrypting and decrypting password)
5. [Flask-sqlalchemy](https://flask-sqlalchemy.readthedocs.io/en/stable/) (For database)
6. [Flask-migrate](https://flask-migrate.readthedocs.io/en/latest/) (For migrating models)
### Frontend
1. [Bootstrap](https://getbootstrap.com/)
2. Jinja2 (For templating purpose, supported by Flask)
### Scripting
1. [Pandas](https://pandas.pydata.org/)
2. [Scikit-learn](https://scikit-learn.org/stable/)
3. Datetime
4. os
5. Pickle
