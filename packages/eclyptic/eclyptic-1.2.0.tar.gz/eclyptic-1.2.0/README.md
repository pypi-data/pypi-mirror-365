# Eclyptic Asymmetric Encryption

**Version**: 1.2.0
**License**: [LICENSE](https://r2.jts.gg/license)
**Developer**: [jts.gg/eclyptic](https://jts.gg/eclyptic)

---

Eclyptic is a lightweight Python library that implements a streamlined ECIES‑style encryption scheme utilizing:

* **Elliptic‑Curve Diffie‑Hellman (ECDH)** for key agreement
* **HKDF‑SHA256** for symmetric key derivation
* **AES‑GCM** for authenticated encryption
* **Compressed ECC public keys** with compact **Base64 URL-safe encoding** (no padding)

Designed for ease of use, forward secrecy, and efficiency with arbitrary binary and text payloads.

## Installation

```bash
# install from PyPI
pip3 install eclyptic
```

## Quick Start

```python
import eclyptic

# generate a compact base64-encoded keypair
priv, pub = eclyptic.keypair()

# encrypt data (bytes or UTF-8 string)
data = "secret data"
encrypted_data = eclyptic.encrypt(pub, data)

# decrypt back into raw bytes or UTF-8 text
decrypted_bytes = eclyptic.decrypt(priv, encrypted_data)
plaintext = decrypted_bytes.decode('utf-8')
```
