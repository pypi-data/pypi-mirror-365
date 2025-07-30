def is_windows():
    import platform
    return platform.system() == "Windows"

def is_linux():
    import platform
    return platform.system() == "Linux"

def is_macos():
    import platform
    return platform.system() == "Darwin"