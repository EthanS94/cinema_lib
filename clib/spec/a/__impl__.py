"""
Specification A functions and utilities for reading and validating databases.
"""

import json
import os
import logging as log
from itertools import product

SPEC_A_JSON_FILENAME = "info.json"
KEY_TYPE = "type"
KEY_VERSION = "version"
VALUE_TYPE = "simple"
VALUE_VERSION = "1.1"
KEY_METADATA = "metadata"
KEY_METADATA_TYPE = "type"
VALUE_METADATA_TYPE = "parametric-image-stack"
KEY_NAME_PATTERN = "name_pattern"
KEY_ARGUMENTS = "arguments"
KEY_ARG_DEFAULT = "default"
KEY_ARG_LABEL = "label"
KEY_ARG_TYPE = "type"
KEY_ARG_VALUES = "values"

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

        if KEY_METADATA not in db:
            log.warning("\"{0}\" not in JSON.".format(KEY_METADATA))
            unnkey_error = True
        elif KEY_METADATA_TYPE not in db[KEY_METADATA]:
            log.warning("\"{0}\" not in \"{1}\".".format(KEY_METADATA_TYPE,
                KEY_METADATA))
            unnkey_error = True
        elif db[KEY_METADATA][KEY_METADATA_TYPE] != VALUE_METADATA_TYPE:
            log.warning("\"{0}\":\"{1}\" is not \"{2}\".".format(
                KEY_METADATA, KEY_METADATA_TYPE, VALUE_METADATA_TYPE))
            unnkey_error = True
        # delay raising these keys

        # check the necessary keys
        key_error = False
        if KEY_NAME_PATTERN not in db:
            log.error("\"{0}\" is not in JSON.".format(KEY_NAME_PATTERN))
            key_error = True

        if KEY_ARGUMENTS not in db:
            log.error("\"{0}\" is not in JSON.".format(KEY_ARGUMENTS))
            key_error = True

        if key_error:
            log.error("Error in checking the keys in \"{0}\"".format(json_path))
            raise Exception("Key check error.")

        # debug the information
        log.info("\"{0}\" is \"{1}\"".format(KEY_NAME_PATTERN, 
            db[KEY_NAME_PATTERN]))
        log.info("Number of arguments is {1}.".format(KEY_ARGUMENTS, 
            len(db[KEY_ARGUMENTS])))

        # check the arguments
        arg_error = False
        for k in db[KEY_ARGUMENTS]:
            v = db[KEY_ARGUMENTS][k]

            if KEY_ARG_DEFAULT not in v:
                log.warning("\"{0}\" missing from argument \"{1}\".".format(
                    KEY_ARG_DEFAULT, k))
                unnkey_error = True
            if KEY_ARG_TYPE not in v:
                log.warning("\"{0}\" missing from argument \"{1}\".".format(
                    KEY_ARG_TYPE, k))
                unnkey_error = True
            if KEY_ARG_LABEL not in v:
                log.warning("\"{0}\" missing from argument \"{1}\".".format(
                    KEY_ARG_LABEL, k))
                unnkey_error = True

            # report values
            if KEY_ARG_VALUES not in v:
                log.error("Values are missing from argument \"{0}\".".format(k))
                arg_error = True
            else:
                log.info("Arguments for \"{0}\" are {1}.".format(k,
                    v[KEY_ARG_VALUES]))

        if arg_error:
            log.error("Missing values for arguments.")
            raise Exception("Missing values for arguments.")

        # check the files
        if not quick:
            n_files = 0
            total_files = 0
            keylist = list(db[KEY_ARGUMENTS].keys())
            for row in product(*[k[KEY_ARG_VALUES] for k in 
                               db[KEY_ARGUMENTS].values()]):
                total_files = total_files + 1
                kv = {k: v for k, v in zip(keylist, row)}
                fp = db['name_pattern'].format(**kv)
                if not os.path.isfile(os.path.join(db_path, fp)):
                    log.error("File \"{0}\" is missing.".format(fp))
                    file_error = True
                else:
                    n_files = n_files + 1

            if n_files != total_files:
                log.error("Only {0} files out of {1} were found.".format(
                    n_files, total_files))
            else:
                log.info("{0} files validated to be present.".format(n_files))
        else:
            log.info("Doing a quick check. Not checking files.")

        # delay raising
        if unnkey_error:
            log.error("Error in checking the keys in \"{0}\"".format(json_path))
            raise Exception("Missing meta-data (but it may work as a Spec A).")
    except Exception as e:
        log.error("Check failed. \"{0}\" is invalid. {1}".format(db_path, e))
        return False

    log.info("Check succeeded.")
    return True

