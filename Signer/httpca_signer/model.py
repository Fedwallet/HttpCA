# Copyright (c) 2013, Patrick Uiterwijk <puiterwijk@gmail.com>
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#     * Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#     * Neither the name of Patrick Uiterwijk nor the
#       names of its contributors may be used to endorse or promote products
#       derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL Patrick Uiterwijk BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String
from sqlalchemy.types import Enum

Base = declarative_base()


class Certificate(Base):
    __tablename__ = 'certificate'

    id                  = Column(Integer                # The key identifier
                                , primary_key=True)
    Type                = Column(Enum( 'CA'             # sub-CA certificate
                                     , 'Server'         # Server certificate
                                     , 'User'           # User certificate
                                     )
                                )
    CommonName          = Column(String)                # Subject CN
    OrganizationalUnit  = Column(String)                # Subject OU
    Organization        = Column(String)                # Subject O
    Location            = Column(String)                # Subject L
    State               = Column(String)                # Subject S
    Country             = Column(String)                # Subject CO
    CSR                 = Column(String)                # The certificate signing request PEM string
    Certificate         = Column(String)                # The signed certificate PEM string
    Status = Column(Enum( 'Waiting-For-Approval'        # Certificate needs administrator approval
                        , 'Waiting-For-Signature'       # Certificate is ready to be signed
                        , 'Waiting-For-Transmission'    # Certificate is signed and is ready for transmission to the web interface
                        , 'Valid'                       # Certificate is valid
                        , 'Expired'                     # Certificate has expired
                        , 'Revoked-Unspecified'         # From here on, only revocation reasons follow
                        , 'Revoked-KeyCompromise'
                        , 'Revoked-CACompromise'
                        , 'Revoked-AffiliationChanged'
                        , 'Revoked-Superseded'
                        , 'Revoked-CessationOfOperation'
                        , 'Revoked-CertificateHold'
                        )
                   )




from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
def create_tables(db_url, debug=False):
    """ Create the tables in the database using the information from the
    url obtained.

    :arg db_url, URL used to connect to the database. The URL contains
    information with regards to the database engine, the host to connect
    to, the user and password and the database name.
      ie: <engine>://<user>:<password>@<host>/<dbname>
    :kwarg debug, a boolean specifying wether we should have the verbose
    output of sqlalchemy or not.
    :return a session that can be used to query the database.
    """
    engine = create_engine(db_url, echo=debug)
    db.Model.metadata.create_all(engine)

    sessionmak = sessionmaker(bind=engine)
    return sessionmak()
