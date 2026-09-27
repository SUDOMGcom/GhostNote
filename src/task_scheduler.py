import subprocess
import sys
from pathlib import Path

TASK_NAME = "GhostNote Capture Prompts"
DAY_NAMES = ("Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday")


def get_launch_command():
    if getattr(sys, "frozen", False):
        return sys.executable, "scheduled"

    main_path = Path(__file__).resolve().parents[1] / "main.py"
    return sys.executable, f'"{main_path}" scheduled'


def update_task(times, work_days=None):
    executable, arguments = get_launch_command()

    trigger_lines = []

    for time in times:
        if work_days is None:
            trigger_lines.append(f"$triggers += New-ScheduledTaskTrigger -Daily -At '{time}'")
        else:
            days = ",".join(f"'{DAY_NAMES[day]}'" for day in work_days)
            trigger_lines.append(f"$triggers += New-ScheduledTaskTrigger -Weekly -DaysOfWeek {days} -At '{time}'")

    triggers = "\n".join(trigger_lines)

    script = f"""
$action = New-ScheduledTaskAction -Execute '{executable}' -Argument '{arguments}'
$triggers = @()
{triggers}

$settings = New-ScheduledTaskSettingsSet -MultipleInstances IgnoreNew -StartWhenAvailable:$false
$settings.DisallowStartIfOnBatteries = $false
$settings.StopIfGoingOnBatteries = $false

Register-ScheduledTask `
    -TaskName '{TASK_NAME}' `
    -Action $action `
    -Trigger $triggers `
    -Settings $settings `
    -Description 'GhostNote Schedule - Task created by the GhostNote app.' `
    -Force | Out-Null
"""

    subprocess.run(
        ["powershell.exe", "-NoProfile", "-NonInteractive", "-Command", script],
        check=True,
        creationflags=subprocess.CREATE_NO_WINDOW,
    )


def remove_task():
    script = f"""
$task = Get-ScheduledTask | Where-Object {{ $_.TaskName -eq '{TASK_NAME}' }}
if ($task) {{
    Unregister-ScheduledTask -TaskName '{TASK_NAME}' -Confirm:$false
}}
"""

    subprocess.run(
        ["powershell.exe", "-NoProfile", "-NonInteractive", "-Command", script],
        check=True,
        creationflags=subprocess.CREATE_NO_WINDOW,
    )
    