"""
Specification A functions and utilities for reading and validating databases.
"""

import json
import os
import logging as log

SPEC_A_JSON_FILENAME = "info.json"
KEY_TYPE = "type"
KEY_VERSION = "version"
VALUE_TYPE = "simple"
VALUE_VERSION = "1.1"

def get_dictionary(db_path, json_path=SPEC_A_JSON_FILENAME):
    """
    Return a JSON dictionary, assuming a valid Spec A database. Does
    not validate that it is a proper Spec A database. 

    arguments:
        db_path : string
            POSIX path to Cinema database
        json_path : string = SPEC_A_JSON_FILENAME
            POSIX relative path to Cinema JSON 

    returns:
        a dictionary of the contents of the Cinema JSON if the file can
        be opened, otherwise returns None
    """

    json_fn = os.path.join(db_path, json_path)
    if not os.path.exists(json_fn):
        return False
   
    try:
        with open(json_fn) as jf:
            return json.load(jf)
    except:
        return None

def check_database(db_path, json_path=SPEC_A_JSON_FILENAME, quick=False):
    """
    Validate a Spec A database.

    arguments:
        db_path : string
            POSIX path to Cinema database
        json_path : string = SPEC_A_JSON_FILENAME
            POSIX relative path to Cinema JSON
        quick : boolean = False
            if True, perform a quick check, which means only checking
            validating the JSON, and not the files

    returns:
        True if it is valid, False otherwise

    side effects:
        logs error and info messages to the logger
    """

    log.info("Checking database \"{0}\" as Spec A.".format(db_path))

    try:
        db = get_dictionary(db_path, json_path)
        if db == None:
            log.error("Error opening \"{0}\".".format(json_path))
            raise Exception("Error opening \"{0}\".".format(json_path))

        # check the unnecessary keys
        unnkey_error = False
        if KEY_TYPE not in db:
            log.warning("\"{0}\" not in JSON.".format(KEY_TYPE))
            unnkey_error = True
        elif db[KEY_TYPE] != VALUE_TYPE:
            log.warning("\"{0}\" is not \"{1}\".".format(KEY_TYPE, VALUE_TYPE))
            unnkey_error = True

        if KEY_VERSION not in db:
            log.warning("\"{0}\" not in JSON.".format(KEY_VERSION))
            unnkey_error = True
        elif db[KEY_VERSION] != VALUE_VERSION:
            log.warning("\"{0}\" is not \"{1}\".".format(KEY_VERSION, 
                VALUE_VERSION))
            unnkey_error = True

        # delay raising
        if unnkey_error:
            log.error("Error in checking the keys in \"{0}\"".format(json_path))
            raise Exception("Key check error.")
    except Exception as e:
        log.error("Check failed. \"{0}\" is invalid. {1}".format(db_path, e))
        return False

    log.info("Check succeeded.")
    return True

