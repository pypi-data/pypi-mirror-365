import subprocess

task_name = "scheduleperfectmindwebscraper"
script_path = r"C:\Users\Justin Ho\Coding\perfectMind_webscraper\main_scheduled.py"
python_path = r"C:\Users\Justin Ho\AppData\Local\Programs\Python\Python313\python.exe"

# Build the full schtasks command (escaped properly for PowerShell)
schtasks_cmd = (
    f'schtasks /Create /SC DAILY /TN "{task_name}" '
    f'/TR "\\"{python_path}\\" \\"{script_path}\\"" '
    f'/ST 23:30 /RL LIMITED /F'
)

# Wrap it in a PowerShell Start-Process call to elevate
powershell_cmd = [
    "powershell",
    "-Command",
    f"Start-Process cmd -ArgumentList '/c {schtasks_cmd}' -Verb runAs"
]

try:
    subprocess.run(powershell_cmd, check=True)
    print("✅ Task created successfully as admin.")
except subprocess.CalledProcessError as e:
    print("❌ Failed to create task:", e)
