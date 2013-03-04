import copy, glob, os, platform, re, socket, sys, threading, wx
import wx.lib.mixins.listctrl  as  listmix

platform = platform.system()
print platform+" Directory Mode"

gnames = []
gfiles = []
gselct = []
	
class SaveLoadOps():
	def InitList(self):
		global gnames, gfiles, gselct
		try:
			lst = open("ns-img.lst",'r')
			for line in lst:
				if line is not '':
					files = []
					dsct = re.findall(r"[^,{}\n;]+", line)
					state = dsct[0][0]
					name = dsct[0][1:]
					for entry in dsct[1:]:
						files.append(entry)
					gnames.append(name)
					gfiles.append(files)
					gselct.append(state)
		except:
			print "ns-img.lst does not exist or is unreadable."
			
	def ResetList(self):
		global gnames, gfiles, gselct
		gnames = []
		gfiles = []
		gselct = []
		self.InitList()
		
	def SaveList(self):
		lst = open("ns-img.lst",'w')
		for i in range(len(gnames)):
			line = gselct[i]+gnames[i]+"{"+','.join(gfiles[i])+"}\n"
			lst.write(line)
		lst.close()
	
class EditableListCtrl(wx.ListCtrl, listmix.TextEditMixin):
    def __init__(self, parent, ID=wx.ID_ANY, pos=wx.DefaultPosition,
                 size=wx.DefaultSize, style=0):
        """Constructor"""
        wx.ListCtrl.__init__(self, parent, ID, pos, size, style)
        listmix.TextEditMixin.__init__(self)
	
class GUI(wx.Frame):
	def __init__(self, parent):
		wx.Frame.__init__(self, parent)
		self._parent = parent
		self.gnames = copy.copy(gnames)
		self.gfiles = copy.copy(gfiles)
		self.gal = ''
		self.MPanel = wx.Panel(self)
		self.InitUI()
		
	def InitUI(self):
		self.GalPanel = wx.Panel(self.MPanel)
		self.GalList = wx.ListBox(self.GalPanel, choices=gnames)
		self.GalList.Bind(wx.EVT_LISTBOX, self.OnSelectGal)
		self.GalText = wx.TextCtrl(self.GalPanel)
		self.GalEntr = wx.Button(self.GalPanel, label="Add")
		self.GalEntr.Bind(wx.EVT_BUTTON, lambda evt: self.OnAddGal(evt, self.GalText.GetValue()))
		self.GalRemv = wx.Button(self.GalPanel, label="Remove")
		self.GalRemv.Bind(wx.EVT_BUTTON, lambda evt: self.OnRemoveGal(evt, self.GalList.GetSelection()))
		self.FilPanel = wx.Panel(self.MPanel)
		self.FilList = EditableListCtrl(self.FilPanel, style=wx.LC_REPORT|wx.BORDER_SUNKEN)
		self.FilList.InsertColumn(0, 'Name', width=250)
		self.FilEntr = wx.Button(self.FilPanel, label="Add")
		self.FilEntr.Bind(wx.EVT_BUTTON, self.OnAddFile)
		self.FilUpdt = wx.Button(self.FilPanel, label="Update Listing")
		self.FilUpdt.Bind(wx.EVT_BUTTON, self.UpdateFiles)
		self.FilRemv = wx.Button(self.FilPanel, label="Remove")
		self.FilRemv.Bind(wx.EVT_BUTTON, self.OnRemoveFile)
		self.SelPanel = wx.Panel(self.MPanel)
#		self.SelText = wx.StaticText(self.SelPanel, pos=((1070, 10)), size=((200, 20)), label="Enable/Disable Galleries")
		self.SelList = wx.ListBox(self.SelPanel, choices=gnames, style=wx.LB_EXTENDED)
		self.SelCmmt = wx.Button(self.SelPanel, label="Commit")
		self.SelCmmt.Bind(wx.EVT_BUTTON, self.OnCommit)
		self.SelCmmt.SetBackgroundColour((127,255,127))
		self.SelUpdt = wx.Button(self.SelPanel, label="Update Selections")
		self.SelUpdt.Bind(wx.EVT_BUTTON, self.OnCommitSelections)
		self.SelExit = wx.Button(self.SelPanel, label="Exit Editor")
		self.SelExit.Bind(wx.EVT_BUTTON, self.OnClose)
		
		self.MainBox = wx.BoxSizer(wx.HORIZONTAL)
		self.GalBox = wx.BoxSizer(wx.VERTICAL)
		self.FilBox = wx.BoxSizer(wx.VERTICAL)
		self.SelBox = wx.BoxSizer(wx.VERTICAL)
		
		self.GalBox.Add(self.GalRemv, 1, wx.EXPAND)
		self.GalBox.Add(self.GalList, 21, wx.EXPAND)
		self.GalBox.Add(self.GalText, 1, wx.EXPAND)
		self.GalBox.Add(self.GalEntr, 1, wx.EXPAND)
		
		self.FilBox.Add(self.FilRemv, 1, wx.EXPAND)
		self.FilBox.Add(self.FilList, 21, wx.EXPAND)
		self.FilBox.Add(self.FilEntr, 1, wx.EXPAND)
		self.FilBox.Add(self.FilUpdt, 1, wx.EXPAND)
		
		self.SelBox.Add(self.SelList, 21, wx.EXPAND)
		self.SelBox.Add(self.SelCmmt, 1, wx.EXPAND)
		self.SelBox.Add(self.SelUpdt, 1, wx.EXPAND)
		self.SelBox.Add(self.SelExit, 1, wx.EXPAND)
		
		self.MainBox.Add(self.GalPanel, 1, wx.EXPAND)
		self.MainBox.Add(self.FilPanel, 3, wx.EXPAND)
		self.MainBox.Add(self.SelPanel, 1, wx.EXPAND)
		
		self.GalPanel.SetSizer(self.GalBox)
		self.FilPanel.SetSizer(self.FilBox)
		self.SelPanel.SetSizer(self.SelBox)
		self.MPanel.SetSizer(self.MainBox)
		
		for i in range(len(gselct)):
			if gselct[i] == 'e':
				self.SelList.Select(i)
	
		self.SetSize((800, 600))
		self.SetMinSize((800, 600))
		self.SetTitle("NetSlideshow Server Configuration")
		self.Centre()
		self.Show()

	def OnAddGal(self, evt, txt, files=[]):
		self.GalList.Append(txt)
		self.gnames.append(txt)
		self.gfiles.append([])
		self.SelList.Set(self.gnames)
		self.SelCmmt.SetBackgroundColour((255,127,127))
		
	def OnRemoveGal(self, evt, index):
		self.GalList.Delete(index)
		self.gnames.pop(index)
		self.gfiles.pop(index)
		self.SelList.Set(self.gnames)
		self.SelCmmt.SetBackgroundColour((255,127,127))
		
	def OnAddFile(self, evt):
		sel = self.FilList.GetFirstSelected()
		if sel > -1:
			self.FilList.InsertStringItem(sel, '')
		else:
			self.FilList.Append([''])
		
	def OnRemoveFile(self, evt):
		deletion = []
		for i in xrange(self.FilList.GetItemCount()):
			if self.FilList.IsSelected(i):
				deletion.append(i)
		for i in reversed(deletion):
				self.FilList.DeleteItem(i)
		
	def OnSelectGal(self, evt):
		self.FilList.DeleteAllItems()
		self.gal = self.GalList.GetSelection()
		for i in range(len(self.gfiles[self.gal])):
			self.FilList.Append([self.gfiles[self.gal][i]])
		
	def UpdateFiles(self, evt):
		r = self.FilList.GetItemCount()
		self.gfiles[self.gal] = ['']*r
		for i in range(r):
			self.gfiles[self.gal][i] = self.FilList.GetItemText(i)
		self.SelCmmt.SetBackgroundColour((255,127,127))
		
	def GUIUpdate(self):
		self.GalList.Set(self.gnames)
		self.SelList.Set(self.gnames)
		for i in range(len(gselct)):
			if self.gselct[i] == 'e':
				self.SelList.Select(i)

	def OnCommit(self, evt):
		global gnames, gfiles, gselct
		self.gnames, self.gfiles = (list(l) for l in zip(*sorted(zip(self.gnames, self.gfiles))))
		gnames = self.gnames
		gfiles = self.gfiles
		self.gselct = ['d']*len(gnames)
		for selected in list(self.SelList.GetSelections()):
			self.gselct[selected] = 'e'
		gselct = self.gselct
		self.SelCmmt.SetBackgroundColour((127,255,127))
		self.GUIUpdate()
		
	def OnCommitSelections(self, evt):
		global gselct
		self.gselct = ['d']*len(gnames)
		for selected in list(self.SelList.GetSelections()):
			self.gselct[selected] = 'e'
		gselct = self.gselct
		self.GUIUpdate()
		
	def OnClose(self, evt):
		self.Close()
		

			
class Server(threading.Thread):
	def __init__(self):
		threading.Thread.__init__(self)
		self.types = ('.png', '.jpg', '.gif')
		self.allfiles = []
		self.daemon = True
	def run(self):
		self.getfiles()
		srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		srv.bind((addr, int(port)))
		srv.listen(1)
		while 1:
			try:
				(clsock, claddr) = srv.accept()
				data = clsock.recv(1024)
				print "CONNECTED:    "+str(claddr)
				data2 = "No Fitting Operations"
				if data == "listsize":
					cllist = len(self.allfiles)
					clsock.send(str(cllist))
					reqint = clsock.recv(1024)
					reqfile = self.allfiles[int(reqint)]
					print "INDEX:        "+reqint+"\nNAME:         "+reqfile+"\n"
					clsock.send(str(reqfile))
					if clsock.recv(1024) == "OK":
						image = open(reqfile,'rb')
						sendimage = image.read()
						image.close()
						clsock.send(sendimage)
						clsock.close()
					else:
						clsock.close()
				else:
					clsock.close()
			except:
				print "A Connection Failed"
		srv.close()
		
	def getfiles(self):
		self.allfiles = []
		print "GENERATING LIST..."
		for i in range(len(gnames)):
			if gselct[i] == 'e':
				bmode = ''
				for file in gfiles[i]:
					if file[0] == 'f':
						self.allfiles.append(file[1:])
					elif file[0] == 's':
						path = file[1:]
						for (path, dirs, files) in os.walk(path):
							for f in files:
								for ctype in self.types:
									if f[-4:] == ctype:
										if platform != "Windows":
											self.allfiles.append(path+"/"+f)
										else:
											self.allfiles.append(path+'\\'+f)
					elif file[0] == 'n':
						path = file[1:]
						for ctype in self.types:
							for files in glob.glob(os.path.join(path, '*'+ctype)):
								self.allfiles.append(files)
					elif file[0] == 'b':
						if file[-1:] != "/" and platform != "Windows":
							bmode = file[1:]+'/'
						if file[-1:] != "\\" and platform == "Windows":
							bmode = file[1:]+'\\'
						else:
							bmode = file[1:]
					elif file[0] == 'p':
						self.allfiles.append(bmode+file[1:])
		print str(len(self.allfiles))+" FILES"

app = wx.App()

addr = raw_input("Address [192.168.1.100]: ")
port = raw_input("Port [8808]: ")
if addr == "":
	addr = "192.168.1.100"
if port == "": 
	port = "8808"
	
SLO = SaveLoadOps()
SLO.InitList()
	
srv = Server()
srv.start()
while 1:
	input = raw_input('')
	if input == "help":
		print ">edit:  (e)        Launch the list editor."
		print ">exit:  (quit, q)  Exit the program."
		print ">regen: (r)        Regenerate the server's file list from changes in the editor."
		print ">reset: (rr)       Rescan ng-img.lst for a new list, resetting all unsaved changes made in the editor."
		print ">save:  (s)        Save list to ns-img.lst"
	elif input in ('edit', 'e'):
		interface=GUI(None)
		app.MainLoop()
	elif input in ('regen', 'r'):
		srv.getfiles()
	elif input in ('save', 's'):
		SLO.SaveList()
	elif input in ('reset', 'rr'):
		SLO.ResetList()
	elif input in ('exit', 'quit', 'q'):
		sys.exit(1)
	else:
		print "Unknown Command"
