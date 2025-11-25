# SSH Agent for Claude

Simple polling agent that lets Claude run SSH commands on remote hosts.

## Setup (One-Time)

```bash
# Install dependencies
cd ssh_agent
pip install -r requirements.txt

# Start the agent (in a separate terminal or tmux)
python agent.py
```

The agent will keep running, watching for new commands.

## How Claude Uses It

Claude writes JSON commands to `ops_queue/requests.jsonl` and reads results from `ops_queue/results.jsonl`.

See `../ssh_agent_protocol.md` for the full protocol.

## Configuration

Edit `ssh_hosts.yaml` to add hosts. Currently configured:
- **runpod**: Reads POD_ID from `.pod_id` file, connects to `ssh.runpod.io`

## Testing

```bash
# Test a simple command
echo '{"id":"test1","host":"runpod","command":"pwd","reason":"test"}' >> ../ops_queue/requests.jsonl

# Check results
tail -1 ../ops_queue/results.jsonl
```

## Notes

- Agent polls every 1 second for new requests
- Supports both RSA and ED25519 SSH keys
- Auto-expands `~` in key paths
- For RunPod, reads the POD_ID from `../.pod_id` automatically

