import subprocess
# import os

def shell(cmd):
    """Возвращает функцию, выполняющую команду в терминале (асинхронно).

    :cmd - команда;
    """
    return subprocess.getoutput(cmd)

#def shell(cmd):
#    """Возвращает функцию, выполняющую команду в терминале.
#
#    :cmd - команда;
#    """
#    return os.popen(cmd).read()