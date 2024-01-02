import subprocess

def runcmd(cmd: "list[str]", verbose = False):

    process = subprocess.run(
        cmd,
        capture_output=True,
        check=True,
        text=True,
    )
    if verbose:
        print(std_out.strip(), std_err)

runcmd(["wget", "https://bravenlyglobal.d-solmedia.com/"], verbose = True)