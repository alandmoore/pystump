#########################
# PyStump CONFIGURATION #
#########################

# Comment or change to false to stop debugging output:
DEBUG = True

# If you move or rename the database file, specify the path and filename here:
DATABASE_FILE = "pystump.db"

# Uncomment the "HOST" line to make PyStump accessible
# to other computers on the LAN:

# HOST="0.0.0.0"

# Edit and uncomment the "PORT" line if you want to use a different port:

# PORT=6000

# SECRET_KEY should be set to some unique, random value

SECRET_KEY = "this is a bad secret key and you need to change it"

# The uploads folder is for background images

UPLOAD_FOLDER = "uploads"


######################
# LDAP Configuration #
######################

# Login backend.  Valid values are "dummy", "AD", or "eDirectory"
AUTH_BACKEND = "dummy"

# Configuration values for LDAP
LDAP_CONFIG = {
        "host" : None, #The IP or hostname of the LDAP server
        "port" : None, #The Port for LDAP
        "base_dn" : None, #The DN to start searching for login names
        "bind_dn_username" : None, #If you need a bind DN for your LDAP
        "bind_dn_password" : None, #PW for bind DN
        "require_group" : None, #Login requires membership in this group
        "ssl" : None #Use SSL
        }
