from typing import Optional

from base58 import b58decode_check, b58encode_check


def normalize_evm_address(evm_address: str) -> str:
    """Normalize EVM address format.

    Args:
        evm_address: EVM address with or without '0x' prefix

    Returns:
        str: Normalized EVM address (lowercase, without '0x' prefix)

    Raises:
        ValueError: If the address format is invalid
    """
    if not isinstance(evm_address, str):
        raise ValueError("Address must be a string")

    if not evm_address or evm_address.isspace():
        raise ValueError("Empty address")

    # Remove 0x prefix, spaces and convert to lowercase
    norm_address = evm_address.lower().replace("0x", "").strip()

    # First check if it's a valid hex string
    try:
        int(norm_address, 16)
    except ValueError:
        raise ValueError("Invalid hex characters in EVM address")

    # Then check the length
    if len(norm_address) != 40:
        raise ValueError(
            f"Invalid EVM address length: {len(norm_address)}, expected 40"
        )

    return norm_address


def validate_tron_base58_address(address: str) -> bool:
    """Validate address in Base58Check format.

    Args:
        address: Address in Base58Check format

    Returns:
        bool: True if the address is valid, False otherwise
    """
    if not isinstance(address, str):
        return False

    if not address.startswith("T"):
        return False

    try:
        decoded = b58decode_check(address)
        return len(decoded) == 21 and decoded[0] == 0x41
    except Exception:
        return False


def validate_tron_hex_address(address: str) -> bool:
    """Validate address in hex format with specific prefix.

    Args:
        address: Address in hex format

    Returns:
        bool: True if the address is valid, False otherwise
    """
    if not isinstance(address, str):
        return False

    # Remove 0x prefix and spaces
    norm_address = address.lower().replace("0x", "").strip()

    if not norm_address.startswith("41"):
        return False

    if len(norm_address) != 42:
        return False

    try:
        int(norm_address, 16)
        return True
    except ValueError:
        return False


def evm_to_tron(evm_address: str, output_format: str = "base58") -> str:
    """Convert EVM address to alternative format.

    Args:
        evm_address: EVM address with or without '0x' prefix
        output_format: Output format, either 'base58' or 'hex'

    Returns:
        str: Address in specified format

    Raises:
        ValueError: If the address format is invalid or output_format is invalid
    """
    if output_format not in ["base58", "hex"]:
        raise ValueError("output_format must be 'base58' or 'hex'")

    # Normalize EVM address
    evm_address = normalize_evm_address(evm_address)

    # Add specific prefix
    tron_hex = "41" + evm_address

    if output_format == "hex":
        return tron_hex

    # Convert to Base58Check format
    try:
        address_bytes = bytes.fromhex(tron_hex)
        base58check = b58encode_check(address_bytes)
        return base58check.decode()
    except Exception as e:
        raise ValueError(f"Failed to convert to Base58Check format: {str(e)}")


def tron_to_evm(tron_address: str, add_prefix: bool = True) -> str:
    """Convert address from alternative format to EVM format.

    Args:
        tron_address: Address in Base58Check format or hex format
        add_prefix: Whether to add '0x' prefix to the result

    Returns:
        str: EVM address (with or without '0x' prefix)

    Raises:
        ValueError: If the address format is invalid
    """
    if not isinstance(tron_address, str):
        raise ValueError("Address must be a string")

    if not tron_address or tron_address.isspace():
        raise ValueError("Empty address")

    # Handle Base58Check format
    if tron_address.startswith("T"):
        if not validate_tron_base58_address(tron_address):
            raise ValueError("Invalid Base58Check address")

        try:
            address_bytes = b58decode_check(tron_address)
            tron_hex = address_bytes.hex()
        except Exception as e:
            raise ValueError(f"Failed to decode Base58Check address: {str(e)}")
    else:
        # Handle Hex format
        if not validate_tron_hex_address(tron_address):
            raise ValueError("Invalid hex address")

        tron_hex = tron_address.lower().replace("0x", "").strip()

    # Remove prefix
    evm_address = tron_hex[2:]

    return f"0x{evm_address}" if add_prefix else evm_address


def get_address_type(address: str) -> Optional[str]:
    """Detect address type.

    Args:
        address: Address to detect

    Returns:
        Optional[str]: Address type ('evm', 'tron_base58', 'tron_hex', or None if invalid)
    """
    if not isinstance(address, str):
        return None

    address = address.strip()
    if not address:
        return None

    try:
        # Remove 0x prefix for consistent checking
        norm_address = address.lower().replace("0x", "").strip()

        # Check if it's a hex address with specific prefix
        if norm_address.startswith("41") and len(norm_address) == 42:
            if validate_tron_hex_address(norm_address):
                return "tron_hex"

        # Check if it's a Base58Check address
        if validate_tron_base58_address(address):
            return "tron_base58"

        # Check if it's an EVM address (with or without 0x prefix)
        if len(norm_address) == 40:
            normalize_evm_address(address)
            return "evm"

    except ValueError:
        pass

    return None


# Test cases
if __name__ == "__main__":
    test_cases = [
        "0x123456789abcdef123456789abcdef123456789a",  # Standard EVM address
        "123456789ABCDEF123456789ABCDEF123456789A",  # Uppercase EVM address without prefix
        "TJCnKsPa7y5okkXvQAidZBzqx3QyQ6sxMW",  # Base58Check address
        "4154fdaf1515acfd32744cc33935817ff4d383e31f",  # Hex format address
        "0x4154fdaf1515acfd32744cc33935817ff4d383e31f",  # Hex format with 0x prefix
        "invalid_address",  # Invalid address
        "",  # Empty address
    ]

    print("Testing address type detection and conversions:")
    for addr in test_cases:
        print(f"\nTesting address: {addr}")
        try:
            addr_type = get_address_type(addr)
            print(f"Address type: {addr_type}")

            if addr_type in ["evm"]:
                tron_base58 = evm_to_tron(addr, "base58")
                tron_hex = evm_to_tron(addr, "hex")
                print(f"EVM -> Base58: {tron_base58}")
                print(f"EVM -> Hex: {tron_hex}")

                # Verify reverse conversion
                evm_back = tron_to_evm(tron_base58)
                print(f"Base58 -> EVM: {evm_back}")

            elif addr_type in ["tron_base58", "tron_hex"]:
                evm = tron_to_evm(addr)
                print(f"Alt -> EVM: {evm}")

                # Verify reverse conversion
                tron_back = evm_to_tron(evm)
                print(f"EVM -> Alt: {tron_back}")

        except ValueError as e:
            print(f"Error: {str(e)}")
