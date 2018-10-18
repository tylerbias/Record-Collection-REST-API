# Record-Collection-REST-API
Record Collection REST API - Tyler Bias, Final Project, Oregon State University 2018

Python, Flask, Google NoSQL Cloud Datastore

Video demonstrating app functionality using hardcoded account tokens:
https://www.youtube.com/watch?v=g3dMY6wzK9k

Tyler Bias
3/18/18
Final Project Documentation

GET /
Displays two links, one to page of all records, one to page of all users. If given an access token,
the welcome page will display a message, “Logged in as <username>.”

GET /records
Displays all records, belonging to all owners (or at least the first page of all records).

POST /records
Creates a new record. Can only be used if given an access token for a valid account. A record
cannot be created without an owner, and you need a valid account in order to establish
ownership of a record. Given a json object containing two fields, “Artist” and “Title”. This
information is then passed through MusicBrainz API, where the release date / year is collected,
along with a link to the album art.

GET /users
Displays all users. Currently the only functional verb for the users route, because the accounts
used up to this point have been hardcoded. The API does not currently support the creation of
new accounts.

GET /users/me
Displays the user data for the currently logged in user, as determined by the access token
bundled with the request.

GET /users/me/collection
Displays the collection of records belonging to the currently logged in user, again using the
access token to identify the user

PATCH /users/me/username
Allows a user to change her username on the site. Relies on the access token to pull up the
appropriate user entity in order to manipulate the data. Cannot be used without the access
token.

GET /users/<user_id>
Directly access the information belonging to a specific user account. Does not rely on an access
token. Cannot modify any information (read only).

GET /users/<user_id>/collection
Directly access the collection of records belonging to a specific user account. Does not rely on
an access token. Cannot modify any information.

GET /records/<record_id>
Directly access a specific record entity, belonging to some user. Read only access, cannot
modify the record in any way. Does not rely on an access token.

DELETE /records/<record_id>
Delete a record entity. Checks to ensure that the user making the request has the proper
authorization before proceeding. Will reject any request that is not accompanied by the correct
access token which identifies the user as the owner of the record in question. When the record
is deleted, it is removed from the user’s collection list as well as the entity itself being eliminated.

MusicBrainzNGS:
The API I used was a basic music metadata service. It gives you the ability to query a
huge database of music releases and pull a wide breadth of information about any particular
album, single, etc. I did not want to overcomplicate things for this project, so I kept the
information I was pulling to a minimum. I use artist and title fields to search for a release group.
Release groups are the somewhat abstract entities that musicbrainz uses to represent some
album, overall, as opposed to individual releases, meaning re-issues, foreign versions, etc. of
the same album. From the release group I pulled only two things, cover art, and release date
information.
