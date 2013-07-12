# camassassins #

Simple Django and Tropo based application for playing a game of assassins over SMS message.

## Tropo setup ##

Get an account at http://tropo.com, create an application, and go through the 
steps to get yourself text-sending capabilities. Set the SMS Handler URL to
`http://yourserver.com:4242/handleSms`, and create a phone number for it, with
an area code near you. This is the number you'll send all future texts to.

## Django setup ##

On the server you want to run the game on, download this repository. Then, run
`./manage.py syncdb && ./manage.py runserver 0.0.0.0:4242 &`

Point your browser at http://yourserver.com:4242/admin, and add a game. Give it
a name, put the tropo application's  phone number in the `number` spot, and
check the box for `registration open`.


