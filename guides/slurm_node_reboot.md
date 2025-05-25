# SLURM Node Reset Guide

## When to Use This Guide
- Node has extremely high load average (>50)
- Stuck/unkillable processes consuming 100% CPU
- Node is slow and unresponsive
- System appears hung or unstable

## Step-by-Step Reset Process

### Step 1: Assess the Problem
```bash
# Check node status in SLURM
scontrol show node <nodename>

# Check system load and processes
ssh <nodename> "top -bn1 | head -20"
ssh <nodename> "uptime"
ssh <nodename> "free -h"
```

### Step 2: Drain the Node
```bash
# Prevent new jobs from being scheduled
sudo scontrol update NodeName=<nodename> State=DRAIN Reason="Node reset required"
```

### Step 3: Attempt Process Cleanup (Optional)
```bash
# Try to kill problematic processes
ssh <nodename> "kill -9 <PID>"

# Restart SLURM daemon
ssh <nodename> "systemctl restart slurmd"
```

### Step 4: Check if Issues Persist
```bash
# Check load again
ssh <nodename> "uptime"

# If load is still high (>20) or processes are unkillable, proceed to reboot
```

### Step 5: Reboot the Node
```bash
# Reboot the problematic node
ssh <nodename> "reboot"
```

### Step 6: Monitor Boot Process
```bash
# Check if node responds to ping
ping <nodename>

# Monitor SSH availability (wait 5-15 minutes)
watch -n 10 'ssh -o ConnectTimeout=5 <nodename> "uptime" 2>/dev/null || echo "Still booting..."'
```

### Step 7: Verify Node Health
Once SSH is available:
```bash
# Check system health
ssh <nodename> "uptime && free -h"
ssh <nodename> "top -bn1 | head -10"

# Verify no stuck processes and load is normal (<10)
```

### Step 8: Resume the Node
```bash
# Check current SLURM status
scontrol show node <nodename> | grep State

# Resume the node for job scheduling
sudo scontrol update NodeName=<nodename> State=RESUME

# Verify it's back in service
scontrol show node <nodename> | grep State
sinfo -N | grep <nodename>
```

## Troubleshooting

### If Node Won't Boot (No SSH after 20+ minutes)
- Check ping response: `ping <nodename>`
- If ping fails: Node needs physical/IPMI intervention
- If ping works but no SSH: Wait longer or check console access

### If Resume Fails
```bash
# Try explicitly setting to IDLE first
sudo scontrol update NodeName=<nodename> State=IDLE

# Then try resume again
sudo scontrol update NodeName=<nodename> State=RESUME
```

### Emergency Marking Node as Down
```bash
# If node is completely unresponsive
sudo scontrol update NodeName=<nodename> State=DOWN Reason="Requires physical intervention"
```

## Success Indicators
- ✅ Load average under 10
- ✅ SSH responsive
- ✅ No stuck processes consuming 100% CPU
- ✅ SLURM state shows IDLE/MIXED/ALLOCATED
- ✅ Node accepts job scheduling

## Timeline Expectations
- **Drain**: Immediate
- **Reboot**: 1-2 minutes
- **Boot process**: 5-15 minutes (depending on NFS mounts)
- **Resume**: Immediate once healthy

## Safety Notes
- Always drain before rebooting
- Wait for boot completion before resuming
- Monitor node for a few minutes after resume
- Document any recurring issues for hardware investigation
