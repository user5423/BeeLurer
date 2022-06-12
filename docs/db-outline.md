## Interfaces:

### Database Module (Python)

This class `_database` will have a set of methods that interact with the relational Database on behalft of the user

1. `async  _database.hasBaitCredentials(credentials: object) -> bool`
    - This checks whether bait credentials exist in the database
2. `async  _database.logBaitConnection(credentials: namedTuple, ipAddress: str, datetime: datetime) -> None`
    - Logs any bait credential request in the database
3. `async _database.createBaitAttempt(credentials: namedTuple, ipAddress: str, datetime: datetime) -> None
    - Creates a corresponding bait attempt in the database

**TODO**: Need to modify the arguments for the above methods (they are missing some information), and are better to be rearranged


`credentials` at the moment will be a `namedTuple` with attributes
- `credentials.username`
- `credentials.password`


**NOTE**: The database related moduled MUST be asynchronous (or at least ran concurrently in another way)

**NOTE**: A future goal after MVP is to support multiple authentication methods


### ER Table Design

Below, I've provided a base outline of what the tables could look like.


#### "BaitAttempts" Table

____________________________________________________________________________________________________________________________________________
|     |               |                 |                   |                    |                   |                  |                   |
| ID  |  srcIPAddress |  destIPAddress  |  Microdescriptor  |   CredentialID     |  CreationDatetime |  AccessAttempts  |  LastAccessDT     |
|_____|_______________|_________________|___________________|____________________|___________________|__________________|___________________|

**Goal:** The point of this table is to store running bait connections

- ID (int) - ** Primary Key **
- srcIPAddress (str)
- destIPAddress (str)
- Microdescriptor (str)
- CredentialID (int) - **Foreign Key** for "Credentials Table"
- CreationDatetime (datetime)
- AccessAttemps (int)
- LastAccessDatetime (datetime)



#### "Credentials" Table

_________________________________
|     |            |            |
| ID  |  Username  |  Password  |
|_____|____________|____________|

**Goal:** The point of this table is to store credentials for the corresponding "BaitAttempts" table

- ID (int) - **Primary Key**
- Username (str) 
- Password (str) - DBMS is likely to have inbuilt hashing for this (USE IT!!!!)


**NOTE:** The credential set (e.g. {"Username, "Password"} should only be used uniquely (per destIPAddress)


FUTURE Proofing:
- I've outlined a basic `credentials` table
- However, there will likely be future support for other authentication methods
- Therefore this table will likely be modified to
    __________________________________________________________
    |              |                |                        |
    | ID (Primary) | CredentialType | CredentialID (Foreign) |
    |______________|________________|________________________|

- where the `credentialID` will be a foreign key for the table that corresponds to the selected `credentialType`
- and there could be tables named:
    - userpass
    - APIKey
    - JWT
    - etc.


#### "BaitConnections" Table

_____________________________________________________________________________________________________
|     |               |                 |             |                       |                     |
| ID  |  srcIPAddress |  destIPAddress  |   Datetime  |  ResourceRequestType  |  ResourceRequestID  |
|_____|_______________|_________________|_____________|_______________________|_____________________|

**Goal:** This table should contain logs of requests that the honeypot server wishes to store

- ID (int) - **PrimaryKey**
- srcIPAddress (str)
- destIPAddress (str)
- Datetime (datetime
- ResourceRequestType (enum)
- ResourceRequestID (int) - **Foregin Key**

There are different types of requests/protocols, which are likely to have different attributes, which is why they've been split into different tables:
- HTTP
- FTP
- SMTP
- etc.



#### "ResourceRequest" Table

___________________________________________________
|     |                     |                     |
|  ID | ResourceRequestType |  ResourceRequestID  |
|_____|_____________________|_____________________|


- ID (int) - **Primary Key**
- ResourceRequestType (enum) 
    - HTTP
    - SMTP
    - FTP


#### Request Specific tables

** "HTTPrequest" Table **

________________________________________________________
|      |       |            |                    |         
|  ID  |  URL  |  HTTP Verb | User-String Header |  Metadata (undecided data - could be other headers or payload even) ...
|______|_______|____________|____________________|_______


** "FTPrequest" Table **

_______________________________________
|      |       |                |         
|  ID  |  URL  |  FTP Operation | Metadata  (undecided data - could be other headers of payload even) ...
|______|_______|________________|_______


** "SMTPrequest" Table **


**TODO** : Finish SMTP basic table design


**NOTE**: I've provided basic types for each of the attributes. **HOWEVER**, relational DBs have their own custom types that enforce entity and referential constraints. You need to research the neccessary types for the DBMS you employed. e.g. `primarykey` or `hashedpassword` might be one.




### Work TODO

This describes what work needs to be done:
- Finalize the arguments for the `_database` class methods
- Create ER diagram to reflect what tables will be created
- Create tables in chosen SQL language (e.g. MySQL)
- Create setup script for the Database
- Create methods for the `_database` class as listed above
- Create test cases











