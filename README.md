# TarentSocialWallPython

This project is the backend from project "SocialWall".

## Next Steps
For an easier deployment process of the SocialWall we are working towards moving the frontend and backend portion in a combined project. Because of this both repositories will become deprecated in the near future. 

## Software Architecture & Design 


## Configuration

The configuration can be found here: [docker-compose.yml](./docker-compose.yml)

### Authorization for access of different services

The folder "credentials/json_template" contains the templates for services.

Fill fields in a template file and move this into /credentials/ folder

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

