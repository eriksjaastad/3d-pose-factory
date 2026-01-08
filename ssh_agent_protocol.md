# SSH Agent Protocol

You have access to an SSH Agent that reads commands from `/Users/eriksjaastad/projects/_tools/ssh_agent/queue/requests.jsonl`
and writes results to `/Users/eriksjaastad/projects/_tools/ssh_agent/queue/results.jsonl`.

## How to request a command

- Append **one JSON object per line** to `/Users/eriksjaastad/projects/_tools/ssh_agent/queue/requests.jsonl`.
- Each object MUST have this shape:

{
  "id": "<unique-id-string>",
  "host": "<host-alias from ssh_hosts.yaml>",
  "command": "<shell command>",
  "reason": "<short explanation of why you're running this>"
}

Example:

{
  "id": "2025-11-24T15-03-00Z__docker_ps",
  "host": "runpod",
  "command": "cd /srv/pose-factory && docker compose ps",
  "reason": "Check status of containers for debugging"
}

## How to read results

- The agent appends JSON lines to `/Users/eriksjaastad/projects/_tools/ssh_agent/queue/results.jsonl` with this shape:

{
  "id": "<same id as request>",
  "host": "<host alias>",
  "command": "<command actually run>",
  "stdout": "<stdout string>",
  "stderr": "<stderr string>",
  "exit_status": <int>,
  "ts": "<ISO8601 timestamp>"
}

- When you need the output of a command you requested, scan `/Users/eriksjaastad/projects/_tools/ssh_agent/queue/results.jsonl`
  for the latest entry with the matching `id`.

## Safety rules

- Prefer read-only commands (status, logs, df -h, etc.).
- Only run destructive commands (rm, docker rm, etc.) if the user explicitly asks.
- Summarize large outputs; do not paste huge raw logs in full.
