---
id: examples/01-rest-endpoint
topic: examples
slug: rest-endpoint
title: "Example — REST Endpoint"
type: doc
order: 1
status: ready
tags: [examples, rest-endpoint]
related: [examples/02-react-component, workflows/07-add-api-endpoint, rest-api/09-error-handling, nestjs/04-controllers, testing/12-api-testing]
when_to_use: "Read when implementing a REST endpoint end to end — contract, validation, service, errors, and tests."
---
# Example — REST Endpoint

## The Feature

`POST /api/v1/events/:id/signups` — register the current user for an event. Fails when the
event is full, already started, or the user is already registered.

The process that produces this is [Workflow — Add an API Endpoint](../workflows/07-add-api-endpoint.md);
this is what the result looks like.

---

## 1. The Contract, First

```text
POST /api/v1/events/{eventId}/signups
Authorization: Bearer <token>

Request:
  { "notes": "string, optional, max 500 chars" }

Responses:
  201 { "id": 4471, "eventId": 12, "status": "confirmed", "createdAt": "..." }
  400 validation failed
  401 not authenticated
  403 event not open to this user
  404 event does not exist
  409 already registered  |  event full  |  event already started
  429 rate limited
```

Deciding the codes before writing the handler is what keeps them consistent: `409` for
"the request is valid but the state does not allow it", `403` for "you may not", `404` for
"there is nothing here". Getting this wrong is what forces clients to parse error strings.

---

## 2. Validation at the Boundary

```ts
// signups.dto.ts
import { IsOptional, IsString, MaxLength } from 'class-validator';

export class CreateSignupDto {
  @IsOptional()
  @IsString()
  @MaxLength(500, { message: 'notes must be 500 characters or fewer' })
  readonly notes?: string;
}
```

The service below assumes `notes` is a string of a bounded length. Validating here is what
makes that assumption safe — the handler is the only place untrusted input enters.

---

## 3. Business Logic, Separate from HTTP

```ts
// signups.service.ts
export class EventFullError extends Error {}
export class AlreadyRegisteredError extends Error {}
export class EventStartedError extends Error {}

export class SignupsService {
  constructor(private readonly db: Database) {}

  async register(eventId: number, userId: number, notes?: string): Promise<Signup> {
    // One transaction: the capacity check and the insert must not be separated,
    // or two concurrent requests both see space and both succeed.
    return this.db.transaction(async (tx) => {
      const event = await tx.events.findByIdForUpdate(eventId);
      if (!event) throw new NotFoundError('event');

      if (event.startsAt <= new Date()) throw new EventStartedError();

      const existing = await tx.signups.findOne({ eventId, userId });
      if (existing) throw new AlreadyRegisteredError();

      const taken = await tx.signups.countConfirmed(eventId);
      if (taken >= event.capacity) throw new EventFullError();

      return tx.signups.insert({ eventId, userId, notes, status: 'confirmed' });
    });
  }
}
```

The domain errors are the interesting part: the service knows *what* went wrong, the
controller decides *which status code* says so. That split is what lets the same service
back a REST endpoint, a CLI command, and a background job.

`findByIdForUpdate` takes a row lock. Without it, the capacity check is a race — see
[Databases — Concurrency](../databases/10-concurrency.md).

---

## 4. The Controller: Thin

```ts
// signups.controller.ts
@Controller('api/v1/events/:eventId/signups')
export class SignupsController {
  constructor(private readonly signups: SignupsService) {}

  @Post()
  @UseGuards(AuthGuard, ThrottlerGuard)   // 401 and 429 handled before this runs
  @HttpCode(201)
  async create(
    @Param('eventId', ParseIntPipe) eventId: number,
    @Body() dto: CreateSignupDto,
    @CurrentUser() user: User,
  ): Promise<SignupResponse> {
    try {
      const signup = await this.signups.register(eventId, user.id, dto.notes);
      return SignupResponse.from(signup);
    } catch (error) {
      // Translate domain errors into the contract above. The service never
      // imports an HTTP type; the controller never contains business rules.
      if (error instanceof NotFoundError) throw new NotFoundException('Event not found');
      if (error instanceof AlreadyRegisteredError) throw new ConflictException('Already registered');
      if (error instanceof EventFullError) throw new ConflictException('Event is full');
      if (error instanceof EventStartedError) throw new ConflictException('Event has started');
      throw error;   // anything unrecognized becomes a 500 — and gets logged
    }
  }
}
```

Rethrowing the unrecognized case matters: swallowing it would turn an unexpected bug into a
misleading 409.

---

## 5. The Response Shape

```ts
// signup.response.ts — an explicit boundary, not the database row
export class SignupResponse {
  id!: number;
  eventId!: number;
  status!: 'confirmed' | 'waitlisted';
  createdAt!: string;

  static from(signup: Signup): SignupResponse {
    // Fields are listed explicitly so a new database column never leaks into the API
    // by accident. Returning the entity directly is how internal notes and soft-delete
    // flags end up in public responses.
    return {
      id: signup.id,
      eventId: signup.eventId,
      status: signup.status,
      createdAt: signup.createdAt.toISOString(),
    };
  }
}
```

---

## 6. Tests

```ts
// signups.service.spec.ts — the rules, tested without HTTP
describe('SignupsService.register', () => {
  it('rejects a second signup from the same user', async () => {
    await service.register(event.id, user.id);
    await expect(service.register(event.id, user.id)).rejects.toThrow(AlreadyRegisteredError);
  });

  it('rejects when the event is at capacity', async () => {
    const event = await createEvent({ capacity: 1 });
    await service.register(event.id, userA.id);
    await expect(service.register(event.id, userB.id)).rejects.toThrow(EventFullError);
  });

  it('does not exceed capacity under concurrent requests', async () => {
    const event = await createEvent({ capacity: 1 });

    // The race the transaction exists to prevent. Without the row lock this
    // passes intermittently, which is worse than failing.
    const results = await Promise.allSettled([
      service.register(event.id, userA.id),
      service.register(event.id, userB.id),
    ]);

    expect(results.filter((r) => r.status === 'fulfilled')).toHaveLength(1);
  });
});
```

```ts
// signups.e2e-spec.ts — the contract, tested over HTTP
describe('POST /api/v1/events/:id/signups', () => {
  it('returns 201 with the signup', async () => {
    const res = await request(app.getHttpServer())
      .post(`/api/v1/events/${event.id}/signups`)
      .set('Authorization', `Bearer ${token}`)
      .send({ notes: 'Dietary: vegetarian' })
      .expect(201);

    expect(res.body).toMatchObject({ eventId: event.id, status: 'confirmed' });
    expect(res.body).not.toHaveProperty('userId');   // not in the contract
  });

  it('returns 401 without a token', () =>
    request(app.getHttpServer()).post(`/api/v1/events/${event.id}/signups`).expect(401));

  it('returns 409 when already registered', async () => {
    await request(app.getHttpServer()).post(url).set(auth).expect(201);
    await request(app.getHttpServer()).post(url).set(auth).expect(409);
  });

  it('returns 400 when notes exceed the limit', () =>
    request(app.getHttpServer())
      .post(url).set(auth)
      .send({ notes: 'x'.repeat(501) })
      .expect(400));
});
```

The two levels answer different questions. The service tests cover the rules and the race;
the e2e tests cover the contract — status codes, auth, and what the response does *not*
contain.

---

## What a Real Implementation Adds

Deliberately omitted here, and needed in production:

- **Idempotency** — an `Idempotency-Key` header so a client retry does not double-register.
- **Waitlisting** — the `waitlisted` status exists in the response type but is never set.
- **Notification** — confirmation email, dispatched as a job rather than inline.
- **Observability** — structured logs with a request ID, and a metric on the full/conflict rate.
- **OpenAPI** — the contract in section 1, generated from the code rather than kept beside it.

---

## Examples

**Good Example** — the failure paths are as designed as the happy one

```ts
// Each failure is distinguishable, so a client can act on it.
export async function POST(request: NextRequest, { params }: RouteContext) {
  const session = await auth();
  if (!session) return problem(401, 'not_authenticated');

  const { eventId } = await params;
  const parsed = CreateSignup.safeParse(await request.json().catch(() => null));
  if (!parsed.success) return problem(400, 'validation_failed', z.treeifyError(parsed.error));

  const result = await signups.register(eventId, session.userId, parsed.data);

  switch (result.error) {
    case 'NOT_FOUND':          return problem(404, 'event_not_found');
    case 'NOT_OPEN':           return problem(403, 'event_not_open');
    case 'ALREADY_REGISTERED': return problem(409, 'already_registered');
    case 'EVENT_FULL':         return problem(409, 'event_full');
  }

  return Response.json({ id: result.id, status: 'confirmed' }, { status: 201 });
}
```

**Bad Example** — one success shape and one catch-all failure

```ts
export async function POST(request: Request) {
  try {
    const body = await request.json();
    const id = await signup(body.eventId, body.userId);
    return Response.json({ ok: true, id });
  } catch (e) {
    // "Event full" and "database unreachable" are the same response, so the
    // client either retries both — hammering a full event — or neither.
    return Response.json({ ok: false, message: String(e) }, { status: 500 });
  }
}
```

`userId` taken from the body also means any caller can register any user. The endpoint works
in the demo and is a defect in production.

---

## Related

- `knowledge/examples/02-react-component.md`
- `knowledge/workflows/07-add-api-endpoint.md`
- `knowledge/rest-api/09-error-handling.md`
- `knowledge/nestjs/04-controllers.md`
- `knowledge/testing/12-api-testing.md`
