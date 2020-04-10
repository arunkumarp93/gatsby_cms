**Static Site generator Using Flask and Github for gatsby**
========================================

Static site generator used to create the markdown content and store it on github.

This will help you to create the markdown file for gatsby blog. It'll help to create content and post immediatly or save it in draft, edit again and finally post it.

**Create OAUTH application in github**
============================

We need github clien-id and client-secret to access the gihtub api for both development and production.
So create oauth application in gihtub

*step 1:*
Goto --> https://github.com/settings/developers

click on OAuth Apps --> New OAuth apps

*step 2:*

Add Appname: sample app

if it's localhost

Homepage URL: http://localhost:5000

Authorization callback URL: http://localhost:5000/authorize

click --> Register Application

*step 3:*

click on app name that's created before in above case

sample app

you can see the client id and client secret. we need to add this to our .env


**Start App**
===============

*Step 1:* Clone the repo

cd static_site_generator

*Step 2:* create .env file in root folder

Add below values to .env replace the GITHUB_CLIENTID and GITHUB_CLIENTSECRET with your application id and secret.

SECRET_KEY = 'some-text-you-cannot-guess'  
GITHUB_CLIENTID = ''  
GITHUB_CLIENTSECRET = ''  
ENV='development'  

*step-3:* install requirement
pip install -r requirements.txt

*step-4:* start server
python3 server.py

**How to use**
===============

*step 1*: configure github folder
we need to configure the github repo and content folder path and draft folder path after login to the site

Repo Name --> gatsby_sample

(Trailing slash in the end of the folder is must)

Post Folder Name --> content/posts/

Draft Folder Name --> content/drafts/

you'll be redirected to home-page automatically content will be fetched from github posts folder and displayed here.

Links
https://gatsby-ssg.herokuapp.com/drafts

https://gatsby-ssg.herokuapp.com/configure

https://gatsby-ssg.herokuapp.com/create


Heroku Sample App:
https://gatsby-ssg.herokuapp.com/


**deployment on heroku**
===========================

*step 1:* install herko cli
https://devcenter.heroku.com/articles/heroku-cli

*step 2:* create app
      heroku create APP-NAME (APP-NAME is not mention then heroku creates a random name)

*step 3:* git push heroku master

*step 4:*
 Update .env variables to Config vars in heroku

 https://dashboard.heroku.com/apps/APP-NAME/settings

 On Config Vars tabs click on Reveal Config Vars

 Add all .env variables

 *step 5:* heroku ps:scale web=1

 *step 6:* heroku open


**issue:**

***githubfolder configre will be reset whenever server is restart or started newly***
