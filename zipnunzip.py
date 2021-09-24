import os
from zipfile import ZipFile
from config import *
import logging as log


log.basicConfig(filename=APP_PATH+"/logs/std.log",encoding="utf-8",level=log.DEBUG,format="%(name)s:%(levelname)s:[%(asctime)s] %(message)s")

def logWrite(state,msg):
    """Write appropriate log  to loghandler."""
    if state=="INFO":
        log.info(msg)
    if state=="DEBUG":
        log.debug(msg)
    if state=="ERROR":
        log.error(msg)
    if state=="WARNING":
        log.warning(msg)

def getFiles(dirs):
    """Return list of files in  passed directory."""
    fp=[]
    for root,directories,files in os.walk(dirs):
        for filename in files:
            filepath=os.path.join(root,filename)
            fp.append(filepath)
    return fp

def archive(name,*dirs):
    """Make archive including files from passed directory."""
    with ZipFile(name+".zip",'w') as backup:
        logWrite("DEBUG","Files to zip:")
        for i in dirs:
            if not os.path.isfile(i):
                files=getFiles(i)
                for path in files:
                    logWrite("DEBUG",path)
                    backup.write(path)
            else:
                logWrite("DEBUG",i)
                backup.write(i)
    logWrite("INFO","Files archived in "+name+".zip")


def extract(archive,clear=False,dst="./"):
    """Extract archive."""
    if clear:
        files=getFiles(dst)
        for i in files:
            os.remove(i)
    with ZipFile(archive,'r') as inp:
        inp.extractall(dst)
    logWrite("INFO","Files extracted to "+dst)