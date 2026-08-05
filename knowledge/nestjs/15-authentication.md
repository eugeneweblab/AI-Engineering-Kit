---
id: nestjs/15-authentication
topic: nestjs
slug: authentication
title: "NestJS Authentication"
type: doc
order: 15
status: ready
tags: [nestjs, authentication]
related: [nestjs/16-authorization, nestjs/09-guards, security/03-authentication, security/07-jwt]
when_to_use: "Read before building or reviewing any login, signup, session, token, or credential-handling code."
---
# NestJS Authentication

## Purpose

This document defines the engineering standards for implementing authentication in NestJS applications.

The objective is to verify user identities securely while keeping authentication independent from authorization and business logic.

Authentication answers one question:

> Who is making this request?

It should not determine what the user is allowed to do.

---

## Core Principle

Authenticate identities.

Do not implement business rules.

Authorization belongs elsewhere.

---

## Authentication Goals

Every authentication system should provide:

- identity verification;
- secure credential handling;
- token lifecycle management;
- session independence;
- auditability;
- scalability.

Authentication should remain transport-independent whenever practical.

---

## Authentication Flow

Typical JWT flow:

```
Login Request

↓

Credential Validation

↓

Identity Verification

↓

Generate Access Token

↓

Generate Refresh Token

↓

Return Tokens

↓

Authenticated Requests

↓

Token Validation

↓

Authenticated User
```

Every stage should have a clearly defined responsibility.

---

## Responsibilities

Authentication is responsible for:

- verifying credentials;
- issuing tokens;
- validating tokens;
- refreshing sessions;
- revoking sessions;
- identifying users.

Authentication should not:

- evaluate permissions;
- enforce business policies;
- determine resource ownership.

---

## Identity Providers

Authentication may use:

- email and password;
- OAuth2;
- OpenID Connect;
- SAML;
- API keys;
- service accounts;
- enterprise identity providers.

Business logic should remain independent of the identity provider.

---

## Password Handling

Passwords should:

- never be stored in plain text;
- always be hashed using a modern password hashing algorithm;
- never be logged;
- never be returned by the API.

Password verification should occur only during authentication.

Use a memory-hard algorithm such as Argon2id (or bcrypt). Never hash
passwords with fast, general-purpose hashes like SHA-256 or MD5 — they are
trivial to brute-force. Wrap hashing in an injectable service so the algorithm
can be swapped without touching callers:

```typescript
// password.service.ts
import { Injectable } from '@nestjs/common';
import * as argon2 from 'argon2';

@Injectable()
export class PasswordService {
  // Argon2id resists both GPU and side-channel attacks.
  private readonly options: argon2.Options = {
    type: argon2.argon2id,
    memoryCost: 19_456, // 19 MiB
    timeCost: 2,
    parallelism: 1,
  };

  hash(plain: string): Promise<string> {
    return argon2.hash(plain, this.options);
  }

  // argon2.verify parses the stored parameters from the encoded hash itself.
  verify(hash: string, plain: string): Promise<boolean> {
    return argon2.verify(hash, plain);
  }
}
```

**Bad Example** — fast hash, no salt, reversible-in-practice:

```typescript
import { createHash } from 'node:crypto';

// A raw SHA-256 digest of a password is NOT a password hash.
// No salt, no work factor, precomputable with rainbow tables.
const stored = createHash('sha256').update(plain).digest('hex');
```

**Good Example** — memory-hard, self-describing, per-hash salt:

```typescript
const stored = await this.passwordService.hash(plain); // "$argon2id$v=19$m=19456,t=2,p=1$..."
const ok = await this.passwordService.verify(stored, plain);
```

---

## Access Tokens

Access tokens should:

- have short lifetimes;
- contain only required claims;
- be cryptographically signed;
- remain stateless.

Avoid storing sensitive information inside tokens.

Validate the login payload with a class-validator DTO (the global
`ValidationPipe` enforces it), verify the credential, then sign a short-lived
access token with `@nestjs/jwt`. Use a constant-time password check and return
an identical error for "unknown user" and "wrong password" so the endpoint does
not disclose which accounts exist:

```typescript
// login.dto.ts
import { IsEmail, IsString, MinLength } from 'class-validator';

export class LoginDto {
  @IsEmail()
  email!: string;

  @IsString()
  @MinLength(8)
  password!: string;
}
```

```typescript
// auth.service.ts
import { Injectable, UnauthorizedException } from '@nestjs/common';
import { JwtService } from '@nestjs/jwt';
import { ConfigService } from '@nestjs/config';
import { PasswordService } from './password.service';
import { UsersService } from '../users/users.service';
import { LoginDto } from './login.dto';

@Injectable()
export class AuthService {
  constructor(
    private readonly users: UsersService,
    private readonly passwords: PasswordService,
    private readonly jwt: JwtService,
    private readonly config: ConfigService,
  ) {}

  async login(dto: LoginDto): Promise<{ accessToken: string }> {
    const user = await this.users.findByEmail(dto.email);

    // Verify even when the user is missing to keep timing uniform,
    // and surface one indistinguishable error for both failure modes.
    const passwordHash = user?.passwordHash ?? '';
    const valid = user
      ? await this.passwords.verify(passwordHash, dto.password)
      : false;

    if (!user || !valid) {
      throw new UnauthorizedException('Invalid credentials');
    }

    const accessToken = await this.jwt.signAsync(
      { sub: user.id, email: user.email }, // minimal claims — no roles/PII
      {
        secret: this.config.getOrThrow<string>('JWT_SECRET'),
        expiresIn: '15m',
        issuer: this.config.getOrThrow<string>('JWT_ISSUER'),
        audience: this.config.getOrThrow<string>('JWT_AUDIENCE'),
      },
    );

    return { accessToken };
  }
}
```

```typescript
// auth.controller.ts
import { Body, Controller, HttpCode, Post } from '@nestjs/common';
import { AuthService } from './auth.service';
import { LoginDto } from './login.dto';

@Controller('auth')
export class AuthController {
  constructor(private readonly auth: AuthService) {}

  @Post('login')
  @HttpCode(200)
  login(@Body() dto: LoginDto) {
    return this.auth.login(dto);
  }
}
```

Register `JwtModule` and `ConfigModule` so the signing dependencies resolve:

```typescript
// auth.module.ts
import { Module } from '@nestjs/common';
import { JwtModule } from '@nestjs/jwt';
import { ConfigModule } from '@nestjs/config';
import { AuthController } from './auth.controller';
import { AuthService } from './auth.service';
import { PasswordService } from './password.service';
import { UsersModule } from '../users/users.module';

@Module({
  imports: [ConfigModule, JwtModule.register({}), UsersModule],
  controllers: [AuthController],
  providers: [AuthService, PasswordService],
  exports: [AuthService],
})
export class AuthModule {}
```

---

## Refresh Tokens

Refresh tokens should:

- have longer lifetimes;
- be stored securely;
- support revocation;
- support rotation.

Refresh tokens should never be treated as permanent credentials.

---

## Token Rotation

Implement refresh token rotation.

Flow:

```
Refresh Token

↓

Validate

↓

Invalidate Previous Token

↓

Issue New Refresh Token

↓

Issue New Access Token
```

Reusing an old refresh token should be treated as a security event.

Store only a hash of each refresh token (never the raw value), issue a new
token on every refresh, and revoke the old one atomically. If a token that was
already rotated is presented again, treat it as theft and revoke the whole
session family:

```typescript
// refresh-token.entity.ts
import {
  Column,
  Entity,
  Index,
  PrimaryGeneratedColumn,
} from 'typeorm';

@Entity('refresh_tokens')
export class RefreshToken {
  @PrimaryGeneratedColumn('uuid')
  id!: string;

  @Index()
  @Column()
  userId!: string;

  // Groups every token derived from one login so a family can be revoked together.
  @Index()
  @Column()
  familyId!: string;

  @Column()
  tokenHash!: string; // argon2 hash of the raw token — never the token itself

  @Column({ default: false })
  revoked!: boolean;

  @Column({ type: 'timestamptz' })
  expiresAt!: Date;
}
```

```typescript
// refresh-token.service.ts
import {
  ForbiddenException,
  Injectable,
  UnauthorizedException,
} from '@nestjs/common';
import { InjectRepository } from '@nestjs/typeorm';
import { Repository } from 'typeorm';
import { randomBytes, randomUUID } from 'node:crypto';
import { PasswordService } from './password.service';
import { RefreshToken } from './refresh-token.entity';

@Injectable()
export class RefreshTokenService {
  constructor(
    @InjectRepository(RefreshToken)
    private readonly repo: Repository<RefreshToken>,
    private readonly hasher: PasswordService,
  ) {}

  async issue(userId: string, familyId = randomUUID()): Promise<string> {
    const raw = randomBytes(32).toString('base64url');
    const entity = this.repo.create({
      userId,
      familyId,
      tokenHash: await this.hasher.hash(raw),
      expiresAt: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000), // 7 days
    });
    await this.repo.save(entity);
    // The caller returns `${entity.id}.${raw}` to the client.
    return `${entity.id}.${raw}`;
  }

  async rotate(presented: string): Promise<string> {
    const [id, raw] = presented.split('.');
    const record = await this.repo.findOne({ where: { id } });

    if (!record || record.expiresAt < new Date()) {
      throw new UnauthorizedException('Invalid refresh token');
    }

    // Reuse of an already-rotated token means the token leaked.
    if (record.revoked) {
      await this.repo.update(
        { familyId: record.familyId },
        { revoked: true },
      );
      throw new ForbiddenException('Refresh token reuse detected');
    }

    if (!(await this.hasher.verify(record.tokenHash, raw))) {
      throw new UnauthorizedException('Invalid refresh token');
    }

    record.revoked = true;
    await this.repo.save(record);
    return this.issue(record.userId, record.familyId);
  }
}
```

---

## Token Revocation

Support revocation for:

- logout;
- password changes;
- compromised accounts;
- administrator actions.

Revoked tokens should no longer grant access.

---

## JWT Claims

Include only necessary claims.

Typical claims:

- subject (user ID);
- issuer;
- audience;
- issued at;
- expiration;
- token identifier.

Avoid embedding authorization rules inside JWTs unless explicitly required.

---

## Session Management

Authentication may remain stateless.

If sessions are required:

- define expiration;
- support revocation;
- monitor active sessions.

Session behavior should remain predictable.

---

## Multi-Factor Authentication

Support MFA when required.

Examples:

- authenticator applications;
- hardware security keys;
- email verification;
- SMS verification (only when appropriate).

MFA should complement—not replace—strong password security.

---

## OAuth Integration

When integrating OAuth:

- validate provider tokens;
- verify issuer;
- verify audience;
- retrieve trusted user information.

Never trust unverified identity data.

---

## API Keys

API keys should:

- identify clients;
- support expiration;
- support rotation;
- support revocation.

Treat API keys as secrets.

---

## Rate Limiting

Authentication endpoints should be protected against abuse.

Examples:

- login attempts;
- password reset;
- token refresh.

Protect against brute-force attacks.

---

## Account Lockout

Repeated authentication failures may trigger:

- temporary lockout;
- progressive delays;
- additional verification.

Avoid permanent lockout without administrative recovery.

---

## Audit Logging

Record security events.

Examples:

- successful login;
- failed login;
- logout;
- password reset;
- token refresh;
- MFA enrollment.

Audit logs should be immutable.

---

## Security

Always verify:

- token signature;
- expiration;
- issuer;
- audience;
- replay protection when applicable.

Never trust client-provided identity information.

---

## Testing

Verify:

- successful authentication;
- failed authentication;
- expired tokens;
- revoked tokens;
- refresh token rotation;
- logout behavior.

Authentication should remain deterministic.

---

## AI Decision Matrix

Authentication is responsible for:

✓ Identity verification

✓ Token issuance

✓ Token validation

✓ Session lifecycle

✓ Credential verification

Authentication is **not** responsible for:

✗ Permission checks

✗ Business rules

✗ Resource ownership

✗ Feature access

---

## AI Execution Checklist

## Investigation

☐ Identify authentication mechanism.

☐ Review token lifecycle.

☐ Review credential storage.

☐ Review security requirements.

---

## Planning

☐ Separate authentication from authorization.

☐ Issue short-lived access tokens.

☐ Rotate refresh tokens.

☐ Protect credentials.

---

## Verification

☐ Passwords securely handled.

☐ Tokens validated.

☐ Revocation supported.

☐ MFA considered.

☐ Security events logged.

☐ Authentication independently testable.

---

## Common Mistakes

Avoid:

Storing plain text passwords.

Using long-lived access tokens.

Returning sensitive user information.

Embedding business permissions inside authentication logic.

Skipping refresh token rotation.

Trusting unsigned JWTs.

Logging credentials or tokens.

---

## Completion Criteria

Authentication is complete when:

- user identities are verified securely;
- passwords are protected;
- access and refresh tokens follow secure lifecycle rules;
- authentication remains separate from authorization;
- revocation and rotation are supported;
- security events are logged.

---

## Summary

Authentication establishes the identity of every request.

By separating identity verification from authorization, protecting credentials, implementing secure token management, and supporting modern authentication workflows, NestJS applications remain secure, scalable, and maintainable.

## Related

- `knowledge/nestjs/16-authorization.md`
- `knowledge/nestjs/09-guards.md`
- `knowledge/security/03-authentication.md`
- `knowledge/security/07-jwt.md`
