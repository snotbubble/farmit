<xmp class="bcode">
# non-version-locked houdini to deadline7 script. by c.p.brown 2016
###################################################################

import os
import string
import getpass
import time

usr = getpass.getuser()
fail = 0

pathtodeadline = "C:\\Program Files\\Thinkbox\\Deadline8\\bin\\deadlinecommand.exe"
pathtohoudini = "C:\\hfs\\Houdini " + hou.applicationVersionString()
nethfs = "Z:\\hfs\\Houdini " + hou.applicationVersionString()

if not os.path.isdir(nethfs) :
	print("looking for " + nethfs)
	print("your version of houdini isn't in Z:\\hfs\\\nCopy it over 1st...")
	fail = 1

ops = hou.selectedNodes()

if len(ops) <= 0 :
   print('select a rop 1st...')
   fail = 1

for i in ops :
	otn = i.type().name()
	if otn != 'ifd' and otn != 'rop_geometry' and otn != 'rop_dop' and otn != 'geometry' and otn != 'wedge' and otn != 'rop_comp' and otn != 'comp':
		print('wrong node dude...')
		fail = 1

if fail == 0 :
	di = ("C:\\Users\\" + usr + "\\Desktop\\deadline_jobid\\")
	if not os.path.exists(di):
		os.mkdir(di)

	hscene = hou.hipFile.name()
	hname = hou.hipFile.path().split('.')[0].split('/')[-1]
	hdir = hou.hipFile.path().split('.')[0].split('/')[-3]

	deadlinecmd = ""
	xcmd = cmd = ("(xcopy <QUOTE>" + nethfs + "<QUOTE> <QUOTE>" + pathtohoudini + "\\<QUOTE> /d /e /v /c /r /y /h /i)")
	
	for i in ops :
		otn = i.type().name()
		opth = i.path()
		if otn == 'rop_geometry' or otn == 'rop_dop' or otn == 'geometry' or otn == 'wedge' or otn == 'rop_comp' or otn == 'comp' :
			opn = i.name()
			if otn == 'wedge' :
				drv = i.parm('driver').eval()
				wd = hou.node(drv)
				rng = wd.parm('trange').eval()
				if rng == 0 :
					fstart = str(int(hou.frame()))
					fend = fstart
					fdur = "1"
				else :
					fstart = str(int(wd.parm('f1').eval()))
					fend = str(int(wd.parm('f2').eval()))
					fdur = str(int(wd.parm('f2').eval() - (wd.parm('f1').eval()-1)))               
			else :
				rng = i.parm('trange').eval()
				if rng == 0 :
					fstart = str(int(hou.frame()))
					fend = fstart
					fdur = "1"
				else :
					fstart = str(int(i.parm('f1').eval()))
					fend = str(int(i.parm('f2').eval()))
					fdur = str(int(i.parm('f2').eval() - (i.parm('f1').eval()-1)))

			deadlinecmd = "\"" + pathtodeadline + "\" -SubmitCommandLineJob -executable cmd.exe -arguments \"/c " + xcmd + " && <QUOTE>" + pathtohoudini + "\\bin\\hbatch.exe<QUOTE> -c <QUOTE>render " + opth + "<QUOTE> -c  quit <QUOTE>" +  hou.hipFile.path() + "<QUOTE>\" -frames " + fstart + "-" + fend + " -chunksize " + fdur + " -pool \"hbatch\" -priority 60 -name \"" + hname + "_" + opn + " - hbatch\" -initialstatus \"Active\" -prop MachineLimit=1"
		if otn == 'ifd' :
			opn = i.name()
			print('selected node is a mantra ROP : ' + opn)
			fstart = str(int(i.parm('f1').eval()))
			ifdf = i.parm('soho_diskfile').eval()
			ifdp = ifdf.split('.')
			if len(ifdp) > 1 :
				checkp = (ifdp[0] + '.' + fstart + '.' + ifdp[2])
				print('checking ifd 1st frame : ' + checkp + '\n')
				if os.path.isfile(checkp) :
					rng = i.parm('trange').eval()
					ifs = i.parm('soho_diskfile').eval()
					ifa = ifs.split('.')
					ifs = (ifa[0] + '.<STARTFRAME>.' + ifa[2])
					if rng == 0 :
						fstart = str(int(hou.frame()))
						fend = fstart
					else :
						fstart = str(int(i.parm('f1').eval()))
						fend = str(int(i.parm('f2').eval()))
					deadlinecmd = "\"" + pathtodeadline + "\" -SubmitCommandLineJob -executable cmd.exe -arguments \"/c " + xcmd + " && <QUOTE>" + pathtohoudini + "\\bin\\mantra.exe<QUOTE> -V 4a -j 0 -f <QUOTE>" + ifs + "<QUOTE>\" -frames " + fstart + "-" + fend + " -chunksize 1 -priority 60 -name \"" + hname + "_" + opn + "\" -pool \"mantra\"  -initialstatus \"Active\" -prop MachineLimit=15"
				else :
					print('ifds are missing, write them out 1st...')
			else : print('ifd path not set...')
		
		if deadlinecmd != "" :
			print(deadlinecmd)
			j = (di + hname  + "_" + opn + "_RENDER_jobID.txt")
			deadlinecmd = "(" + deadlinecmd + ")>>\"" + j + "\""
			os.system(deadlinecmd)
</xmp>
