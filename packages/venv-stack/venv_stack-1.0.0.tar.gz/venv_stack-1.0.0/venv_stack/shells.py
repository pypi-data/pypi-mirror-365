
# needed in order for the activate command to work properly. 
# If you are using a different shell, you may need to adjust the candidates accordingly.
shells = {
    "bash": {
        "flags": lambda tmp_profile_path: ["--rcfile", f"{tmp_profile_path}", "-i"],
        "rc": [".bashrc", ".bash_profile", ".profile"]
    },
    "zsh": {
        "env": lambda tmp_profile_path: f"ZDOTDIR={tmp_profile_path.parent}",
        "flags": ["-i"],
        "rc": [".zshrc", ".zprofile"]
    },
}