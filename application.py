import os

from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session, make_response
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached


@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


# Custom filter


# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///league_organizer.db")


@app.route("/")
@login_required
def index():
    # Get leagues registered by loged in admin
    admininfo = db.execute("SELECT * FROM administrators WHERE admin_ID = :admin_ID", admin_ID=session["user_id"])
    myleagues = db.execute("SELECT * FROM leagues WHERE league_admin = :admin", admin=admininfo[0]["admin_name"])
    return render_template("myleagues.html", leagues=myleagues)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # On POST log user in (if valid logic credentials)
    if request.method == "POST":
        # Ensure username was submitted
        adminexists = True
        pswinput = True
        adminput = True
        wrongpsw = False
        if not request.form.get("admin_name"):
            return render_template("login.html", adminput=False)
            # return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return render_template("login.html", pswinput=False)
            # return apology("must provide password", 403)

        # Query database for username
        admins = db.execute("SELECT * FROM administrators WHERE admin_name = :admin_name",
                            admin_name=request.form.get("admin_name"))

        # Ensure username exists and password is correct
        if not admins:
            return render_template("login.html", adminexists=False)
            # return apology("Wrong admin name", 403)

        elif not check_password_hash(admins[0]["psw_hash"], request.form.get("password")):
            return render_template("login.html", wrongpsw=True)
            # return apology("Wrong password", 403)

        else:
            # Remember which user has logged in adn redirect user to the homepage
            session["user_id"] = admins[0]["admin_ID"]
            return redirect("/")

    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register new league admin"""
    if request.method == "POST":
        nousername = False
        nopsw = False
        noconfirm = False
        nomatch = False
        taken = False
        if not request.form.get("username"):
            return render_template("register.html", nousername=True)
            # return apology("Please provide username!")

        elif not request.form.get("password"):
            return render_template("register.html", nopsw=True)
            # return apology("Please provide password!")

        elif not request.form.get("confirmation"):
            return render_template("register.html", noconfirm=True)
            # return apology("Please repeat your password as confirmation!")

        elif request.form.get("password") != request.form.get("confirmation"):
            return render_template("register.html", nomatch=True)
            # return apology("Passwords didn't match. Please retype your password!")

        else:
            user = request.form.get("username")
            psw = request.form.get("password")
            hash = generate_password_hash(psw)
            taken = db.execute("SELECT * FROM administrators WHERE admin_name = :user", user=user)

            if taken:
                return render_template("register.html", taken=True)

            else:
                db.execute("INSERT INTO administrators (admin_name, psw_hash) VALUES (:admin_name, :psw_hash)",
                           admin_name=user, psw_hash=hash)
                rows = db.execute("SELECT * FROM administrators WHERE admin_name = :admin_name",
                                  admin_name=user)
                # Remember which user has logged in
                session["user_id"] = rows[0]["admin_ID"]

                # Redirect user to home page
                return redirect("/")
    else:
        return render_template("register.html")


@app.route("/view", methods=["GET", "POST"])
def view():
    leagues = db.execute("SELECT * FROM leagues")
    return render_template("view.html", leagues=leagues)


@app.route("/table/<string:thisleague>", methods=["GET", "POST"])
def table(thisleague):
    leaguetable = db.execute("SELECT * FROM {} ORDER BY Pts DESC, GD DESC, GS DESC".format(thisleague))
    return render_template("table.html", thisleague=thisleague, leaguetable=leaguetable)


@app.route("/fixtures/<string:thisleague>", methods=["GET", "POST"])
def fixtures(thisleague):
    matches = db.execute("SELECT * FROM fixtures WHERE league = :thisleague ORDER BY round", thisleague=thisleague)
    return render_template("fixtures.html", thisleague=thisleague, matches=matches)


@app.route("/pswchange", methods=["GET", "POST"])
@login_required
def changepsw():
    """Change admin's password"""
    admininfo = db.execute("SELECT * FROM administrators WHERE admin_ID = :admin_ID", admin_ID=session["user_id"])
    if request.method == "POST":
        # Get form input
        old = request.form.get("oldpsw")
        new = request.form.get("newpsw")
        cnf = request.form.get("confirmpsw")

        # Check input
        if not old:
            return render_template("passwordchange.html", noold=True)
            # return apology("Please type old password!")

        elif not new:
            return render_template("passwordchange.html", nonew=True)
            # return apology("Please type new password!")

        elif not cnf:
            return render_template("passwordchange.html", nocnf=True)
            # return apology("Please repeat your password as confirmation!")

        # Check if old password is correct
        elif not check_password_hash(admininfo[0]["psw_hash"], old):
            return render_template("passwordchange.html", wrongpsw=True)

        # Check if new password and confirmation match
        elif new != cnf:
            return render_template("passwordchange.html", nomatch=True)
            # return apology("Passwords didn't match. Please retype your password!")

        else:
            # Update administrators table with new password hash
            hash = generate_password_hash(new)
            db.execute("UPDATE  administrators SET psw_hash = :hash WHERE admin_name = :admin",
                       hash=hash, admin=admininfo[0]["admin_name"])
            if not result:
                return apology("Sorry, username already taken. Please select different username!")
            else:
                rows = db.execute("SELECT * FROM administrators WHERE admin_name = :admin_name",
                                  admin_name=admininfo[0]["admin_name"])
                # Remember which user has logged in
                session["user_id"] = rows[0]["admin_ID"]

                # Redirect user to home page
                return redirect("/")
    else:
        return render_template("passwordchange.html")


@app.route("/mytable/<string:thisleague>", methods=["GET", "POST"])
@login_required
def mytable(thisleague):
    # Get table data
    leaguetable = db.execute("SELECT * FROM {} ORDER BY Pts DESC, GD DESC, GS DESC".format(thisleague))
    # Return sorted table
    return render_template("mytable.html", thisleague=thisleague, leaguetable=leaguetable)


@app.route("/leagueregistration", methods=["GET", "POST"])
@login_required
def leagueregistration():
    """Register new league admin"""
    if request.method == "POST":

        leaguename = str(request.form.get("leaguename"))

        # Check for league name input
        if not leaguename:
            return render_template("leagueregistration.html", noleaguename=True)
            # return apology("Please fill in the name of the league you wish to register")

        else:
            # To get league admin info
            rows = db.execute("SELECT * FROM administrators WHERE admin_ID = :admin_ID", admin_ID=session["user_id"])
            exists = db.execute("SELECT * FROM leagues WHERE leaguename = :leaguename", leaguename=leaguename)
            if exists:
                return render_template("leagueregistration.html", taken=True)

            else:
                # Add the league in the league table in "db" database
                db.execute("INSERT INTO leagues (leaguename, league_admin, number_of_teams) VALUES (:leaguename, :league_admin, :number_of_teams)",
                           leaguename=leaguename, league_admin=rows[0]["admin_name"], number_of_teams=0)

                db.execute('''CREATE TABLE IF NOT EXISTS {} (
                    teamID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                    teamname VARCHAR(255),
                    P SMALLINT NOT NULL DEFAULT 0,
                    W SMALLINT NOT NULL DEFAULT 0,
                    D SMALLINT NOT NULL DEFAULT 0,
                    L SMALLINT NOT NULL DEFAULT 0,
                    GS INT NOT NULL DEFAULT 0,
                    GA INT NOT NULL DEFAULT 0,
                    GD INT NOT NULL DEFAULT 0,
                    Pts INT NOT NULL DEFAULT 0)'''.format(leaguename))

                return redirect("/leaguemanagement")
    else:
        return render_template("leagueregistration.html")


# Rename league
@app.route("/edit/renameleague/<string:thisleague>", methods=["GET", "POST"])
@login_required
def rename(thisleague):
    if request.method == "POST":
        new_name = request.form.get("new")

        if not new_name:
            return render_template("renameleague.html", thisleague=thisleague, noinput=True)

        taken = db.execute("SELECT * FROM leagues WHERE leaguename = :thisleague", thisleague=new_name)
        if taken:
            return render_template("renameleague.html", thisleague=thisleague, leagueexists=True)

        else:
            db.execute("ALTER TABLE {} RENAME TO {}".format(thisleague, new_name))
            db.execute("UPDATE leagues SET leaguename= :new WHERE leaguename= :thisleague", new=new_name, thisleague=thisleague)

            # Get data from the league with new name and redirect user to "edit" apge
            thisleague = new_name
            teams = db.execute("SELECT * FROM {} ORDER BY Pts DESC, GD DESC, GS DESC".format(thisleague))
            return redirect("/edit/{}".format(thisleague))

    return render_template("renameleague.html", thisleague=thisleague)


@app.route("/edit/deleteleague/<string:thisleague>", methods=["GET", "POST"])
@login_required
def deleteleague(thisleague):
    # If "Yes button is clicked remove league from leagues table and remove league table from the database"
    if request.method == "POST":

        db.execute("DELETE FROM leagues  WHERE leaguename = :thisleague", thisleague=thisleague)
        db.execute("DROP TABLE {}".format(thisleague))
        db.execute("DELETE FROM fixtures  WHERE league = :thisleague", thisleague=thisleague)

        rows = db.execute("SELECT * FROM administrators WHERE admin_ID = :admin_ID", admin_ID=session["user_id"])

        # Select all leagues registered by logged in admin
        myleagues = db.execute("SELECT * FROM leagues WHERE league_admin = :league_admin ORDER BY league_ID",
                               league_admin=rows[0]["admin_name"])

        # Return dictionary with the league data
        return render_template("leaguemanagement.html", myleagues=myleagues)

    return render_template("deleteleague.html", thisleague=thisleague)


@app.route("/edit/addteam/<string:thisleague>", methods=["GET", "POST"])
@login_required
def addteam(thisleague):
    teams = db.execute("SELECT * FROM {} ORDER BY Pts DESC, GD DESC, GS DESC".format(thisleague))

    """Register new league admin"""
    if request.method == "POST":
        teamname = request.form.get("teamname")
        league = db.execute("SELECT * FROM leagues WHERE leaguename = :leaguename", leaguename=thisleague)

        # Check for team name input
        if not teamname:
            return render_template("addteams.html", thisleague=thisleague, teams=teams, noname=True)
            # return apology("Please fill in the name of the team you wish to add to the league")

        # Check if the team name already exists in the league
        registered = db.execute("SELECT teamname FROM {} WHERE teamname = :teamname".format(thisleague), teamname=teamname)
        if registered:
            return render_template("addteams.html", thisleague=thisleague, teams=teams, registered=True)
            # return apology("Team with the same name already exists in this league")
        else:
            # To get league admin info
            rows = db.execute("SELECT * FROM administrators WHERE admin_ID = :admin_ID", admin_ID=session["user_id"])

            # Add the team to the selected league
            newteam = db.execute("INSERT INTO {} (teamname) VALUES (:teamname)".format(thisleague), teamname=teamname)
            db.execute("UPDATE leagues SET number_of_teams= :new WHERE leaguename= :thisleague",
                       new=league[0]["number_of_teams"] + 1, thisleague=thisleague)

            # Redirect user to league managment page
            teams = db.execute("SELECT * FROM {} ORDER BY Pts DESC, GD DESC, GS DESC".format(thisleague))
            return render_template("addteams.html", thisleague=thisleague, teams=teams)
    else:
        return render_template("addteams.html", thisleague=thisleague, teams=teams)


@app.route("/edit/rmvteam/<string:thisleague>", methods=["GET", "POST"])
@login_required
def rmvteam(thisleague):
    teams = db.execute("SELECT * FROM {} ORDER BY Pts DESC, GD DESC, GS DESC".format(thisleague))

    """Register new league admin"""
    if request.method == "POST":
        league = db.execute("SELECT * FROM leagues WHERE leaguename = :leaguename", leaguename=thisleague)
        teamname = request.form.get("teamname")

        # Check for team name input
        if not teamname:
            return render_template("removeteam.html", thisleague=thisleague, teams=teams, noname=True)
            # return apology("Please fill in the name of the team you wish to add to the league")

        # Check if the team name already exists in the league
        registered = db.execute("SELECT teamname FROM {} WHERE teamname = :teamname".format(thisleague), teamname=teamname)
        if not registered:
            return render_template("removeteam.html", thisleague=thisleague, teams=teams, noteam=True)
            # return apology("Team with this name does not exist in this league")

        else:
            # Delete the team from the selected league
            db.execute("DELETE FROM {}  WHERE teamname = :teamname".format(thisleague), teamname=teamname)
            db.execute("UPDATE leagues SET number_of_teams= :new WHERE leaguename= :thisleague",
                       new=league[0]["number_of_teams"] - 1, thisleague=thisleague)

            # Redirect user to edit page
            teams = db.execute("SELECT * FROM {} ORDER BY Pts DESC, GD DESC, GS DESC".format(thisleague))

            return render_template("editpage.html", thisleague=thisleague, teams=teams)
    else:
        return render_template("removeteam.html", thisleague=thisleague, teams=teams)


@app.route("/leaguemanagement", methods=["GET", "POST"])
@login_required
def manage():
    rows = db.execute("SELECT * FROM administrators WHERE admin_ID = :admin_ID", admin_ID=session["user_id"])

    # Select all leagues registered by logged in admin
    myleagues = db.execute("SELECT * FROM leagues WHERE league_admin = :league_admin ORDER BY league_ID",
                           league_admin=rows[0]["admin_name"])

    # Return dictionary with the league data
    return render_template("leaguemanagement.html", myleagues=myleagues)


@app.route("/edit/result/<string:thisleague>", methods=["GET", "POST"])
@login_required
def result(thisleague):
    teams = db.execute("SELECT * FROM {} ORDER BY Pts DESC, GD DESC, GS DESC".format(thisleague))
    """Add new result to the league"""
    if request.method == "POST":
        # Get input from html
        hometeam = request.form.get("hometeam")
        awayteam = request.form.get("awayteam")
        hg = int(request.form.get("homescore"))
        ag = int(request.form.get("awayscore"))
        day = request.form.get("matchdate")
        matchweek = request.form.get("matchweek")

        hw = 0
        aw = 0
        d = 0
        ph = 0
        pa = 0
        p = 0

        if not ag:
            ag = 0
        if not hg:
            hg = 0

        # Check for team input:
        if not hometeam or hometeam == "Select team":
            return render_template("result.html", thisleague=thisleague, teams=teams, nohometeam=True)
            # return apology("Please select home and away team")

        elif not awayteam or awayteam == "Select team":
            return render_template("result.html", thisleague=thisleague, teams=teams, noawayteam=True)
            # return apology("Please select home and away team")

        elif hometeam == awayteam:
            return render_template("result.html", thisleague=thisleague, teams=teams, sameteam=True)
            # return apology("You've entered the same team twice")

        # Check for score input
        elif hg < 0 or ag < 0:
            return render_template("result.html", thisleague=thisleague, teams=teams, wrongscore=True)
            # return apology("Please fill the complete score!")

        elif not day:
            return render_template("result.html", thisleague=thisleague, teams=teams, noday=True)

        elif not matchweek:
            return render_template("result.html", thisleague=thisleague, teams=teams, noround=True)

        # Else evaluate result
        else:
            if hg > ag:
                p = 1
                hw = 1
                aw = 0
                d = 0
                ph = 3
                pa = 0

            elif hg < ag:
                p = 1
                hw = 0
                aw = 1
                d = 0
                ph = 0
                pa = 3

            elif hg == ag:
                p = 1
                hw = 0
                aw = 0
                d = 1
                ph = 1
                pa = 1

            # Store the match in fixture table

            # Check that the same team don't play more than once during the same matchweek in the same legue
            leaguefixtures = db.execute("SELECT * FROM fixtures WHERE league = :thisleague AND round = :matchweek AND (hometeam = :hometeam OR hometeam = :awayteam) AND (awayteam = :hometeam OR awayteam = :awayteam)",
                                        thisleague=thisleague, matchweek=matchweek, hometeam=hometeam, awayteam=awayteam)

            if leaguefixtures:
                return render_template("result.html", thisleague=thisleague, teams=teams, played=True)

            else:
                db.execute("INSERT INTO fixtures (league, round, hometeam, awayteam, homescore, awayscore, matchdate) VALUES (:thisleague, :matchweek, :hometeam, :awayteam, :hg, :ag, :day)",
                           thisleague=thisleague, matchweek=matchweek, hometeam=hometeam, awayteam=awayteam, hg=hg, ag=ag, day=day)

            # Get the teams from the league table tp access their stats
            teams = db.execute("SELECT * FROM {} ORDER BY Pts DESC, GD DESC, GS DESC".format(thisleague))
            home = db.execute("SELECT * FROM {} WHERE teamname = :hometeam".format(thisleague), hometeam=hometeam)
            away = db.execute("SELECT * FROM {} WHERE teamname = :awayteam".format(thisleague), awayteam=awayteam)

            # Add result to the table
            db.execute('''UPDATE {} SET
                P = :p1,
                W = :w1,
                D = :d1,
                L = :l1,
                GS = :gs1,
                GA = :ga1,
                GD = :gd1,
                Pts = :pts1 WHERE teamname= :hometeam'''.format(thisleague), hometeam=hometeam, p1=home[0]["P"] + p, w1=home[0]["W"] + hw, d1=home[0]["D"] + d, l1=home[0]["L"] + aw,
                       gs1=home[0]["GS"] + hg, ga1=home[0]["GA"] + ag, gd1=(home[0]["GS"] + hg)-(home[0]["GA"] + ag), pts1=home[0]["Pts"] + ph)

            db.execute('''UPDATE {} SET
                P = :p1,
                W = :w1,
                D = :d1,
                L = :l1,
                GS = :gs1,
                GA = :ga1,
                GD = :gd1,
                Pts = :pts1 WHERE teamname= :awayteam'''.format(thisleague), awayteam=awayteam, p1=away[0]["P"] + p, w1=away[0]["W"] + aw, d1=away[0]["D"] + d, l1=away[0]["L"] + hw,
                       gs1=away[0]["GS"] + ag, ga1=away[0]["GA"] + hg, gd1=(away[0]["GS"] + ag)-(away[0]["GA"] + hg), pts1=away[0]["Pts"] + pa)

            teams = db.execute("SELECT * FROM {} ORDER BY Pts DESC, GD DESC, GS DESC".format(thisleague))
            return render_template("result.html", thisleague=thisleague, teams=teams)

    else:
        return render_template("result.html", thisleague=thisleague, teams=teams)


@app.route("/edit/datachange/<string:thisleague>", methods=["GET", "POST"])
@login_required
def change(thisleague):
    teams = db.execute("SELECT * FROM {} ORDER BY Pts DESC, GD DESC, GS DESC".format(thisleague))
    # Change data
    if request.method == "POST":
        team = request.form.get("teamname")
        item = request.form.get("item")
        value = request.form.get("new")

        # CHeck if all input is provided
        if not team or team == "Select team":
            return render_template("datachange.html", thisleague=thisleague, teams=teams, noteam=True)
            # return apology("Please select a team")

        elif not item or item == "What do you want ot change?":
            return render_template("datachange.html", thisleague=thisleague, teams=teams, noitem=True)
            # return apology("Please select item you wish to change")

        elif not value:
            return render_template("datachange.html", thisleague=thisleague, teams=teams, novalue=True)
            # return apology("Please enter the new value of selected item")

        if item == "Team name":
            item = "teamname"

        else:
            value = int(request.form.get("new"))

        thisteam = db.execute("SELECT * FROM {} WHERE teamname = :team".format(thisleague), team=team)
        db.execute("UPDATE {} SET {} = :value WHERE teamname = :team".format(thisleague, item), value=value, team=team)
        thisteam = db.execute("SELECT * FROM {} WHERE teamname = :team".format(thisleague), team=team)
        db.execute("UPDATE {} SET GD = :ngd WHERE teamname = :team".format(
            thisleague), ngd=thisteam[0]["GS"] - thisteam[0]["GA"], team=team)
        teams = db.execute("SELECT * FROM {} ORDER BY Pts DESC, GD DESC, GS DESC".format(thisleague))

        return render_template("datachange.html", thisleague=thisleague, teams=teams)

    return render_template("datachange.html", thisleague=thisleague, teams=teams)


@app.route("/edit/<string:thisleague>", methods=["GET", "POST"])
@login_required
def edit(thisleague):
    # league = db.execute("SELECT * FROM leagues WHERE leaguename = :thisleague", thisleague=thisleague)

    # Select all teams registered in this league
    teams = db.execute("SELECT * FROM {} ORDER BY Pts DESC, GD DESC, GS DESC".format(thisleague))

    # Return dictionary with the league data
    return render_template("editpage.html", teams=teams, thisleague=thisleague)


@app.route("/leaguefixtures/<string:thisleague>", methods=["GET", "POST"])
@login_required
def myfixtures(thisleague):
    matches = db.execute("SELECT * FROM fixtures WHERE league = :thisleague ORDER BY round", thisleague=thisleague)
    return render_template("myfixtures.html", thisleague=thisleague, matches=matches)


@app.route("/edit/deleteresult/<string:thisleague>", methods=["GET", "POST"])
@login_required
def deleteresult(thisleague):
    results = db.execute("SELECT * FROM fixtures WHERE league = :thisleague ORDER BY round", thisleague=thisleague)
    """Remove the result from the league table and from fixtures"""
    if request.method == "POST":
        # Get input from html
        hometeam = request.form.get("hometeam")
        awayteam = request.form.get("awayteam")
        hg = int(request.form.get("homescore"))
        ag = int(request.form.get("awayscore"))
        day = request.form.get("matchdate")
        matchweek = request.form.get("round")

        hw = 0
        aw = 0
        d = 0
        ph = 0
        pa = 0
        p = 0

        # Evaluate result
        print("checked")
        if hg > ag:
            p = 1
            hw = 1
            aw = 0
            d = 0
            ph = 3
            pa = 0

        elif hg < ag:
            p = 1
            hw = 0
            aw = 1
            d = 0
            ph = 0
            pa = 3

        elif hg == ag:
            p = 1
            hw = 0
            aw = 0
            d = 1
            ph = 1
            pa = 1

        # Delete the match from fixtures table
        db.execute("DELETE FROM fixtures WHERE matchdate = :day AND round = :matchweek AND hometeam = :hometeam AND awayteam = :awayteam",
                   day=day, matchweek=matchweek, hometeam=hometeam, awayteam=awayteam)

        # Get the teams from the league table to access they stats
        teams = db.execute("SELECT * FROM {} ORDER BY Pts DESC, GD DESC, GS DESC".format(thisleague))
        home = db.execute("SELECT * FROM {} WHERE teamname = :hometeam".format(thisleague), hometeam=hometeam)
        away = db.execute("SELECT * FROM {} WHERE teamname = :awayteam".format(thisleague), awayteam=awayteam)

        # Remove result from the league table (update tablestats)
        db.execute('''UPDATE {} SET
            P = :p1,
            W = :w1,
            D = :d1,
            L = :l1,
            GS = :gs1,
            GA = :ga1,
            GD = :gd1,
            Pts = :pts1 WHERE teamname= :hometeam'''.format(thisleague), hometeam=hometeam, p1=home[0]["P"] - p, w1=home[0]["W"] - hw, d1=home[0]["D"] - d, l1=home[0]["L"] - aw,
                   gs1=home[0]["GS"] - hg, ga1=home[0]["GA"] - ag, gd1=(home[0]["GS"] - hg)-(home[0]["GA"] - ag), pts1=home[0]["Pts"] - ph)

        db.execute('''UPDATE {} SET
            P = :p1,
            W = :w1,
            D = :d1,
            L = :l1,
            GS = :gs1,
            GA = :ga1,
            GD = :gd1,
            Pts = :pts1 WHERE teamname= :awayteam'''.format(thisleague), awayteam=awayteam, p1=away[0]["P"] - p, w1=away[0]["W"] - aw, d1=away[0]["D"] - d, l1=away[0]["L"] - hw,
                   gs1=away[0]["GS"] - ag, ga1=away[0]["GA"] - hg, gd1=(away[0]["GS"] - ag)-(away[0]["GA"] - hg), pts1=away[0]["Pts"] - pa)

        teams = db.execute("SELECT * FROM {} ORDER BY Pts DESC, GD DESC, GS DESC".format(thisleague))
        return redirect("/edit/{}".format(thisleague))

    else:
        return render_template("deleteresult.html", thisleague=thisleague, results=results)


# Error handler is reused from pset8/finance
def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors (reused from pset8/finance)
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
