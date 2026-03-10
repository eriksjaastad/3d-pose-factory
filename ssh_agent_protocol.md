# SSH Agent Protocol

This document describes the protocol for interacting with the SSH agent within the 3D Pose Factory infrastructure. The agent allows you to execute commands on remote hosts via SSH in a controlled and auditable manner.

The SSH agent reads command requests from `${PROJECTS_ROOT}/_tools/ssh_agent/queue/requests.jsonl` and writes results to `${PROJECTS_ROOT}/_tools/ssh_agent/queue/results.jsonl`.  These files are newline-delimited JSON (JSONL) files.

## Key Concepts

*   **Request Queue:**  `${PROJECTS_ROOT}/_tools/ssh_agent/queue/requests.jsonl` -  A file where you submit commands to be executed by the agent. Each line represents a single command request.
*   **Results Queue:** `${PROJECTS_ROOT}/_tools/ssh_agent/queue/results.jsonl` - A file where the agent writes the results of the executed commands. Each line represents the result of a single command execution.
*   **Host Alias:** A short name defined in `ssh_hosts.yaml` that represents a specific remote host.  This allows you to refer to hosts without needing to specify full SSH connection details.
*   **Idempotency:**  The system does *not* guarantee idempotency. If a request is submitted multiple times, it will be executed multiple times.  It is the responsibility of the user to ensure that commands are only submitted when needed.

## How to Request a Command

1.  **Format your request as a JSON object.**  Each request must conform to the schema described below.
2.  **Append the JSON object as a single line to the `requests.jsonl` file.**  Use a tool like `jq` or a simple script to append the JSON to the file.

### Request Schema

Each JSON object in the `requests.jsonl` file MUST have the following structure:

```json
{
  "id": "<unique-id-string>",
  "host": "<host-alias from ssh_hosts.yaml>",
  "command": "<shell command>",
  "reason": "<short explanation of why you're running this>"
}
```

*   **`id` (string, required):** A unique identifier for the request.  This ID is used to correlate the request with its result.  A good practice is to include a timestamp and a descriptive name in the ID (e.g., `"2025-11-24T15-03-00Z__docker_ps"`).  This field should be unique across all requests.
*   **`host` (string, required):** The host alias, as defined in the `ssh_hosts.yaml` file, on which the command should be executed.
*   **`command` (string, required):** The shell command to execute on the remote host.
*   **`reason` (string, required):** A brief explanation of why you are running the command. This is important for auditing and debugging purposes.

### Example Request

```json
{
  "id": "2025-11-24T15-03-00Z__docker_ps",
  "host": "runpod",
  "command": "cd /srv/pose-factory && docker compose ps",
  "reason": "Check status of containers for debugging"
}
```

## How to Read Results

The agent appends JSON lines to `${PROJECTS_ROOT}/_tools/ssh_agent/queue/results.jsonl` after executing each command.  The results are structured as follows:

### Result Schema

```json
{
  "id": "<same id as request>",
  "host": "<host alias>",
  "command": "<command actually run>",
  "stdout": "<stdout string>",
  "stderr": "<stderr string>",
  "exit_status": <int>,
  "ts": "<ISO8601 timestamp>"
}
```

*   **`id` (string):** The same ID as the corresponding request.
*   **`host` (string):** The host alias on which the command was executed.
*   **`command` (string):** The exact command that was executed (may differ slightly from the requested command due to shell interpretation).
*   **`stdout` (string):** The standard output of the command.
*   **`stderr` (string):** The standard error of the command.
*   **`exit_status` (integer):** The exit status of the command.  `0` typically indicates success.
*   **`ts` (string):** An ISO8601 timestamp indicating when the command was executed.

### Retrieving Results

To retrieve the output of a command you requested, scan the `results.jsonl` file for the entry with a matching `id`.  It is recommended to read the file from the end to find the most recent entry.

Example using `jq`:

```bash
jq -c --arg id "your-request-id" 'select(.id == $id)' "${PROJECTS_ROOT}/_tools/ssh_agent/queue/results.jsonl"
```

## Safety Rules and Best Practices

*   **Prefer read-only commands:**  Use commands like `status`, `logs`, `df -h`, etc., whenever possible.
*   **Avoid destructive commands:** Only run destructive commands (e.g., `rm`, `docker rm`) if the user explicitly requests them and understands the consequences.
*   **Summarize large outputs:** Do not paste huge raw logs in full.  Instead, summarize the relevant information or provide a snippet.
*   **Be mindful of resource usage:** Avoid running commands that consume excessive CPU, memory, or disk I/O on the remote hosts.
*   **Use appropriate error handling:**  Check the `exit_status` and `stderr` fields to ensure that commands executed successfully.
*   **Document your reasons:**  Provide clear and concise reasons for running commands in the `reason` field.  This helps with auditing and debugging.
*   **Rate Limiting:** Be aware that excessive requests may be rate limited to prevent abuse and ensure system stability.

## Related Documentation

*   `ssh_hosts.yaml` - Configuration file containing the host aliases and SSH connection details.  (This file is not directly documented here, but is a critical part of the system.)
