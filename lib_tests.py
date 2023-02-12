from Remilia import lite
#LiteLog
Logger=lite.LiteLog.Logger(__name__,factory=lite.LiteLog.DefaultStyle.default_LogStyle1)
Logger.setlevel(lite.LiteLog.LOGLEVEL_DEBUG)
Logger.info("Import Lib Successfully")
Logger.debug("Open Debug Successfully")
Logger.recorder.exportCateLog("info","test.log")
#LiteResource
testfile=lite.LiteResource.File("test.log")
Logger.debug("[File] test.log <Status>")
Logger.debug("exist",testfile.isexist)
Logger.debug("size",testfile.Attrs.filesize)
Logger.debug("unlink file ...")
testfile.unlink()
Logger.debug("unlink successfully")
Logger.addPrintType("success")
Logger.success("CONGRATULATIONS! TEST FINISH SUCCESSFULLY!")