# Flask UIML
Flask UIML (User Interface Machine Learning) is website that can create, train, and deploy your own ML model using just user interface. This website is also serve as my personal portfolio website. If you guys are the recruiters or someone who just curious about my skill, you could just read this readme or explore the repository.

## Released Features
1. Create your own model just by picking available algorithm and dataset in the website
2. Customize your own parameters, or you could just use the default value that already given in the website
3. Train your own model
4. Download the model to your own device for your deployment purposes
## Limitation
1. This web app still only using Scikit-learn so no deep learning yet
2. User still can't upload their own dataset yet, that role can be done by admin
## Future Possibilities
1. Implementing deep learning into the web app (Tensorflow or Pytorch)
2. Use the model from inside the web app UI to predict new data (Your own files or new inputted data)
3. Choose your own train:test ratio, the default is still 75:25
4. User can upload their own dataset
5. Visualize available dataset
## What's the tools that I used?
I'm gonna detailing all of the programming languange, tools, and library that I used to make this website.
### Language
1. Python
2. HTML
3. CSS
### Backend
1. Flask (For main back-end framework)
2. Flask-login (For user authentication)
3. Flask-wtf (Use with Flask-login for user registration and login)
4. Flask-bcrypt (For encrypting and decrypting password)
5. Flask-sqlalchemy (For database)
6. Flask-migrate (For migrating models)
### Frontend
1. Bootstrap
2. Jinja2 (For templating purpose, supported by Flask)
### Scripting
1. Numpy
2. Scikit-learn
3. Datetime
4. os
