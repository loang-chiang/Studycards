# STUDYCARDS

## Overview:
STUDYCARDS is, as the name suggests, a web application that allows the user to create study flashcards and use them to revise any subject of their choice. Other features of this program include the option of creating user accounts with usernames and passwords (which are saved using a hash method) and creating different packages to save each flashcard in so that they better organized.

## Technologies Used
I chose to implement this idea with HTML and CSS for the frontend, as well as Bootstrap to elevate my CSS styling and a Google Fonts font that wasn't already available. For my backend, I used the programming languages of Python and SQL (specifically Flask-SQLAlchemy). Finally, the Flask microframework helps tie my work together into a functional web app.

## File-by-file Description:
Now I will explain what each of the files in my project folder does:

### Not Templates
* `styles.css`: As the only file inside the static directory, this is where I did all my CSS styling to make the website more user-friendly and pleasing to the eye.

* `app.py`: This is where all my Python code is collected. Here is where all my functions are defined, handling both POST and GET requests and making the program actually work. This is also the place where I handle my SQL database, which has the following models:
    * `User`, which includes the fields **id** (integer, primary key), **username** (string), and **hash** (string)
    * `Package`, which includes **id** (integer) **user_id** (ForeignKey for User) and **name** (string)
    * `Flashcard`, which includes **id** (integer), **user_id** (ForeignKey for User), package_name (TEXT NOT NULL), **question** (string) and **answer** (string)

* `.gitignore`: Here I store the names of the cache files created by my program when running it.

### Templates
* `layout.html`: This is the file where I write the HTML that will be used as a template for all the other HTML files, as well as where I import Bootstrap and the Google Fonts font that my website uses for all the text.

* `login.html`: This the page that users will be directed to if the aren't logged in. It lets the user input their username and password, and also features a button that leads to a registration page in case that this is their first time using the program.

* `register.html`: In case that the user wants to create a new account, this page lets them input their new username and password (which is asked twice for confirmation). After submitting the form they users are automatically redirected to the homepage.

* `index.html`: This is the website's homepage. It has a welcome message, shortly explains the web app's function, and lets the user choose between three options: study cards, add cards, or edit cards.

* `choose_package.html`: Whether the user chooses to study, add, or edit, they will be taken to this page, which displays all of their created packages and prompts them to choose which of them they want to study from / add to / edit from. If the user chose the Add Cards option, at the bottom of the page they will find an option that lets them create a new package, ready to be used.

* `study_cards.html`: The main function of the web app, it allows users to study from the flashcards they've created by displaying the questions stored one by one and having a button underneath the question that displays the answer, as well as a button that lets the user move on to the next question.

* `no_more_cards.html`: Once the user has finished revising all the flashcards associated with the chosen package, they will get directed to this simple page that says that they are not flashcards left in the package and includes a button leading back to the homepage.

* `add_cards`: After the user picks which package they want to add a flashcard to, they are directed to this page which lets them input a question and an answer for their flashcard, with a submit button underneath to save it. Once clicked, the page will reload with the input fields cleared so that the user can rapidly add more flashcards. There's also a button to go back to the homepage for once they are done adding cards.

* `edit_cards`: After the user picks which package they want to edit a flashcard from, they are taken to this page that displays (as as table) all the flashcards currently in that package and gives them the option to either edit or delete them. Choosing to edit a card will take them to the edit_card page, while choosing to delete one will just update the database and reload edit_cards (obviously not including the deleted card).

* `edit_card`: If the user picks a flashcard to edit, this page (similarly to add_cards) will display two text fields for the new question and answer of the flashcard. This time, both textfields are automatically initialized to the current values of the chosen card, making it easier for the user to edit small mistakes.

* `no_cards`: This page will be seen if the user tries to study from a package that has to flashcards inside. Although most other similar situations didn't require an entire different file just to say that no cards can be displayed, I chose to make this a separate file because study_cards.html wouldn't load if there weren't any flashcards in the package, so I couldn't just add a message within study_cards.