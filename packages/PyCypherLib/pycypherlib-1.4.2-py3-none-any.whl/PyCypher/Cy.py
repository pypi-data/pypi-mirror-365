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

try:
    from argon2 import PasswordHasher
    from argon2.low_level import hash_secret_raw, Type
    ARGON2_AVAILABLE = True
except ImportError:
    ARGON2_AVAILABLE = False
    print("Warning: argon2-cffi not installed. Using PBKDF2 as default.")


class Cy:
    def __init__(self, kdf_type=None):
        self._xMode = None
        self._xfIn = None
        self._xfOut = None
        self._xPwd = None
        self._xNewPwd = None
        self._xDel = False
        self._xDataLines = None
        self._xToData = False

        if kdf_type is None:
            self._kdf_type = "A" if ARGON2_AVAILABLE else "P"
        elif kdf_type.upper() in ["A", "P"]:
            if kdf_type.upper() == "A" and not ARGON2_AVAILABLE:
                print("Warning: argon2-cffi not installed. Using PBKDF2 as default")
                self._kdf_type = "P"
            else:
                self._kdf_type = kdf_type.upper()
        else:
            raise ValueError("Invalid KDF type. Use 'A' for Argon2 or 'P' for PBKDF2")

        kdf_name = "Argon2" if self._kdf_type == "A" else "PBKDF2"
        printBanner('PyCypher', 'v1.4.2', 'by eaannist', '█')
        print(f"Using {kdf_name} KDF.")

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
        if len(password) < 8:
            raise ValueError("Password too short (minimum 8 characters).")
        self._xNewPwd = password
        return self

    def delInput(self):
        self._xDel = True
        return self

    def toData(self):
        self._xToData = True
        return self

    def P(self, password):
        if not password:
            raise ValueError("Password cannot be empty.")
        if len(password) < 8:
            raise ValueError("Password too short (minimum 8 characters).")
        self._xPwd = password
        return self._xExec()

    def terminalP(self, msg="Password: "):
        try:
            self._xPwd = getpass(msg)
        except (EOFError, KeyboardInterrupt):
            raise ValueError("Password input cancelled.")

        if not self._xPwd:
            raise ValueError("Password cannot be empty.")
        if len(self._xPwd) < 8:
            raise ValueError("Password too short (minimum 8 characters).")
        return self._xExec()

    def _xExec(self):
        match self._xMode:
            case "enc":
                return self._xDoEncFile()
            case "dec":
                return self._xDoDecFile()
            case "run":
                return self._xDoRunFile()
            case "enc_lines":
                return self._xDoEncLines()
            case "dec_lines":
                return self._xDoDecLines()
            case "changeP":
                return self._xDoChangePwd()
            case _:
                raise ValueError("No valid mode selected.")

    def _detect_kdf_type(self, enc_data):
        if len(enc_data) < 6:
            return "legacy"

        match True:
            case _ if enc_data.startswith(b"CY_A2_"):
                return "A"
            case _ if enc_data.startswith(b"CY_PB_"):
                return "P"
            case _:
                return "legacy"

    def _xKdfArgon2(self, password, salt):
        if not ARGON2_AVAILABLE:
            raise ValueError("Argon2 not available. Install argon2-cffi.")

        try:
            hash_result = hash_secret_raw(
                secret=password.encode("utf-8"),
                salt=salt,
                time_cost=3,
                memory_cost=65536,
                parallelism=1,
                hash_len=32,
                type=Type.ID
            )

            key = base64.urlsafe_b64encode(hash_result)
            hash_result_ba = bytearray(hash_result)

            for i in range(len(hash_result_ba)):
                hash_result_ba[i] = 0
            del hash_result_ba
            del hash_result

            return key
        except Exception as e:
            raise ValueError(f"Argon2 key derivation failed: {str(e)}")

    def _xKdfPBKDF2(self, password, salt):
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

    def _xKdf(self, password, salt, kdf_type=None):
        if kdf_type is None:
            kdf_type = self._kdf_type

        match kdf_type:
            case "A":
                return self._xKdfArgon2(password, salt)
            case "P":
                return self._xKdfPBKDF2(password, salt)
            case _:
                raise ValueError(f"Unknown KDF type: {kdf_type}")

    def _xEncData(self, data, password):
        salt = os.urandom(16)
        key = self._xKdf(password, salt)
        cipher_suite = Fernet(key)
        encrypted_data = cipher_suite.encrypt(data)
        self._xZero(key)
        del key

        if self._kdf_type == "A":
            magic = b"CY_A2_"
        else:
            magic = b"CY_PB_"

        return magic + salt + encrypted_data

    def _xDecData(self, enc_data, password):
        detected_kdf = self._detect_kdf_type(enc_data)

        if detected_kdf == "legacy":
            if len(enc_data) < 16:
                raise ValueError("Invalid encrypted data format.")
            salt = enc_data[:16]
            encrypted = enc_data[16:]
            kdf_type = "P"
        else:
            if len(enc_data) < 22:
                raise ValueError("Invalid encrypted data format.")
            salt = enc_data[6:22]
            encrypted = enc_data[22:]
            kdf_type = detected_kdf

        key = self._xKdf(password, salt, kdf_type)
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
        kdf_name = "Argon2" if self._kdf_type == "A" else "PBKDF2"

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
            print(f"Encrypted [{kdf_name}] and deleted '{self._xfIn}' -> '{out_file}'.")
        else:
            print(f"Encrypted [{kdf_name}] '{self._xfIn}' -> '{out_file}'.")
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

        script_globals = {
            '__name__': '__main__',
            '__file__': self._xfIn.replace('.cy', ''),
            '__builtins__': __builtins__,
        }

        original_cwd = os.getcwd()
        script_dir = os.path.dirname(os.path.abspath(self._xfIn))
        if script_dir:
            os.chdir(script_dir)

        original_argv = sys.argv.copy()
        sys.argv = [self._xfIn.replace('.cy', '')]

        print("Executing decrypted content...")
        try:
            compiled_code = compile(code_str, script_globals['__file__'], 'exec')
            exec(compiled_code, script_globals)
            print("Execution completed successfully.")

        except SyntaxError as e:
            print(f"Syntax error in encrypted script: {e}")
            raise ValueError(f"Invalid Python syntax: {e}")
        except SystemExit as e:
            print(f"Script exited with code: {e.code}")
        except KeyboardInterrupt:
            print("Script execution interrupted by user.")
            raise
        except Exception as e:
            print(f"Runtime error during execution: {e}")
            raise ValueError(f"Script execution failed: {e}")
        finally:
            os.chdir(original_cwd)
            sys.argv = original_argv

            self._xZero(code_str.encode("utf-8"))
            del code_str

            for key in list(script_globals.keys()):
                if key not in ['__name__', '__file__', '__builtins__']:
                    try:
                        del script_globals[key]
                    except:
                        pass

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
        kdf_name = "Argon2" if self._kdf_type == "A" else "PBKDF2"

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
        print(f"Encrypted [{kdf_name}] lines -> '{out_file}'.")
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
        kdf_name = "Argon2" if self._kdf_type == "A" else "PBKDF2"
        self._xWipe()
        print(f"Password changed [{kdf_name}] for '{self._xfIn}'.")
        return self


def printBanner(nome, versione, autore, filler):
    versione_width = len(versione)
    inner_width = max(len(nome) + versione_width, len(f">> {autore}")) + 4
    border = '    ' + filler * (inner_width + 4)
    line2 = f"    {filler}{filler} {nome.ljust(inner_width - versione_width - 2)}{versione.rjust(versione_width - 2)} {filler}{filler}"
    line3 = f"    {filler}{filler} {f">> {autore}".rjust(inner_width - 2)} {filler}{filler}"
    banner = f"\n{border}\n{line2}\n{line3}\n{border}\n"
    print(banner)