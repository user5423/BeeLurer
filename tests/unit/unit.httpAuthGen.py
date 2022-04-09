## Currently the only auth that is supported is basic username and password
## that is stored in the url query or the headers, or the body

## Therefore the below tests are for "userpass":

## Test: Does the username follow rules?
##      TODO: Currently there are no rules, but this should be provided
##      --> Is username.length >= minLength?
##      --> Is username.lnegth <= maxLength?

## Test: Does the password follow rules?
##      --> Is password.length >= minLength?
##      --> Is password.length <= maxLength?

## Test: Is the username reused? 
##      ==> That is ok

## Test: Is the password reused?
##      ==> That is ok

## Test: Is the userpass combo reused?
##      ==> It should not (the userpass should be unique)

## Test: What happens when we run out of usernames? (i.e. from the wordlist)
##      ==> It should raise an exception

## Test: What happens when we run out of passwords?
##      ==> This shouldn't happen at the momement since we are generating from `secrets`

## Test: Does the wordlist shuffler work?
##      TODO: The wordlist shuffler needs to be implemented
##      --> Is the shuffled wordlist == original wordlist? 
##      ==> Too many lines for it to be likley that it will be identical
