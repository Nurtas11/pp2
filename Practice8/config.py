from configparser import ConfigParser
def load_config(filename='database.ini', section='postgresql'):
    parser = ConfigParser() #creates a ConfigParser object.
    parser.read(filename)

    config = {} #dictionary where everything is stored(password, host and etc)
    if parser.has_section(section): #checks if [postgresql] exists in the file
        params = parser.items(section) #gets all the key-value pairs
        for param in params:
            config[param[0]] = param[1] #loops through each pair and puts it in the config dictionary
    return config      

