
import os
import sys
import base64
from getpass import getpass

try:
    from cryptography.fernet import Fernet
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.backends import default_backend
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
except ImportError:
    print("Please install 'cryptography'.")
    sys.exit(1)


class Cy:
    def __init__(self):
        self._xMode = None
        self._xfIn = None
        self._xfOut = None
        self._xPwd = None
        self._xNewPwd = None
        self._xDel = False
        self._xDataLines = None
        self._xToData = False
        printBanner('PyCypher', 'v1.3.5', 'by eaannist', '█')

    def enc(self, input_file=None):
        self._xMode = "enc"
        if input_file:
            if not input_file.strip():
                raise ValueError("Input filename cannot be empty.")
            self._xfIn = input_file
        return self

    def dec(self, input_file=None):
        self._xMode = "dec"
        if input_file:
            if not input_file.strip():
                raise ValueError("Input filename cannot be empty.")
            self._xfIn = input_file
        return self

    def run(self, input_file=None):
        self._xMode = "run"
        if input_file:
            if not input_file.strip():
                raise ValueError("Input filename cannot be empty.")
            if not input_file.endswith('.py.cy'):
                raise ValueError("File must be a .py.cy encrypted Python script.")
            self._xfIn = input_file
        return self

    def encLines(self, output_file=None):
        self._xMode = "enc_lines"
        if output_file:
            if not output_file.strip():
                raise ValueError("Output filename cannot be empty.")
            self._xfOut = output_file
        return self

    def decLines(self, input_file=None):
        self._xMode = "dec_lines"
        if input_file:
            if not input_file.strip():
                raise ValueError("Input filename cannot be empty.")
            self._xfIn = input_file
        return self

    def changeP(self, input_file=None):
        self._xMode = "changeP"
        if input_file:
            if not input_file.strip():
                raise ValueError("Input filename cannot be empty.")
            if not input_file.endswith('.cy'):
                raise ValueError("File must be encrypted (.cy extension).")
            self._xfIn = input_file
        return self

    def newName(self, output_file):
        if not output_file or not output_file.strip():
            raise ValueError("Output filename cannot be empty.")
        invalid_chars = '<>:"/\\|?*'
        if any(char in output_file for char in invalid_chars):
            raise ValueError("Invalid characters in filename.")
        self._xfOut = output_file
        return self

    def Lines(self, data):
        if data is None:
            raise ValueError("Lines data cannot be None.")
        if not isinstance(data, (str, list)):
            raise ValueError("Lines must be a string or list of strings.")
        if isinstance(data, list):
            if not data:
                raise ValueError("Lines list cannot be empty.")
            if not all(isinstance(line, str) for line in data):
                raise ValueError("All lines must be strings.")
        elif isinstance(data, str) and not data.strip():
            raise ValueError("String cannot be empty.")
        self._xDataLines = data
        return self

    def terminalL(self, msg="Enter line: "):
        try:
            line_input = input(msg).rstrip("\r")
        except (EOFError, KeyboardInterrupt):
            raise ValueError("Input cancelled.")

        if self._xDataLines is None:
            self._xDataLines = []
        elif isinstance(self._xDataLines, str):
            self._xDataLines = [self._xDataLines]
        self._xDataLines.append(line_input)
        if self._xMode == "enc":
            self._xMode = "enc_lines"
        return self

    def newP(self, password):
        if not password:
            raise ValueError("New password cannot be empty.")
        if len(password) < 4:
            raise ValueError("Password too short (minimum 4 characters).")
        self._xNewPwd = password
        return self

    def delInput(self):
        self._xDel = True
        return self

    def toData(self):
        """Return data instead of writing to file"""
        self._xToData = True
        return self

    def P(self, password):
        if not password:
            raise ValueError("Password cannot be empty.")
        if len(password) < 4:
            raise ValueError("Password too short (minimum 4 characters).")
        self._xPwd = password
        return self._xExec()

    def terminalP(self, msg="Password: "):
        try:
            self._xPwd = getpass(msg)
        except (EOFError, KeyboardInterrupt):
            raise ValueError("Password input cancelled.")

        if not self._xPwd:
            raise ValueError("Password cannot be empty.")
        if len(self._xPwd) < 4:
            raise ValueError("Password too short (minimum 4 characters).")
        return self._xExec()

    def _xExec(self):
        if self._xMode == "enc":
            return self._xDoEncFile()
        elif self._xMode == "dec":
            return self._xDoDecFile()
        elif self._xMode == "run":
            return self._xDoRunFile()
        elif self._xMode == "enc_lines":
            return self._xDoEncLines()
        elif self._xMode == "dec_lines":
            return self._xDoDecLines()
        elif self._xMode == "changeP":
            return self._xDoChangePwd()
        else:
            raise ValueError("No valid mode selected.")

    def _xKdf(self, password, salt):
        pwd_bytes = bytearray(password.encode("utf-8"))
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=default_backend()
        )
        key_material = kdf.derive(pwd_bytes)
        for i in range(len(pwd_bytes)):
            pwd_bytes[i] = 0
        del pwd_bytes
        key = base64.urlsafe_b64encode(key_material)
        temp_ba = bytearray(key_material)
        for i in range(len(temp_ba)):
            temp_ba[i] = 0
        del key_material
        del temp_ba
        return key

    def _xEncData(self, data, password):
        salt = os.urandom(16)
        key = self._xKdf(password, salt)
        cipher_suite = Fernet(key)
        encrypted_data = cipher_suite.encrypt(data)
        self._xZero(key)
        del key
        return salt + encrypted_data

    def _xDecData(self, enc_data, password):
        if len(enc_data) < 16:
            raise ValueError("Invalid encrypted data format.")

        salt = enc_data[:16]
        encrypted = enc_data[16:]
        key = self._xKdf(password, salt)
        cipher_suite = Fernet(key)
        try:
            decrypted = cipher_suite.decrypt(encrypted)
        except Exception:
            decrypted = None
        self._xZero(key)
        del key
        return decrypted

    def _xZero(self, bdata):
        if isinstance(bdata, bytearray):
            for i in range(len(bdata)):
                bdata[i] = 0
        else:
            temp_ba = bytearray(bdata)
            for i in range(len(temp_ba)):
                temp_ba[i] = 0
            del temp_ba

    def _xWipe(self):
        if self._xPwd is not None:
            temp_ba = bytearray(self._xPwd.encode("utf-8"))
            for i in range(len(temp_ba)):
                temp_ba[i] = 0
            del temp_ba
            self._xPwd = None
        if self._xNewPwd is not None:
            temp_ba2 = bytearray(self._xNewPwd.encode("utf-8"))
            for i in range(len(temp_ba2)):
                temp_ba2[i] = 0
            del temp_ba2
            self._xNewPwd = None

    def _xFileDel(self, filename):
        if not os.path.isfile(filename):
            raise FileNotFoundError(f"Cannot delete: file not found '{filename}'.")
        try:
            size = os.path.getsize(filename)
            with open(filename, "r+b") as f:
                f.write(os.urandom(size))
                f.flush()
                os.fsync(f.fileno())
        except PermissionError:
            raise PermissionError(f"Cannot delete: permission denied '{filename}'.")
        except Exception as e:
            raise ValueError(f"Cannot delete file '{filename}': {str(e)}")

        try:
            os.remove(filename)
        except Exception as e:
            raise ValueError(f"Cannot remove file '{filename}': {str(e)}")

    def _xDoEncFile(self):
        if not self._xfIn:
            raise ValueError("No input file specified.")
        if not os.path.isfile(self._xfIn):
            raise FileNotFoundError(f"File not found: '{self._xfIn}'.")
        if not os.access(self._xfIn, os.R_OK):
            raise PermissionError(f"Cannot read file: '{self._xfIn}'.")

        try:
            with open(self._xfIn, "rb") as f:
                data = f.read()
        except Exception as e:
            raise ValueError(f"Cannot read file '{self._xfIn}': {str(e)}")

        if not data:
            raise ValueError(f"File is empty: '{self._xfIn}'.")

        enc_data = self._xEncData(data, self._xPwd)
        self._xZero(data)
        del data

        if self._xToData:
            result = enc_data
            self._xWipe()
            return result

        out_file = self._xfOut or (self._xfIn + ".cy")

        try:
            with open(out_file, "wb") as f:
                f.write(enc_data)
        except Exception as e:
            raise ValueError(f"Cannot write output file '{out_file}': {str(e)}")

        self._xZero(enc_data)
        del enc_data
        self._xWipe()

        if self._xDel:
            self._xFileDel(self._xfIn)
            print(f"Encrypted and deleted '{self._xfIn}' -> '{out_file}'.")
        else:
            print(f"Encrypted '{self._xfIn}' -> '{out_file}'.")
        return self

    def _xDoDecFile(self):
        if not self._xfIn:
            raise ValueError("No input file specified.")
        if not os.path.isfile(self._xfIn):
            raise FileNotFoundError(f"File not found: '{self._xfIn}'.")
        if not os.access(self._xfIn, os.R_OK):
            raise PermissionError(f"Cannot read file: '{self._xfIn}'.")

        try:
            with open(self._xfIn, "rb") as f:
                enc = f.read()
        except Exception as e:
            raise ValueError(f"Cannot read file '{self._xfIn}': {str(e)}")

        if not enc:
            raise ValueError(f"File is empty: '{self._xfIn}'.")

        dec_data = self._xDecData(enc, self._xPwd)
        self._xZero(enc)
        del enc

        if dec_data is None:
            self._xWipe()
            raise ValueError("Decryption failed: wrong password or corrupted data.")

        if self._xToData:
            result = dec_data
            self._xWipe()
            return result

        if self._xfOut:
            out_file = self._xfOut
        else:
            if self._xfIn.endswith(".cy"):
                out_file = self._xfIn[:-3]
            else:
                out_file = self._xfIn + ".dec"

        try:
            with open(out_file, "wb") as f:
                f.write(dec_data)
        except Exception as e:
            raise ValueError(f"Cannot write output file '{out_file}': {str(e)}")

        self._xZero(dec_data)
        del dec_data
        self._xWipe()

        if self._xDel:
            self._xFileDel(self._xfIn)
            print(f"Decrypted and deleted '{self._xfIn}' -> '{out_file}'.")
        else:
            print(f"Decrypted '{self._xfIn}' -> '{out_file}'.")
        return self

    def _xDoRunFile(self):
        if not self._xfIn:
            raise ValueError("No input file specified.")
        if not os.path.isfile(self._xfIn):
            raise FileNotFoundError(f"File not found: '{self._xfIn}'.")
        if not self._xfIn.endswith(".py.cy"):
            raise ValueError("File must be a .py.cy encrypted Python script.")

        try:
            with open(self._xfIn, "rb") as f:
                enc = f.read()
        except Exception as e:
            raise ValueError(f"Cannot read file '{self._xfIn}': {str(e)}")

        if not enc:
            raise ValueError(f"File is empty: '{self._xfIn}'.")

        dec_data = self._xDecData(enc, self._xPwd)
        self._xZero(enc)
        del enc

        if dec_data is None:
            self._xWipe()
            raise ValueError("Cannot run: decryption failed.")

        try:
            code_str = dec_data.decode("utf-8")
        except UnicodeDecodeError:
            raise ValueError("Invalid Python script encoding.")

        print("Executing decrypted content...")
        try:
            compile(code_str, self._xfIn, 'exec')
            exec(code_str, globals())
            self._xZero(code_str.encode("utf-8"))
            del code_str
        except SyntaxError:
            raise ValueError("Invalid Python syntax in encrypted script.")
        except Exception as e:
            print(f"Execution error: {str(e)}")
        finally:
            print('Execution completed.')

        self._xZero(dec_data)
        del dec_data
        if self._xDel:
            self._xFileDel(self._xfIn)
            print(f"Executed and deleted '{self._xfIn}'.")
        self._xWipe()
        return self

    def _xDoEncLines(self):
        if self._xDataLines is None:
            raise ValueError("No lines data specified.")

        if isinstance(self._xDataLines, list):
            data_str = "\n".join(self._xDataLines)
        else:
            data_str = str(self._xDataLines)

        data_bytes = data_str.encode("utf-8")
        enc_data = self._xEncData(data_bytes, self._xPwd)

        if self._xToData:
            result = enc_data
            self._xZero(data_bytes)
            del data_bytes
            self._xZero(data_str.encode("utf-8"))
            del data_str
            self._xWipe()
            return result

        out_file = self._xfOut or "cyfile.cy"

        try:
            with open(out_file, "wb") as f:
                f.write(enc_data)
        except Exception as e:
            raise ValueError(f"Cannot write output file '{out_file}': {str(e)}")

        self._xZero(data_bytes)
        del data_bytes
        self._xZero(data_str.encode("utf-8"))
        del data_str
        self._xZero(enc_data)
        del enc_data
        self._xWipe()
        print(f"Encrypted lines -> '{out_file}'.")
        return self

    def _xDoDecLines(self):
        if not self._xfIn:
            raise ValueError("No input file specified.")
        if not os.path.isfile(self._xfIn):
            raise FileNotFoundError(f"File not found: '{self._xfIn}'.")

        try:
            with open(self._xfIn, "rb") as f:
                enc = f.read()
        except Exception as e:
            raise ValueError(f"Cannot read file '{self._xfIn}': {str(e)}")

        if not enc:
            raise ValueError(f"File is empty: '{self._xfIn}'.")

        dec_data = self._xDecData(enc, self._xPwd)
        self._xZero(enc)
        del enc

        if dec_data is None:
            self._xWipe()
            raise ValueError("Decryption failed: wrong password or corrupted data.")

        try:
            text = dec_data.decode("utf-8")
        except UnicodeDecodeError:
            raise ValueError("Invalid text encoding in encrypted data.")

        self._xZero(dec_data)
        del dec_data

        if "\n" in text:
            splitted = text.split("\n")
            if len(splitted) > 1:
                result = splitted
            else:
                result = text
        else:
            result = text

        if self._xDel:
            self._xFileDel(self._xfIn)
            print(f"Decrypted and deleted '{self._xfIn}'.")
        else:
            print(f"Decrypted '{self._xfIn}'.")
        self._xWipe()
        return result

    def _xDoChangePwd(self):
        if not self._xfIn:
            raise ValueError("No input file specified.")
        if not os.path.isfile(self._xfIn):
            raise FileNotFoundError(f"File not found: '{self._xfIn}'.")
        if not self._xfIn.endswith('.cy'):
            raise ValueError("File must be encrypted (.cy extension).")
        if not self._xPwd:
            raise ValueError("Old password is missing.")
        if not self._xNewPwd:
            raise ValueError("New password is missing.")

        try:
            with open(self._xfIn, "rb") as f:
                enc = f.read()
        except Exception as e:
            raise ValueError(f"Cannot read file '{self._xfIn}': {str(e)}")

        if not enc:
            raise ValueError(f"File is empty: '{self._xfIn}'.")

        dec_data = self._xDecData(enc, self._xPwd)
        self._xZero(enc)
        del enc

        if dec_data is None:
            self._xWipe()
            raise ValueError("Password change failed: wrong old password.")

        new_enc_data = self._xEncData(dec_data, self._xNewPwd)
        self._xZero(dec_data)
        del dec_data

        try:
            with open(self._xfIn, "wb") as f:
                f.write(new_enc_data)
        except Exception as e:
            raise ValueError(f"Cannot write file '{self._xfIn}': {str(e)}")

        self._xZero(new_enc_data)
        del new_enc_data
        self._xWipe()
        print(f"Password changed for '{self._xfIn}'.")
        return self


def printBanner(nome, versione, autore, filler):
    versione_width = len(versione)
    inner_width = max(len(nome) + versione_width, len(f">> {autore}")) + 4
    border = '    ' + filler * (inner_width + 4)
    line2 = f"    {filler}{filler} {nome.ljust(inner_width - versione_width - 2)}{versione.rjust(versione_width - 2)} {filler}{filler}"
    line3 = f"    {filler}{filler} {f">> {autore}".rjust(inner_width - 2)} {filler}{filler}"
    banner = f"\n{border}\n{line2}\n{line3}\n{border}\n"
    print(banner)