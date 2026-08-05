---
id: security/17-encryption
topic: security
slug: encryption
title: "Encryption"
type: doc
order: 17
status: ready
tags: [security, encryption, Math.random, random]
related: [security/16-secrets-management, security/18-https, security/05-password-security, security/01-security-fundamentals]
when_to_use: "Read before encrypting data at rest, hashing values, or choosing any cryptographic algorithm or key length."
---
# Encryption

## Purpose

This document defines how to protect data with cryptography correctly: what to use
for confidentiality (encryption), what to use for integrity/identity (hashing,
MACs, signatures), and — most importantly — how to avoid the subtle misuse that
turns strong primitives into broken systems. The rule that governs everything here
is: use vetted, high-level libraries and standard algorithms; never assemble your
own scheme from primitives.

Encryption protects data at rest and is the foundation under
[secrets management](16-secrets-management.md) and, via TLS,
[HTTPS](18-https.md). Password *hashing* is a distinct topic covered in
[password security](05-password-security.md).

## Why It Matters

Cryptographic bugs are silent and total: the system appears to work, ciphertext
looks random, and yet a reused nonce, an unauthenticated mode, or a hardcoded key
lets an attacker decrypt or forge everything. These mistakes are easy to make and
nearly impossible to spot by looking at output. Because a break exposes all data at
once and cannot be noticed at runtime, crypto is one place where "roll your own" is
never acceptable — correctness comes from using proven constructions exactly as
intended.

## Core Principles

- **Never invent or hand-assemble crypto.** Use a maintained high-level library
  (libsodium/NaCl, `cryptography`, WebCrypto, cloud KMS). Custom schemes and
  primitive-level code fail in ways only experts catch.
- **Authenticated encryption, always.** Use AEAD (AES-GCM, ChaCha20-Poly1305) so
  ciphertext cannot be tampered with undetected. Plain encryption without a MAC is
  malleable.
- **Right tool for the job.** Encryption for confidentiality; a slow KDF for
  passwords; HMAC/signatures for integrity and authenticity; a CSPRNG for tokens.
  Do not substitute one for another.
- **Keys are the hard part.** Security depends on key generation, storage,
  rotation, and separation — not on the algorithm. Manage keys in a KMS/secret store.
- **Randomness must be cryptographic.** Generate keys, nonces, IVs, and tokens from
  a CSPRNG; never reuse a nonce/IV with the same key.

## Best Practices

- Encrypt with AEAD: **AES-256-GCM** or **ChaCha20-Poly1305**. Generate a fresh
  random nonce per message and store it alongside the ciphertext; never reuse a
  nonce under one key (nonce reuse in GCM is catastrophic).
- Delegate key management to a KMS or secret store; encrypt data keys with a master
  key (envelope encryption) and support rotation without re-encrypting everything.
- For integrity without secrecy, use HMAC-SHA-256 or a signature scheme
  (Ed25519). For hashing content identifiers, use SHA-256; never MD5 or SHA-1.
- For passwords, use a memory-hard KDF (Argon2id/bcrypt) — see
  [password security](05-password-security.md). Never encrypt passwords; hash them.
- Compare secrets and MACs with constant-time comparison to avoid timing leaks.
- Use TLS 1.3 for data in transit; do not build application-layer encryption to
  substitute for transport security.
- Plan key rotation from the start: version your keys, store the key id with the
  ciphertext, and keep old keys available for decryption until re-encrypted.

## Examples

**Good Example** — high-level AEAD with a per-message random nonce

```python
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import os

def encrypt(key: bytes, plaintext: bytes, context: bytes) -> bytes:
    aead = AESGCM(key)                 # AES-256-GCM: encrypts AND authenticates
    nonce = os.urandom(12)             # fresh CSPRNG nonce per message; never reused
    # `context` is authenticated-but-not-encrypted associated data (e.g. record id),
    # binding the ciphertext to where it belongs so it can't be swapped elsewhere.
    ct = aead.encrypt(nonce, plaintext, context)
    return nonce + ct                  # store the nonce with the ciphertext
```

**Bad Example** — hand-rolled, unauthenticated, static IV, hardcoded key

```python
from Crypto.Cipher import AES

KEY = b"0123456789abcdef"                  # hardcoded key + 128-bit only
IV = b"0000000000000000"                   # static IV reused for every message

def encrypt(plaintext):
    cipher = AES.new(KEY, AES.MODE_CBC, IV) # CBC has no integrity: ciphertext is malleable
    return cipher.encrypt(pad(plaintext))   # no MAC → padding-oracle & tampering attacks
```

## Common Mistakes

- Using an unauthenticated mode (ECB/CBC without a MAC); ECB also leaks patterns.
- Reusing a nonce/IV with the same key, or using a static/zero IV.
- Hardcoding keys in source, or storing the key next to the ciphertext it protects.
- Using MD5/SHA-1, or using a fast hash (SHA-256) or encryption for passwords.
- Seeding keys/tokens from `random`/`Math.random` instead of a CSPRNG.
- Rolling a custom protocol from primitives instead of using a high-level library.
- No key rotation plan, so a compromised key means re-encrypting everything by hand.

## Production Tips

- Keep keys in a KMS with access logging; rotate on a schedule and on suspected
  compromise, and alert on unusual decrypt volume.
- Store a key id/version with every ciphertext so rotation and re-encryption are
  incremental rather than all-or-nothing.
- Pin algorithm choices in one crypto module the rest of the app calls, so upgrades
  and reviews happen in a single place.

## AI Review Checklist

- Is an AEAD mode (AES-GCM / ChaCha20-Poly1305) used, with a fresh random nonce?
- Are all keys, nonces, and tokens generated from a CSPRNG, never a static value?
- Are keys managed by a KMS/secret store, not hardcoded or stored beside ciphertext?
- Are passwords hashed with Argon2id/bcrypt rather than encrypted or fast-hashed?
- Are MAC/secret comparisons constant-time?
- Is there a key-rotation plan with versioned keys, and no home-grown crypto scheme?

## Related

- `knowledge/security/16-secrets-management.md`
- `knowledge/security/18-https.md`
- `knowledge/security/05-password-security.md`
- `knowledge/security/01-security-fundamentals.md`
