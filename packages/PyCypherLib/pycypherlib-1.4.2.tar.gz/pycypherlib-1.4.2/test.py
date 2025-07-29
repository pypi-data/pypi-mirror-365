from PyCypher import Cy
import os


def test_basic_functionality():
    """Test basic encryption/decryption functionality"""
    print("Testing basic functionality...")

    # Test data
    test_password = "TestPassword123"
    test_data = "Hello, this is a test message!"

    # Test Argon2 KDF
    print("  Testing Argon2...")
    cy_a = Cy("A")
    encrypted_data = cy_a.encLines().Lines(test_data).toData().P(test_password)

    # Write to temp file for decryption test
    temp_file = "test_argon2.cy"
    with open(temp_file, "wb") as f:
        f.write(encrypted_data)

    # Decrypt and verify
    decrypted = Cy("A").decLines(temp_file).P(test_password)
    assert decrypted == test_data, f"Argon2 test failed: {decrypted} != {test_data}"
    os.remove(temp_file)
    print("  ✓ Argon2 test passed")

    # Test PBKDF2 KDF
    print("  Testing PBKDF2...")
    cy_p = Cy("P")
    encrypted_data = cy_p.encLines().Lines(test_data).toData().P(test_password)

    temp_file = "test_pbkdf2.cy"
    with open(temp_file, "wb") as f:
        f.write(encrypted_data)

    decrypted = Cy("P").decLines(temp_file).P(test_password)
    assert decrypted == test_data, f"PBKDF2 test failed: {decrypted} != {test_data}"
    os.remove(temp_file)
    print("  ✓ PBKDF2 test passed")


def test_file_operations():
    """Test file encryption/decryption with both KDF types"""
    print("Testing file operations...")

    test_content = "This is test file content\nWith multiple lines\nFor testing purposes"
    test_password = "FileTestPassword123"

    # Test with Argon2
    print("  Testing file operations with Argon2...")
    test_file_a = "test_input_argon2.txt"
    with open(test_file_a, "w") as f:
        f.write(test_content)

    Cy("A").enc(test_file_a).P(test_password)
    encrypted_file_a = test_file_a + ".cy"
    assert os.path.exists(encrypted_file_a), "Argon2 encrypted file not created"

    Cy("A").dec(encrypted_file_a).P(test_password)
    with open(test_file_a, "r") as f:
        decrypted_content_a = f.read()
    assert decrypted_content_a == test_content, "Argon2 file content mismatch"

    os.remove(test_file_a)
    os.remove(encrypted_file_a)
    print("  ✓ Argon2 file operations test passed")

    # Test with PBKDF2
    print("  Testing file operations with PBKDF2...")
    test_file_p = "test_input_pbkdf2.txt"
    with open(test_file_p, "w") as f:
        f.write(test_content)

    Cy("P").enc(test_file_p).P(test_password)
    encrypted_file_p = test_file_p + ".cy"
    assert os.path.exists(encrypted_file_p), "PBKDF2 encrypted file not created"

    Cy("P").dec(encrypted_file_p).P(test_password)
    with open(test_file_p, "r") as f:
        decrypted_content_p = f.read()
    assert decrypted_content_p == test_content, "PBKDF2 file content mismatch"

    os.remove(test_file_p)
    os.remove(encrypted_file_p)
    print("  ✓ PBKDF2 file operations test passed")


def test_lines_operations():
    """Test lines encryption/decryption with both KDF types"""
    print("Testing lines operations...")

    test_password = "LinesTestPassword123"

    # Test single string with both KDF types
    single_line = "Single test line"

    # Argon2
    print("  Testing single line with Argon2...")
    result_a = Cy("A").encLines().Lines(single_line).toData().P(test_password)
    temp_file_a = "test_single_argon2.cy"
    with open(temp_file_a, "wb") as f:
        f.write(result_a)
    decrypted_a = Cy("A").decLines(temp_file_a).P(test_password)
    assert decrypted_a == single_line, f"Argon2 single line test failed: {decrypted_a}"
    os.remove(temp_file_a)
    print("  ✓ Argon2 single line test passed")

    # PBKDF2
    print("  Testing single line with PBKDF2...")
    result_p = Cy("P").encLines().Lines(single_line).toData().P(test_password)
    temp_file_p = "test_single_pbkdf2.cy"
    with open(temp_file_p, "wb") as f:
        f.write(result_p)
    decrypted_p = Cy("P").decLines(temp_file_p).P(test_password)
    assert decrypted_p == single_line, f"PBKDF2 single line test failed: {decrypted_p}"
    os.remove(temp_file_p)
    print("  ✓ PBKDF2 single line test passed")

    # Test multiple lines with both KDF types
    multiple_lines = ["Line 1", "Line 2", "Line 3"]

    # Argon2
    print("  Testing multiple lines with Argon2...")
    result_ma = Cy("A").encLines().Lines(multiple_lines).toData().P(test_password)
    temp_file_ma = "test_multiple_argon2.cy"
    with open(temp_file_ma, "wb") as f:
        f.write(result_ma)
    decrypted_ma = Cy("A").decLines(temp_file_ma).P(test_password)
    assert decrypted_ma == multiple_lines, f"Argon2 multiple lines test failed: {decrypted_ma}"
    os.remove(temp_file_ma)
    print("  ✓ Argon2 multiple lines test passed")

    # PBKDF2
    print("  Testing multiple lines with PBKDF2...")
    result_mp = Cy("P").encLines().Lines(multiple_lines).toData().P(test_password)
    temp_file_mp = "test_multiple_pbkdf2.cy"
    with open(temp_file_mp, "wb") as f:
        f.write(result_mp)
    decrypted_mp = Cy("P").decLines(temp_file_mp).P(test_password)
    assert decrypted_mp == multiple_lines, f"PBKDF2 multiple lines test failed: {decrypted_mp}"
    os.remove(temp_file_mp)
    print("  ✓ PBKDF2 multiple lines test passed")


def test_auto_detection():
    """Test KDF auto-detection"""
    print("Testing KDF auto-detection...")

    test_password = "AutoDetectPassword123"
    test_data = "Auto detection test data"

    # Create files with different KDF types
    argon2_data = Cy("A").encLines().Lines(test_data).toData().P(test_password)
    pbkdf2_data = Cy("P").encLines().Lines(test_data).toData().P(test_password)

    # Save to files
    argon2_file = "test_argon2_auto.cy"
    pbkdf2_file = "test_pbkdf2_auto.cy"

    with open(argon2_file, "wb") as f:
        f.write(argon2_data)
    with open(pbkdf2_file, "wb") as f:
        f.write(pbkdf2_data)

    # Test auto-detection (using default constructor)
    print("  Testing auto-detection of Argon2...")
    decrypted_argon2 = Cy().decLines(argon2_file).P(test_password)
    assert decrypted_argon2 == test_data, "Argon2 auto-detection failed"
    print("  ✓ Argon2 auto-detection test passed")

    print("  Testing auto-detection of PBKDF2...")
    decrypted_pbkdf2 = Cy().decLines(pbkdf2_file).P(test_password)
    assert decrypted_pbkdf2 == test_data, "PBKDF2 auto-detection failed"
    print("  ✓ PBKDF2 auto-detection test passed")

    # Clean up
    os.remove(argon2_file)
    os.remove(pbkdf2_file)


def test_cross_compatibility():
    """Test cross-compatibility between KDF types via auto-detection"""
    print("Testing cross-compatibility...")

    test_password = "CrossCompatPassword123"
    test_data = "Cross compatibility test data"

    # Encrypt with Argon2, decrypt with auto-detection
    print("  Testing Argon2 -> Auto...")
    argon2_data = Cy("A").encLines().Lines(test_data).toData().P(test_password)
    temp_file = "test_cross_argon2.cy"
    with open(temp_file, "wb") as f:
        f.write(argon2_data)

    decrypted = Cy().decLines(temp_file).P(test_password)  # Auto-detection
    assert decrypted == test_data, "Argon2 -> Auto cross-compatibility failed"
    os.remove(temp_file)
    print("  ✓ Argon2 -> Auto test passed")

    # Encrypt with PBKDF2, decrypt with auto-detection
    print("  Testing PBKDF2 -> Auto...")
    pbkdf2_data = Cy("P").encLines().Lines(test_data).toData().P(test_password)
    temp_file = "test_cross_pbkdf2.cy"
    with open(temp_file, "wb") as f:
        f.write(pbkdf2_data)

    decrypted = Cy().decLines(temp_file).P(test_password)  # Auto-detection
    assert decrypted == test_data, "PBKDF2 -> Auto cross-compatibility failed"
    os.remove(temp_file)
    print("  ✓ PBKDF2 -> Auto test passed")


def test_password_change():
    """Test password change functionality with both KDF types"""
    print("Testing password change...")

    old_password = "OldPassword123"
    new_password = "NewPassword456"
    test_data = "Password change test data"

    # Test with Argon2
    print("  Testing password change with Argon2...")
    encrypted_data = Cy("A").encLines().Lines(test_data).toData().P(old_password)
    temp_file_a = "test_pwchange_argon2.cy"
    with open(temp_file_a, "wb") as f:
        f.write(encrypted_data)

    # Change password
    Cy("A").changeP(temp_file_a).newP(new_password).P(old_password)

    # Verify with new password
    decrypted = Cy("A").decLines(temp_file_a).P(new_password)
    assert decrypted == test_data, "Argon2 password change failed"
    os.remove(temp_file_a)
    print("  ✓ Argon2 password change test passed")

    # Test with PBKDF2
    print("  Testing password change with PBKDF2...")
    encrypted_data = Cy("P").encLines().Lines(test_data).toData().P(old_password)
    temp_file_p = "test_pwchange_pbkdf2.cy"
    with open(temp_file_p, "wb") as f:
        f.write(encrypted_data)

    # Change password
    Cy("P").changeP(temp_file_p).newP(new_password).P(old_password)

    # Verify with new password
    decrypted = Cy("P").decLines(temp_file_p).P(new_password)
    assert decrypted == test_data, "PBKDF2 password change failed"
    os.remove(temp_file_p)
    print("  ✓ PBKDF2 password change test passed")


def test_error_handling():
    """Test error handling with both KDF types"""
    print("Testing error handling...")

    test_data = "Error handling test"
    correct_password = "CorrectPassword123"
    wrong_password = "WrongPassword123"

    # Test wrong password with Argon2
    print("  Testing wrong password with Argon2...")
    encrypted_data = Cy("A").encLines().Lines(test_data).toData().P(correct_password)
    temp_file = "test_error_argon2.cy"
    with open(temp_file, "wb") as f:
        f.write(encrypted_data)

    try:
        Cy("A").decLines(temp_file).P(wrong_password)
        assert False, "Should have raised an error for wrong password (Argon2)"
    except ValueError as e:
        assert "Decryption failed" in str(e), f"Unexpected error message (Argon2): {e}"
    os.remove(temp_file)
    print("  ✓ Argon2 error handling test passed")

    # Test wrong password with PBKDF2
    print("  Testing wrong password with PBKDF2...")
    encrypted_data = Cy("P").encLines().Lines(test_data).toData().P(correct_password)
    temp_file = "test_error_pbkdf2.cy"
    with open(temp_file, "wb") as f:
        f.write(encrypted_data)

    try:
        Cy("P").decLines(temp_file).P(wrong_password)
        assert False, "Should have raised an error for wrong password (PBKDF2)"
    except ValueError as e:
        assert "Decryption failed" in str(e), f"Unexpected error message (PBKDF2): {e}"
    os.remove(temp_file)
    print("  ✓ PBKDF2 error handling test passed")


def test_toData_functionality():
    """Test toData() method with both KDF types"""
    print("Testing toData functionality...")

    test_password = "ToDataPassword123"
    test_data = "ToData test message"

    # Test Argon2 toData
    print("  Testing toData with Argon2...")
    encrypted_bytes = Cy("A").encLines().Lines(test_data).toData().P(test_password)
    assert isinstance(encrypted_bytes, bytes), "Argon2 toData should return bytes"

    # Write and decrypt
    temp_file = "test_todata_argon2.cy"
    with open(temp_file, "wb") as f:
        f.write(encrypted_bytes)
    decrypted = Cy("A").decLines(temp_file).P(test_password)
    assert decrypted == test_data, "Argon2 toData decryption failed"
    os.remove(temp_file)
    print("  ✓ Argon2 toData test passed")

    # Test PBKDF2 toData
    print("  Testing toData with PBKDF2...")
    encrypted_bytes = Cy("P").encLines().Lines(test_data).toData().P(test_password)
    assert isinstance(encrypted_bytes, bytes), "PBKDF2 toData should return bytes"

    # Write and decrypt
    temp_file = "test_todata_pbkdf2.cy"
    with open(temp_file, "wb") as f:
        f.write(encrypted_bytes)
    decrypted = Cy("P").decLines(temp_file).P(test_password)
    assert decrypted == test_data, "PBKDF2 toData decryption failed"
    os.remove(temp_file)
    print("  ✓ PBKDF2 toData test passed")


def main():
    """Run all tests"""
    print("Starting PyCypher comprehensive tests...\n")

    try:
        test_basic_functionality()
        test_file_operations()
        test_lines_operations()
        test_auto_detection()
        test_cross_compatibility()
        test_password_change()
        test_error_handling()
        test_toData_functionality()

        print("\nAll tests passed successfully!")
        print("Argon2 KDF functionality verified")
        print("PBKDF2 KDF functionality verified")
        print("Auto-detection working correctly")
        print("Cross-compatibility confirmed")
        print("Error handling working properly")

    except Exception as e:
        print(f"\nTest failed: {e}")
        raise


if __name__ == "__main__":
    main()