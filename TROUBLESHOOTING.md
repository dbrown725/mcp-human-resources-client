# Troubleshooting

## Runaway agent.py Process

If your log files are filling up with repeated errors such as:

```
ERROR - Failed while agent.run: EOF when reading a line
```

This typically indicates a runaway `agent.py` process that has lost its input stream but continues to loop.

### Fix

Run the following command to find and kill the process:

```bash
pkill -f agent.py && echo "Killed" || echo "No processes found"
```

To first verify which processes are running before killing them:

```bash
ps aux | grep agent.py | grep -v grep
```
