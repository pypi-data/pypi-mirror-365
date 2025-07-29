# PyCypher

**PyCypher** is a Python library based on the library [cryptography](https://pypi.org/project/cryptography/) that provides secure encryption and decryption of files and strings, plus an optional decrypt&execute option encrypted Python scripts. It attempts to securely wipe in-memory data and input files (on a best-effort basis, not guaranteed on all systems).

## Installation

```bash
pip install PyCypherLib

```
## Usage

```python

# Import the PyCypher library:
from PyCypher import Cy

# Base methods for encryption and decryption ations
# using the .P() method to type the password manually
Cy().enc("file.txt").P("yourpassword")
Cy().dec("file.txt.cy").P("yourpassword")

# With rhe .run() method you can 'decrypt&run' an encrypted python scrypt
Cy().run("file.py.cy").P("yourpassword")

# By default the encrypted file is saved with the .cy extension added to the input file name
Cy().dec("file.txt.cy").P("yourpassword")

# Use the .newNme() method to specify the output file name 
Cy().enc("file.txt").newName("file.enc").P("yourpassword")

# Use the .delInput() method to automatically delete the input file
Cy().enc("file.txt").newName("file.cy").delInput().P("mypassword")
Cy().dec("file.cy").newName("file.txt").delInput().P("mypassword")

# Use the .toData() method to get encrypted/decrypted data instead of writing to file
encrypted_data = Cy().enc("file.txt").toData().P("yourpassword")
decrypted_data = Cy().dec("file.txt.cy").delInput().toData().P("yourpassword")

# Use the .terminalP() method to insert the password in the terminal with your own message
Cy().dec("file.enc").newName("file.txt").delInput().terminalP("Please enter password: ")

# Use the .encLines() and Lines() methods to encrypt a single string or a list of strings
# the default output file will be cyfile.cy 
Cy().encLines().Lines('yoursecretkey').P('yourpassword')
Cy().encLines().Lines(['yoursecretkey', 'yoursecrettoken']).P('yourpassword')

# Use one or more .terminalL() methods to add lines to encrypt by terminal
# and you can specify an output file name as .encLines() argument
Cy().encLines('credentials.cy')\
    .terminalL('Enter your secret key: ')\
    .terminalL('Enter your secret token: ')\
    .terminalP('Enter a password to encrypt your credentials: ')

# Use the .decLines() method to decrypt the encrypted string or strings
# it will return a string or a list of strings
key = Cy().decLines('key.cy').terminalP('Enter a password to access your secret key: ')
key,token = Cy().decLines('credentials.cy').terminalP('Enter a password to access your credentials: ')

# Use the .changeP() and .newP() methods to change the encryption password of an encrypted file
Cy().changeP('credentials.cy').newP('newpassword').P('oldpassword')

```

## Development status

**PyCypher** is a work-in-progress personal project. Suggestions, feature requests, and constructive feedback are highly welcome. Feel free to open an issue or submit a pull request.