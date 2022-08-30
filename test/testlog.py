import Remilia
Logger=Remilia.LiteLog.LiteLog(__name__)
Logger.info("info")
Logger.warn("warn")
Logger.error("error")
Logger.debug("debug")

@Logger.debughere(["stdout"])
def testdebug():
    Logger.debug("func debug")
    
testdebug()

print=Logger.stdout
print("stdout")