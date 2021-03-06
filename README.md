# camassassins #

Simple Django and Tropo based application for playing a game of assassins over SMS message.

## Tropo setup ##

Get an account at http://tropo.com, create an application, and go through the 
steps to get yourself text-sending capabilities. Set the SMS Handler URL to
`http://yourserver.com:4242/handleSms`, and create a phone number for it, with
an area code near you. This is the number you'll send all future texts to.

## Django setup ##

On the server you want to run the game on, download this repository. Then, run
`./manage.py syncdb && ./manage.py runserver 0.0.0.0:<port>`. You'll be prompted
about setting up an admin account.

Point your browser at http://yourserver.com:<port>/admin, and add a game. Give it
a name, put the tropo application's  phone number in the `number` spot and the SMS
token in the `token` spot, and check the box for `registration open`.

### Model updates ###

We use south for model schema updates. If the model is ever updated you just need to run `./manage.py schemamigration assassins_app --auto && ./manage.py migrate assassins_app`.

## Player registrations ##

Players send an SMS message "join [id] [alias]" to the Tropo phone number,
where the id is some verifiable value (like an email address), that will be
shown to the player's victims when xe kills them. The alias is only used
for the public scoreboard.

When all players have registered, go back to the admin page, and run the Admin 
Action for assigning targets, and then run the Action for sending initial
targets. Players should receive their targets' ids.

## Playing the game ##

When a player successfully kills xyr target, xe sends a message "kill [id]" where
id is the target's id. A message will be sent to the target, asking xem to confirm.
If xe replies with "yes", xe is removed from the queue and xyr killer gets xyr next target.

When only one player remains, xe has won, and will be notified.

