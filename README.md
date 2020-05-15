FOOTBALL LEAGUE ORGANIZER
BY MAREK JANDA
OOSTENDE, BELGIUM 2019

INTRODUCTION

   I live in Europe where football, soccer, is the most popular sport and is played at all levels and organization. There is a lot of
amateur football leagues, apart from official national FA competitions, organized by schools, companies, cities or just by enthusiasts.
To track the results and make a table people usualy use MS Excel or Google sheets. So I thought it would be a useful tool to have a
platform where by input of result a league table is generated automatically and results are stored and easily accessible.

   My final project, Football league organizer, serves as tool to help people organize amateur football leagues. Via this tool
people, league admins, can register their league and add the teams to this league. When the league is in database, sqllite database,
they submit results of the matches which will be immediately transfered to points tally, goal difference and all the other football
league stats. The result will be also stored in database in fixtures table. League admin can then see the actual league table and
all the matches ordered by matchweek and date, and he can edit all data. All tables and results are available to non-registeredpeople
so the league participants can see the actual table and results however they are not allowed to change any data in the table.

   For the code I used Python - Flask and a bit of JQuery. I reused functions "login_required", "errorhandaler", and "apology" (only for
internal server error) from pset8/finance as I found them very helpful in this project. All data are stored in SQLLITE database
For HTML styling I used Bootstrap components from https://getbootstrap.com/docs/4.3/components

ARCHITECTURE

   When user visits the website first he will be redirected to login page where he is asked for username and password. After clicking "Log in"
button following checkes are performed: check if all input is provided, check wether username exists, and check if password is correct.
If any of these checks fails, application return back to login page with respective message to the failed check. If he is not registered
he can go to register page where he needs to submit user name, password, and confirm password. There are couple of checks before the user
is registered. There are checks if he provided all the input, if user name is taken, and if passwords match. If any of these checks fails
user is redirected back to register page with respective message to the failed check. Except of login page, and register page there is
a "View league" tab. This accessible without log in and will show the user a table with all registered leagues and two options for each league:
"View table" and"View fixtures". "View table" will redirect user to "table.html" where he can see the table of the league he wants.
"View fixtures" will redirect user to "fixtures.html" where he will see list of all matches played in selected league ordered by matchweek
and date.

   After user, league admin, is logged in he is redirected to "myleagues.html" where he can see list of all leagues registered by him with
option to view the table or view the fixtures. On navbar the user has three menu items "Register league", "Manage league" and "My leagues".
   At "Register league" the user can register a new league. He is only asked for a league name input. After he submits the league name the app
will check wether he provided all input and wether such league already exists. If any of the checks fails the user is redirected back to
"Register league" with respective message to the failed check. After league name is submited a new league is registerd in "leagues" table
with following info: league id, leage name, league admin (logged in user), and number of teams. Then new table with name of the input
league name will be created where all the league stats will be stored.
   After league is registered the user is redirect to "League managment" page where he will see a list of all leagues registered by
the logged in user with an option "Manage league" next to it.
   At "Manage league" the user will see a league name with a drop down menu with actions he can take and under this a league table is displayed.
There are following items in the dropdown menu: Add result, Change data, Add team, Remove team, Change the name of the league, Delete league,
and Delete result.
   At "Add result" user can submit a result of a match. He needs to select date, matchweek, home team, away team, and fill in the score. After
submit several checks are performed to check if input is correct. When checks are passed result is transformed to league table stats and
and league table is updated and result is stored in the database.
   At "Change data" user can edit all the data in the league table and change them to any value. After submit checks of correct input are
performed.
   At "Add team" the user can add team to the league. After the team name is submitted and all checks are passed the team is added to league
table with all stats initiated to 0.
   At "Remove" team the user can select a team and after submit the team is deleted from the league.
   At "Change the name of the league" the user can rename the league. After submit the league name in the "leagues" table is change and the name
of the league table is changed.
   At "Delete league" the user can delete a complete league. After submit the league is removed from the "leagues" table and the complete league
table is dropped and all fixtures of this league are deleted. This allow user to store only the leagues he wants and by deleting a league not just
his league list will be cleaner but the memory at server will be used more efficiently as not needed data will be removed.
   At "Delete result" the user can delete any result from the league. All results are displayed in a table with a button to delete next to it.
After delete button is pressed the result is deleted from fixtures table in the database and the league table is updated accordingly.

   At right site of the navbar the user has an option to change his password. User is asked for old password and to provide new password and new
password for again as confirmation. After submiting several checks are performer to ensure input is correct and old password is checked against
the hash stored in the database. If all checks are passed new password is hashed and stored in the database in "administrators" table.
    Second and last item on the right side of the navbar is "Log out". By clicking on this item the user is logged out and redirected to log in page.

SUMARY

   This tool can help people to organize the amateur leagues in an easier, quicker, nicer, and more efficient way. By this tool the users can keeo track
of the results and see the table immediately after submitting result. The league participants can see the table and results without the need to register.
Because peaple can easily track the results and tables via this tool I hope Football league organizer will encourage people to play and compete more and
promote the sport.
