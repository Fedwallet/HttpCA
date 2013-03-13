HttpCA
======
Web-based Certificate Authority


Components
----------
HttpCA consists of the web role, the web worker role, a signer role and a command line client for the signer.

The web role provides the web interface, and only creates and accepts signing requests and puts jobs into the database.
It provides both a standards-compliant HTML interface and a JSON API.

The web worker role retrieves the jobs from the database and transmits them to the message broker and accepts responses from the broker and stores those in the database.
This intermediate step is primarily meant so that the web role will not have to wait if the broker does not respond immediately, and so that the web role will not have to wait for broker connections.
This role might become obsolete in a next release when I figure out a way to make the web role do this reliably by itself.

The signer role is the role that does the real certificate signing.
It starts three seperate threads, which have different responsibilities.
One thread accepts messages from the broker, and stores them in the database as Rejected, Waiting-For-Approval or Waiting-For-Signature, based on the policy.
The second thread checks for any Waiting-For-Signature jobs in the database, signs those, and then marks them Waiting-For-Tranmission.
The last thread checks for any jobs in the database marked as Waiting-For-Transmission and transmits these on the broker.

The command line client is a client which checks the database for any Waiting-For-Approval requests, shows them one by one, and asks the administrator to approve or reject the certificate requests.


Security
--------
The HttpCA system is built with security as a highly critical, integral, target.

The signer role and web roles will only communicate with eachother through the message broker, and thus need not be able to have access to eachother or even know of the other.

All mesages that are sent to the message broker are signed with a pair of certificates generated during setup by a certificate authority also generated during setup, but which is only used to generate these certificates.

The web role and web worker role need to share a SQL database.
The signer role needs its own SQL database, but this does not have to be (and SHOULD NOT be) shared with the web (worker) roles.


Requirements
------------
HttpCA will require at least python 2.6 or higher.
It also requires a message broker implementing the AMQP protocol.

Furthermore, the web role will require Flask, SQLAlchemy, Flask-SQLAlchemy, Flask-Babel and pika python packages to be installed.
Also, if you want to use beaker database-stored sessions, it requires the beaker python package.

The web worker role and signer role both require the SQLAlchemy and pika python packages.

The command line client only requires the SQLAlchemy package to be present.


Running
-------
Both the web role, the web worker role, the signer role and the command line client are built in python.

The web role can either run stand-alone or hosted in an apache process as wsgi application.

The web worker role and signer role can be ran either as a normal python application or as a unix daemon.

The command line client can only be run as a normal python application.


Scalability
-----------
The web worker role and signer role can be scaled up or down almost indefinetely: they will just queue up their jobs and pick them up one by one.

The web role can also be scaled up or down almost indefinitely: it will work fine placed behind a load balancer.

The command line client is limited in the fact that it does not check if another instance is currently reviewing the same certificate request.
If two administrators run the command line client, they might see the same requests, and the behaviour if they make different decissions is undefined.

The message broker is the only real scalability limit, but this shouldn't be too much of a problem as it too can be load-balanced (with some server implementations of the AMQP protocol).
This part might be replaced or reworked in the future to make it more flexible.
