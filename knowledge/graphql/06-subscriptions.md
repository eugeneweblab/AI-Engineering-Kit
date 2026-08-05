---
id: graphql/06-subscriptions
topic: graphql
slug: subscriptions
title: "GraphQL Subscriptions"
type: doc
order: 6
status: ready
tags: [graphql, subscriptions, GraphQLError, mutation, postMessage, publish, onConnect, resolve]
related: [graphql/05-mutations, graphql/07-resolvers, graphql/08-context, graphql/17-security, graphql/22-performance]
when_to_use: "Read before adding or reviewing any real-time GraphQL feature that pushes server events to clients over a subscription."
---
# GraphQL Subscriptions

## Purpose

This document defines how to design, implement, and operate GraphQL **subscriptions**:
long-lived operations that push a stream of results to a client as events occur on the
server. It is written so an agent can add real-time behaviour without leaking events,
exhausting connections, or shipping an unscalable design.

A subscription is the third GraphQL operation type, alongside
[queries](04-queries.md) and [mutations](05-mutations.md). Unlike those, it does not
resolve once — it returns an async stream that emits until the client or server closes it.

## Why It Matters

Subscriptions are the only stateful, long-lived part of a GraphQL server. A query lives
for milliseconds; a subscription can live for hours, holding an open socket, a database
listener, and per-connection memory the whole time. Mistakes here do not fail loudly —
they leak: an unauthorized user keeps receiving another tenant's events, a forgotten
`return` leaves a socket open forever, or an unbounded broadcast turns one write into a
million fan-out messages. The cost surfaces as memory growth and event leaks in
production, not as a red test in CI. Treat every subscription as a resource you must
explicitly acquire, authorize, and release.

## Core Principles

- **Use subscriptions only for genuine server-initiated events.** If the client controls
  when it wants data, use polling or a query. Subscriptions are for state you cannot
  predict (a chat message, a price tick), not for "refresh on demand".
- **Authorize on connect *and* on every event.** Access can be revoked mid-stream; a
  permission checked only at subscribe time becomes a leak the moment the user is removed.
- **Filter server-side, never client-side.** The server must decide who receives an
  event. Sending everything and letting the client ignore it leaks data and wastes fan-out.
- **Every stream must be cancellable and bounded.** On disconnect, tear down the DB
  listener, timer, or iterator. Leaked resources are the default failure mode.
- **Publish from the write path, not the read path.** A mutation that changes state is
  responsible for publishing the event; resolvers should not poll to synthesize events.

## Best Practices

- Prefer the modern `graphql-ws` protocol over the deprecated
  `subscriptions-transport-ws`; the latter is unmaintained and has known auth gaps.
- Authenticate during the WebSocket handshake (`onConnect`) and store identity in the
  subscription [context](08-context.md); re-check authorization inside the resolver's
  `filter`/`resolve` for each event.
- Back the PubSub with a shared broker (Redis, NATS, Kafka) in any multi-instance
  deployment. In-memory PubSub only delivers to clients on the same process.
- Keep subscription payloads small — send an id and changed fields, let the client
  fetch details via a query. Large payloads multiplied by fan-out is how you melt a node.
- Cap concurrent subscriptions per user/connection and apply the same
  [depth/complexity limits](17-security.md) you apply to queries.
- Send periodic keep-alive pings and enforce idle timeouts so dead sockets are reaped.
- Make subscription resolvers idempotent-friendly: clients reconnect and may re-request
  recent state, so design events to tolerate replay and out-of-order delivery.

## Examples

**Good Example** — authorized, server-side filtered, cleaned up

```ts
// Publish from the mutation (write path), keyed so we can filter fan-out.
async function postMessage(_, { roomId, text }, ctx) {
  const msg = await db.messages.insert({ roomId, text, userId: ctx.user.id });
  await pubsub.publish(`MESSAGE_ADDED.${roomId}`, { messageAdded: msg }); // scoped topic
  return msg;
}

const resolvers = {
  Subscription: {
    messageAdded: {
      // Subscribe only to the one room's topic — not a firehose we filter later.
      subscribe: (_, { roomId }, ctx) => {
        if (!ctx.user) throw new GraphQLError("Unauthenticated");
        // Re-check membership on connect; revoked users must not attach.
        if (!ctx.canReadRoom(roomId)) throw new GraphQLError("Forbidden");
        return pubsub.asyncIterator(`MESSAGE_ADDED.${roomId}`);
      },
      // Re-authorize per event: access may have been revoked mid-stream.
      resolve: (payload, _args, ctx) =>
        ctx.canReadRoom(payload.messageAdded.roomId) ? payload.messageAdded : null,
    },
  },
};
```

**Bad Example** — global firehose, auth only at connect, no filtering

```ts
const resolvers = {
  Subscription: {
    messageAdded: {
      // One global topic: every client wakes for every room's messages.
      subscribe: () => pubsub.asyncIterator("MESSAGE_ADDED"),
      // No resolve/filter: a client subscribed to room A receives room B's messages.
      // No auth here at all, and no per-event re-check → cross-tenant leak.
    },
  },
};
// In-memory pubsub → only clients on this exact node ever receive events.
```

## Common Mistakes

- Authorizing at connect time only, so revoked users keep receiving events.
- Using a global topic and filtering on the client — every event fans out to everyone.
- Running in-memory PubSub across multiple instances; clients on other nodes get nothing.
- Never tearing down DB listeners/iterators on disconnect, leaking sockets and memory.
- Putting heavy business logic or large payloads in the event, multiplied by fan-out.
- Using subscriptions where the client could just poll — added state for no real-time need.
- Still shipping `subscriptions-transport-ws` instead of `graphql-ws`.

## Production Tips

- Export metrics for active subscriptions, events published, and fan-out per topic; alert
  on unbounded growth (a leak) or a fan-out spike (a hot topic).
- Load-test reconnection storms: when a node restarts, every client reconnects at once.
  Ensure the handshake auth path can absorb the burst.
- Set an absolute max connection lifetime and require clients to reconnect; this bounds
  the blast radius of a stuck stream and forces periodic re-authorization.

## AI Review Checklist

- Is this genuinely server-initiated, or should it be a query/poll instead?
- Is the user authenticated at connect and re-authorized on every emitted event?
- Is filtering done server-side via scoped topics, never on the client?
- Does the stream tear down its DB listener/iterator on disconnect?
- Is PubSub backed by a shared broker for multi-instance deployments?
- Are payloads small, with depth/complexity and per-user connection limits enforced?
- Is the transport `graphql-ws`, not the deprecated `subscriptions-transport-ws`?

## Related

- `knowledge/graphql/05-mutations.md`
- `knowledge/graphql/07-resolvers.md`
- `knowledge/graphql/08-context.md`
- `knowledge/graphql/17-security.md`
- `knowledge/graphql/22-performance.md`
