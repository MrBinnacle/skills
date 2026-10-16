/**
 * The packet chain (opt-in): each packet records `previous_packet_id`, the id of the newest packet
 * in the store when it was closed. Two packets naming the same parent are two heads; both are kept
 * and reported, never refused.
 */
import { extract, SCAFFOLD_MARKER } from "./packet";
import type { StoredPacket } from "./repo";

async function manifestOf(packet: StoredPacket): Promise<Record<string, unknown> | undefined> {
  try {
    return extract(await packet.read());
  } catch {
    return undefined;
  }
}

/**
 * The id of the newest stored packet that was filled, parses and carries one; null when there is
 * none. A scaffold still carrying its marker was abandoned before the fill, so it is no parent.
 */
export async function latestPacketId(packets: readonly StoredPacket[]): Promise<string | null> {
  for (const packet of packets) {
    let id: unknown;
    try {
      const text = await packet.read();
      if (text.includes(SCAFFOLD_MARKER)) continue;
      id = extract(text).packet_id;
    } catch {
      continue;
    }
    if (typeof id === "string" && id) return id;
  }
  return null;
}

/** One note per parent that more than one stored packet follows. */
export async function chainNotes(packets: readonly StoredPacket[]): Promise<string[]> {
  const children = new Map<string, string[]>();
  for (const packet of packets) {
    const manifest = await manifestOf(packet);
    const parent = manifest?.previous_packet_id;
    const id = manifest?.packet_id;
    if (typeof parent !== "string" || !parent || typeof id !== "string") continue;
    children.set(parent, [...(children.get(parent) ?? []), id]);
  }
  return [...children]
    .filter(([, ids]) => ids.length > 1)
    .map(([parent, ids]) => `two heads: packets ${[...ids].sort().join(" and ")} both follow ${parent}; both are kept`);
}
