# You would not run this as a full script. Instead, pick out the one or two commands you might want to use.
# Basically, I am looking to get text output of username:password and username:hash from public password dumps.

SEARCHTERM=<probably a domain name>

# LastFM dump:
grep $SEARCHTERM ./lastfm.txt  | cut -f 3-4 | sed 's/       /:/g'
