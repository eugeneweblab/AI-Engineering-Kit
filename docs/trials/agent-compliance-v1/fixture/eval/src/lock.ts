import type { RedisClientType } from "redis";

export async function withLock<T>(redis: RedisClientType, key: string, work: () => Promise<T>): Promise<T> {
  const acquired = await redis.set(key, "locked", { NX: true, PX: 30_000 });
  if (!acquired) throw new Error("lock busy");
  try {
    return await work();
  } finally {
    await redis.del(key);
  }
}
