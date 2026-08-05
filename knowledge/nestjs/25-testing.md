---
id: nestjs/25-testing
topic: nestjs
slug: testing
title: "NestJS Testing"
type: doc
order: 25
status: ready
tags: [nestjs, testing, createTestingModule, compile, mockResolvedValue, describe, ValidationPipe, NotFoundException]
related: [nestjs/03-dependency-injection, nestjs/05-services, testing/02-unit-testing, testing/03-integration-testing]
when_to_use: "Read before writing or reviewing unit, integration, or end-to-end tests for NestJS code."
---
# NestJS Testing

## Purpose

This document defines the engineering standards for testing NestJS applications.

The objective is to verify correctness, prevent regressions, enable safe refactoring, and provide confidence that the application behaves as expected in production.

Testing is part of software design.

It is not a phase performed after development.

---

## Core Principle

Test behavior.

Not implementation.

Tests should verify what the system does—not how it is implemented internally.

Assert on observable outcomes—return values, thrown exceptions, HTTP status
codes, emitted events—rather than on internal collaborators.

Bad—coupled to implementation. Renaming the private helper or reordering the
internal calls breaks the test even though behavior is unchanged:

```ts
it('creates a user', async () => {
  const spy = jest.spyOn(service as any, 'hashPassword');
  await service.create({ email: 'a@b.com', password: 'secret' });
  // Asserts HOW the method works, not WHAT it produces.
  expect(spy).toHaveBeenCalledTimes(1);
});
```

Good—asserts the observable result and the persisted side effect:

```ts
it('should_persist_a_user_without_leaking_the_raw_password', async () => {
  const created = await service.create({
    email: 'a@b.com',
    password: 'secret',
  });

  expect(created.email).toBe('a@b.com');
  expect(created).not.toHaveProperty('password');
  await expect(service.findById(created.id)).resolves.toMatchObject({
    email: 'a@b.com',
  });
});
```

---

## Goals

A testing strategy should provide:

- confidence;
- fast feedback;
- maintainability;
- reproducibility;
- regression protection;
- production reliability.

A passing test suite should increase confidence—not simply improve coverage metrics.

---

## Testing Pyramid

Prefer the classic Testing Pyramid.

```
            E2E

      Integration

          Unit
```

Most tests should be unit tests.

Integration tests verify collaboration.

End-to-end tests validate complete business flows.

---

## Test Types

## Unit Tests

Test one unit in isolation.

Mock external dependencies.

Verify:

- business logic;
- validation;
- edge cases;
- failure scenarios.

Unit tests should execute quickly.

Build the unit under test with `Test.createTestingModule` and replace its
dependencies with test doubles. For a service that depends on a TypeORM
repository, provide the mock under `getRepositoryToken(Entity)`—the same token
`@InjectRepository` resolves at runtime:

```ts
// users.service.ts (the unit under test)
import { Injectable, NotFoundException } from '@nestjs/common';
import { InjectRepository } from '@nestjs/typeorm';
import { Repository } from 'typeorm';
import { User } from './user.entity';

@Injectable()
export class UsersService {
  constructor(
    @InjectRepository(User)
    private readonly users: Repository<User>,
  ) {}

  async findById(id: string): Promise<User> {
    const user = await this.users.findOne({ where: { id } });
    if (!user) {
      throw new NotFoundException(`User ${id} not found`);
    }
    return user;
  }
}
```

```ts
// users.service.spec.ts
import { Test, TestingModule } from '@nestjs/testing';
import { NotFoundException } from '@nestjs/common';
import { getRepositoryToken } from '@nestjs/typeorm';
import { Repository } from 'typeorm';
import { UsersService } from './users.service';
import { User } from './user.entity';

describe('UsersService', () => {
  let service: UsersService;
  let repository: jest.Mocked<Pick<Repository<User>, 'findOne'>>;

  beforeEach(async () => {
    // Arrange: swap the real repository for a mock double.
    const moduleRef: TestingModule = await Test.createTestingModule({
      providers: [
        UsersService,
        {
          provide: getRepositoryToken(User),
          useValue: { findOne: jest.fn() },
        },
      ],
    }).compile();

    service = moduleRef.get(UsersService);
    repository = moduleRef.get(getRepositoryToken(User));
  });

  it('should_return_user_when_it_exists', async () => {
    const user = { id: '1', email: 'a@b.com' } as User;
    repository.findOne.mockResolvedValue(user);

    const result = await service.findById('1');

    expect(result).toBe(user);
    expect(repository.findOne).toHaveBeenCalledWith({ where: { id: '1' } });
  });

  it('should_throw_not_found_when_user_does_not_exist', async () => {
    repository.findOne.mockResolvedValue(null);

    await expect(service.findById('missing')).rejects.toBeInstanceOf(
      NotFoundException,
    );
  });
});
```

---

## Integration Tests

Verify collaboration between components.

Examples:

- Service + Repository;
- Repository + Database;
- Service + Cache;
- Queue + Worker.

Use real infrastructure whenever practical.

---

## End-to-End Tests

Validate complete user workflows.

Example:

```
HTTP Request

↓

Authentication

↓

Business Logic

↓

Database

↓

Response
```

E2E tests should resemble production behavior.

Boot the real application through `Test.createTestingModule`, apply the same
global configuration used in `main.ts` (pipes, filters, prefixes), and drive it
with `supertest`. Always `close()` the app so the HTTP server and connection
pools are released:

```ts
// test/users.e2e-spec.ts
import { INestApplication, ValidationPipe } from '@nestjs/common';
import { Test } from '@nestjs/testing';
import request from 'supertest';
import { AppModule } from '../src/app.module';

describe('Users (e2e)', () => {
  let app: INestApplication;

  beforeAll(async () => {
    const moduleRef = await Test.createTestingModule({
      imports: [AppModule],
    }).compile();

    app = moduleRef.createNestApplication();
    // Mirror the production bootstrap so the test exercises the real pipeline.
    app.useGlobalPipes(new ValidationPipe({ whitelist: true }));
    await app.init();
  });

  afterAll(async () => {
    await app.close();
  });

  it('should_return_404_when_user_does_not_exist', () => {
    return request(app.getHttpServer())
      .get('/users/does-not-exist')
      .expect(404);
  });

  it('should_reject_invalid_payload_with_400', () => {
    return request(app.getHttpServer())
      .post('/users')
      .send({ email: 'not-an-email' })
      .expect(400);
  });
});
```

---

## Contract Tests

Verify compatibility between communicating systems.

Examples:

- REST APIs;
- gRPC;
- Event Contracts;
- Message Queues.

Contracts reduce integration failures.

---

## Performance Tests

Measure:

- response time;
- throughput;
- concurrency;
- resource consumption.

Performance should be validated—not assumed.

---

## Security Tests

Verify:

- authorization;
- authentication;
- input validation;
- privilege escalation;
- common attack vectors.

Security testing belongs in CI/CD.

---

## Test Doubles

Use the correct test double.

## Mock

Verifies interactions.

---

## Stub

Returns predefined values.

---

## Spy

Observes behavior while preserving implementation.

---

## Fake

Provides a lightweight working implementation.

Choose the simplest double that satisfies the test.

---

## Test Independence

Every test should:

- run independently;
- produce identical results;
- avoid shared mutable state.

Tests should execute in any order.

---

## Determinism

Avoid dependence on:

- system time;
- network availability;
- random values;
- execution order.

Deterministic tests build confidence.

---

## Test Data

Generate only the data required for each scenario.

Prefer builders or factories.

Avoid large fixture files.

---

## Database Testing

Prefer isolated databases.

Use:

- disposable databases;
- transactions with rollback;
- Testcontainers when practical.

Avoid shared development databases.

---

## External Dependencies

Mock external services unless integration is explicitly under test.

Examples:

- payment gateways;
- email providers;
- cloud storage;
- third-party APIs.

In an integration or E2E test that boots the whole module, replace only the
external collaborator with `overrideProvider(...).useValue(...)`. Everything
else runs for real, so the test still exercises routing, guards, pipes, and
persistence:

```ts
// test/checkout.e2e-spec.ts
import { PaymentGateway } from '../src/payments/payment.gateway';

const paymentGatewayMock = {
  charge: jest.fn().mockResolvedValue({ status: 'paid', id: 'ch_123' }),
};

const moduleRef = await Test.createTestingModule({
  imports: [AppModule],
})
  .overrideProvider(PaymentGateway)
  .useValue(paymentGatewayMock)
  .compile();
```

---

## Snapshot Testing

Use snapshots only for stable output.

Avoid snapshots for:

- business logic;
- dynamic values;
- complex objects.

Snapshots should remain readable.

---

## Property-Based Testing

Useful when validating:

- parsers;
- validators;
- algorithms;
- mathematical logic.

Test properties rather than individual examples.

---

## Mutation Testing

Measure test quality.

Mutation testing verifies whether tests detect intentional defects.

Coverage alone does not guarantee correctness.

---

## Code Coverage

Coverage is a metric.

Not a goal.

Prefer meaningful assertions over high percentages.

A lower-quality suite with 100% coverage is worse than a smaller suite with excellent behavioral verification.

---

## Flaky Tests

Flaky tests must be fixed immediately.

Typical causes:

- race conditions;
- timing assumptions;
- shared state;
- network dependency.

Never ignore flaky tests.

---

## Naming

Test names should describe behavior.

Good:

```
should_return_404_when_user_does_not_exist
```

Bad:

```
test1
```

Names should communicate intent.

---

## Arrange, Act, Assert

Prefer the AAA structure.

```
Arrange

↓

Act

↓

Assert
```

Keep these sections visually distinct.

---

## Error Scenarios

Every critical feature should test:

- valid input;
- invalid input;
- boundary conditions;
- exceptions;
- authorization failures;
- concurrency when applicable.

---

## Continuous Integration

Tests should execute automatically.

CI should block deployment when critical tests fail.

Testing should be part of every pull request.

---

## Performance

Test suites should remain fast.

Review:

- duplicate setup;
- unnecessary E2E tests;
- expensive fixtures.

Slow test suites discourage execution.

---

## AI Test Generation

AI should generate tests that:

- verify observable behavior;
- include edge cases;
- include failure scenarios;
- avoid implementation coupling;
- remain readable.

AI should never generate assertions solely to increase coverage.

---

## AI Decision Matrix

Use Unit Tests for:

✓ Business rules

✓ Validation

✓ Algorithms

✓ Domain logic

Use Integration Tests for:

✓ Database

✓ Cache

✓ Repository

✓ Queue

Use E2E Tests for:

✓ User workflows

✓ Authentication

✓ API behavior

✓ Cross-module interactions

---

## AI Execution Checklist

## Investigation

☐ Identify business behaviors.

☐ Identify edge cases.

☐ Identify failure scenarios.

☐ Review external dependencies.

---

## Planning

☐ Select appropriate test type.

☐ Keep tests independent.

☐ Mock external systems.

☐ Verify observable behavior.

---

## Verification

☐ Tests deterministic.

☐ No shared mutable state.

☐ Edge cases covered.

☐ Failure paths tested.

☐ Test names descriptive.

☐ CI compatible.

---

## Examples

**Good Example** — the unit test isolates the rule; the integration test uses a real database

```ts
describe('OrdersService', () => {
  let service: OrdersService;
  const inventory = { reserve: jest.fn() };
  const orders = { create: jest.fn() };

  beforeEach(async () => {
    const moduleRef = await Test.createTestingModule({
      providers: [
        OrdersService,
        { provide: InventoryService, useValue: inventory },
        { provide: OrdersRepository, useValue: orders },
        { provide: EventEmitter2, useValue: { emit: jest.fn() } },
      ],
    }).compile();

    service = moduleRef.get(OrdersService);
  });

  it('rejects the order when stock is unavailable', async () => {
    inventory.reserve.mockResolvedValue({ ok: false, missingSku: 'SKU-1' });

    // Asserts the rule and the reason — not which methods were called in what order.
    await expect(service.place({ userId: 'u1', items: [] })).rejects.toBeInstanceOf(OutOfStockError);
    expect(orders.create).not.toHaveBeenCalled();
  });
});
```

```ts
// The integration test exercises the real wiring against a real database.
describe('POST /orders (integration)', () => {
  let app: INestApplication;
  let container: StartedPostgreSqlContainer;

  beforeAll(async () => {
    container = await new PostgreSqlContainer().start();
    process.env.DATABASE_URL = container.getConnectionUri();

    const moduleRef = await Test.createTestingModule({ imports: [AppModule] }).compile();
    app = moduleRef.createNestApplication();
    app.useGlobalPipes(new ValidationPipe({ whitelist: true }));   // same config as production
    await app.init();
  });

  afterAll(async () => {
    await app.close();
    await container.stop();
  });

  it('rejects a body with unknown fields', async () => {
    await request(app.getHttpServer())
      .post('/orders')
      .send({ sku: 'SKU-1', quantity: 1, isAdmin: true })
      .expect(400);
  });
});
```

**Bad Example** — everything mocked, nothing asserted

```ts
describe('OrdersService', () => {
  it('places an order', async () => {
    // The service under test is mocked too, so this asserts that jest works.
    const service = { place: jest.fn().mockResolvedValue({ id: '1' }) };
    const result = await service.place({});
    expect(result).toBeDefined();
  });

  it('calls the repository', async () => {
    await service.place({ userId: 'u1', items: [] });

    // Asserts the implementation: extracting a private method or reordering two
    // calls breaks the test although the behaviour is identical.
    expect(repo.create).toHaveBeenCalledBefore(events.emit);
    expect(repo.create).toHaveBeenCalledTimes(1);
  });
});
```

---

## Common Mistakes

Avoid:

Testing implementation details.

Mocking everything.

Ignoring integration tests.

Using production databases.

Overusing snapshots.

Writing assertions only for coverage.

Keeping flaky tests.

Sharing state between tests.

---

## Completion Criteria

A testing strategy is complete when:

- business behavior is verified;
- test types are appropriately balanced;
- tests are deterministic;
- external dependencies are isolated where appropriate;
- CI executes the test suite automatically;
- developers can refactor with confidence.

---

## Summary

Testing provides confidence that software behaves correctly under expected and unexpected conditions.

By emphasizing behavioral verification, maintaining a balanced testing strategy, writing deterministic and independent tests, and treating testing as an integral part of software design, engineering teams can deliver reliable, maintainable, and production-ready NestJS applications.

## Related

- `knowledge/nestjs/03-dependency-injection.md`
- `knowledge/nestjs/05-services.md`
- `knowledge/testing/02-unit-testing.md`
- `knowledge/testing/03-integration-testing.md`
