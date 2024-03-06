import base64
import binascii
from typing import Optional

# A list of fallback encodings to be used as alternatives when decoding byte streams that fail with UTF-8 encoding.
# These encodings cover a variety of languages and scripts, providing broad compatibility across different regions.
FALLBACK_ENCODINGS: list[str] = [
    # Japanese
    'shift_jis', 'euc-jp',
    # Simplified/Traditional Chinese
    'gbk', 'big5',
    # Cyrillic
    'koi8-r', 'koi8-u',
    # Alternatives for Europe
    'windows-1252', 'iso-8859-2', 'iso-8859-5', 'iso-8859-7', 'iso-8859-9',
]


def decode_data_blob(data_blob: bytes, fallback_encodings: Optional[list[str]] = None):
    """
    Attempts to decode a data blob using UTF-8, then falls back to other specified encodings if UTF-8 decoding fails.
    The decoded string is then encoded back to UTF-8 to ensure compatibility with UTF-8 only systems.

    Parameters:
        data_blob (bytes): The byte sequence to decode.
        fallback_encodings (list of str, optional): A list of encoding names to try if UTF-8 decoding fails.

    Returns:
        str: The UTF-8 encoded string, regardless of the original encoding.

    Raises:
        UnicodeDecodeError: If decoding fails for UTF-8 and all specified fallback encodings.
    """

    decoded_string = None

    if fallback_encodings is None:
        fallback_encodings = FALLBACK_ENCODINGS

    # Try UTF-8 first, then fallback encodings
    for encoding in ['utf-8'] + fallback_encodings:
        try:
            decoded_string = data_blob.decode(encoding)
            break  # Stop on the first successful decoding
        except UnicodeDecodeError:
            continue

    if decoded_string is None:
        raise UnicodeDecodeError("Failed to decode data blob with the provided encodings.")

    # Ensure the output is encoded in UTF-8
    return decoded_string.encode('utf-8').decode('utf-8')


def decode_base64_blob(data_base64: str, fallback_encodings: Optional[list[str]] = None):
    """
    Decodes data from Base64 encoding to binary, then attempts to decode the binary data using UTF-8.
    If UTF-8 decoding fails, it tries the specified fallback encodings in order.
    The final decoded string is ensured to be valid UTF-8.

    Parameters:
        data_base64 (str): The Base64 encoded string to decode.
        fallback_encodings (list of str, optional): A list of encoding names to try if UTF-8 decoding fails.

    Returns:
        str: The decoded string from the original binary data, encoded in UTF-8.

    Raises:
        ValueError: If the input is not correctly Base64-encoded.
        UnicodeDecodeError: If decoding fails for UTF-8 and all specified fallback encodings.
    """

    try:
        data_blob = base64.b64decode(data_base64)
    except binascii.Error as e:
        raise ValueError("Invalid Base64 data") from e

    # Reuse the `decode_data_blob` function to decode the binary data
    return decode_data_blob(data_blob, fallback_encodings)
