from configparser import ConfigParser

def load_config(filename='database.ini', section='postgresql'):
    parser = ConfigParser()   # creates a ConfigParser object
    parser.read(filename)     # reads the database.ini file

    config = {}               # dictionary where credentials will be stored
    if parser.has_section(section):         # checks if [postgresql] exists
        params = parser.items(section)      # gets all key-value pairs
        for param in params:
            config[param[0]] = param[1]     # stores each pair in the dict
    return config
