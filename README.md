# TarentSocialWallPython

This project is backend from project "SocialWall".


## Software Architecture & Design 


## Configuration

The configuration can be found here: [docker-compose.yml](./docker-compose.yml)

### Authorization for access of different services

In folder "credentials/json_template" contains the templates for services

 ###Backend:

    - PORT=12300                   - backend server port
    - DB=mongodb://x.x.x.x:27017   - URI for mongo db
    - DEFAULT-AUTH=True            - use a user data for authentication from db
    - LDAP-USE=False               - use a ldap data for authentication  
    - LDAP=ldaps://x.x.x.x:7636    - URI for LDAP (optional)
    - LDAP-BASE                    - dc=your server,dc=your country
    - LDAP_USER_URI                - uid=%s,cn=users,dc=your server,dc=your
    - LDAP_FILTER                  - (|(&(uid=%s)(memberOf=cn=your access group,cn=groups,dc=your server,dc=your)))    
    - DEBUG=True                   - Debug Modus
    - INTERVAL=15 # in minutes     - interval for fetch a data from connectors


## Build and Run
    
    docker-compose up --build --force-recreate -d







