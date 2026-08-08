# Clash on Linux: Proxy Dead While macOS Clash Verge Works — Findings

## Symptom

- macOS Clash Verge with the remote subscription works fine.
- Same subscription on a Linux box (Ubuntu 18.04, `alphaboi`): proxy dead.
  - `curl -x http://127.0.0.1:7890 http://www.gstatic.com/generate_204` → `502 Bad Gateway`
  - All node latency tests fail (`Timeout` / `i/o timeout`)
  - Only DIRECT works (90ms), everything proxied fails

## Root Cause Chain

1. **Wrong core on Linux**: box ran original `clash v1.9.0` (dreamacro, 2021, EOL).
   - No ShadowsocksR support at all (config has many SSR nodes).
   - Parses modern subscription configs partially → nodes register but can't dial.
   - macOS Verge bundles **mihomo (Clash Meta)** — parses the same config fully.
2. **Stale baked-in config on Linux**: providers reported `vehicleType: Compatible`
   (nodes inline in `config.yaml`, **no subscription URL inside**) → config never
   self-refreshes; nodes rotate/expire and dead ones linger.
3. **wget download ≠ what Verge actually runs**: plain `wget` fetch of the
   subscription yields a different (wrong) config — 275KB file with only 1
   `server:` line is a broken/gated download. Verge fetches with its own
   User-Agent and **reloads/renders the profile** (profile chain: remote +
   merge/script/rules/proxies/groups). Only the Verge-processed profile is correct.
4. Node server unavailability is not a box-specific problem: a dead node
   (`78gb1.cdn.node.a.corelink8.net:20434 → dial tcp 206.109.71.134:20434: i/o timeout`)
   was also unreachable from the Mac (`nc` timed out). Verge works because it
   auto-picks other live nodes from the pool and re-tests periodically.

## The Fix

1. **Swap core to mihomo (Clash Meta)** on Linux — same engine family as Verge:

   ```bash
   # old Ubuntu → use the "compatible" build
   ver="v1.19.18"
   wget https://github.com/MetaCubeX/mihomo/releases/download/$ver/mihomo-linux-amd64-compatible-$ver.gz
   gunzip mihomo-linux-amd64-compatible-$ver.gz && chmod +x mihomo-linux-amd64-compatible-$ver
   mv mihomo-linux-amd64-compatible-$ver ~/clash/mihomo
   ```

   **Version pinning**: run `v1.19.18` — the exact mihomo version Clash Verge
   bundles, so the box behaves identically to the known-good macOS setup.
   The latest release (e.g. `v1.19.29`) can be downloaded and kept around, but
   don't run it until the box is stable — patch-level parity removes variables
   when debugging. Bump by editing `ver=` in the snippet above, then restart.

2. **Use the correct config — copy Verge's active profile** (see next section), or
   re-download with a clash User-Agent:

   ```bash
   wget -U "clash-verge" -O config.yaml "<subscription-url>"
   ```

3. **Restart mihomo** (it does NOT auto-reload on file change):

   ```bash
   pkill -15 mihomo; sleep 1; ~/clash/mihomo -d ~/clash/ &
   ```

4. **Verify**:

   ```bash
   curl -x http://127.0.0.1:7890 --max-time 10 -o /dev/null -s -w '%{http_code}\n' http://www.gstatic.com/generate_204   # expect 204
   ./clash-cli -command Doctor -host localhost:9990          # tests all nodes, auto-selects fastest
   ```

5. **Self-healing** (like Verge): point GLOBAL at an auto-URLTest group so clash
   re-tests and switches nodes itself:

   ```bash
   ./clash-cli -command SelectProxy -proxy-group GLOBAL -proxy-name "HK-自动选择" -host localhost:9990
   ```

## macOS Clash Verge: Data Locations

- **App data dir**: `~/Library/Application Support/cashrev/`
  (note: NOT `clash-verge` — easy to miss)
- **Profiles**: `~/Library/Application Support/cashrev/profiles/`
- **Active profile**: `~/Library/Application Support/cashrev/profiles/<profile-uid>.yaml`
  (the remote subscription profile, ~270KB).
  The uid is **not** stable/fixed per user — resolve it from the index file:
- **Profile index**: `~/Library/Application Support/cashrev/profiles.yaml`
  - `current: <uid>` → which profile is active
  - each item has `type` (remote/merge/script/rules/proxies/groups), `name`,
    `file`, and for remote profiles the subscription `url:` (token included),
    usage (`upload`/`download`/`total`), and `expire` timestamp
- Verge applies a **profile chain** (remote + merge + script + rules + proxies +
  groups) — the rendered result is what actually runs; the raw downloaded file
  is not necessarily what Verge executes.

Copy the active profile to the box:

```bash
scp ~/Library/Application\ Support/cashrev/profiles/<profile-uid>.yaml alphaboi@alphaboi:~/clash/config.yaml
```

## Linux Box Diagnosis Commands

```bash
./clash-cli -command Status  -host localhost:9990   # core version + meta/original + ports
./clash-cli -command Test    -host localhost:9990 -proxy-group GLOBAL   # latency all nodes (with failure reasons)
./clash-cli -command Select  -host localhost:9990 -proxy-group GLOBAL   # auto-pick fastest reachable
./clash-cli -command Doctor  -host localhost:9990   # everything + subscription check + auto-select

# node server reachability (isolates network vs clash)
nc -vz -w 5 <server> <port>                          # from box
nc -vz -w 5 <server> <port>                          # from Mac — compare

# config sanity
grep -cE '^\s+- name:' config.yaml                   # expect 100+ nodes
grep -c 'server:' config.yaml                        # expect many; 275KB/1 line = broken download
```

## Gotchas

- `wget` (default UA) often gets a **wrong/gated response** from subscription
  servers — use a clash UA or copy Verge's rendered profile instead.
- **Original clash (dreamacro) is EOL and lacks SSR support** — anything older
  than mihomo will not handle modern subscription configs.
- Configs with `vehicleType: Compatible` providers are **inline snapshots** —
  no subscription URL inside, they can never update themselves; re-copy on a
  schedule or keep using Verge-style live profiles.
- **mihomo does not watch config.yaml** — replace config then restart the
  process (or SIGHUP).
- Latency test URL matters: `https://www.google.com/` is blocked in CN —
  use `http://www.gstatic.com/generate_204` (default in clash-cli) or override
  with `-delay-url`.
