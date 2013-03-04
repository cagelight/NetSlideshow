import os, platform, random, shutil, socket, sys, threading, time, wx, wx.animate
import wx.lib.scrolledpanel as wxsp

platform = platform.system()
print platform+" Directory Mode"

myEVT_NEWIMG = wx.NewEventType()
EVT_NEWIMG = wx.PyEventBinder(myEVT_NEWIMG, 1)
myEVT_COUNT = wx.NewEventType()
EVT_COUNT = wx.PyEventBinder(myEVT_COUNT, 1)
myEVT_CONNECTION_ATTEMPT = wx.NewEventType()
EVT_CONNECTION_ATTEMPT = wx.PyEventBinder(myEVT_CONNECTION_ATTEMPT, 1)
myEVT_CONNECTION_FAILURE = wx.NewEventType()
EVT_CONNECTION_FAILURE = wx.PyEventBinder(myEVT_CONNECTION_FAILURE, 1)
myEVT_CONNECTION_SUCCESS = wx.NewEventType()
EVT_CONNECTION_SUCCESS = wx.PyEventBinder(myEVT_CONNECTION_SUCCESS, 1)
currentimage = wx.EmptyImage(800,600)
currint = -1

class NewImageEvent(wx.PyCommandEvent):
	def __init__(self, etype, eid, value=None, index=0, indexmax=0, filename = "None Specified", width=0, height=0, filesize=0):
		wx.PyCommandEvent.__init__(self, etype, eid)
		self._value = value
		self._index = str(index)
		self._indexmax = str(indexmax)
		self._filename = filename
		self._width = width
		self._height = height
		self._filesize = filesize
		
	def GetValue(self):
		return self._value
		
	def GetIndex(self):
		return self._index, self._indexmax
		
	def GetFilename(self):
		return self._filename
		
	def GetDimensions(self):
		return self._width, self._height
		
	def GetSize(self):
		if self._filesize > 2097152:
			return str(round(float(self._filesize)/1048576, 2))+" MB"
		elif self._filesize > 2048:
			return str(round(float(self._filesize)/1024, 2))+" KB"
		else:
			return str(self._filesize)+" B"
		
class GenericEvent(wx.PyCommandEvent):
	def __init__(self, etype, eid, value=""):
		wx.PyCommandEvent.__init__(self, etype, eid)
		self._value = value
	def GetValue(self):
		return self._value

class GUI(wx.App):
	def __init__(self):
		wx.App.__init__(self)
		self.frame = wx.Frame(None)
		self.panel = wx.Panel(self.frame)
		self.csize = 1
		self.InitUI()
		self.Bind(EVT_NEWIMG, self.OnNewImage)
		self.Bind(EVT_COUNT, self.OnCount)
		self.Bind(EVT_CONNECTION_ATTEMPT, self.OnAttemptConnection)
		self.Bind(EVT_CONNECTION_FAILURE, self.OnFailedConnection)
		self.Bind(EVT_CONNECTION_SUCCESS, self.OnSuccessfulConnection)
		self.frame.Bind(wx.EVT_CLOSE, self.OnClose)
		self._nsprocess_active = False
		
	def InitUI(self):
		self.cpanel = wx.Panel(self.panel)
		
		self.cpanelb = wx.Panel(self.cpanel)
		self.StartB = wx.Button(self.cpanelb, label="Start")
		self.StartB.SetBackgroundColour((127,255,127))
		self.StartB.Bind(wx.EVT_BUTTON, self.nsimage)
		self.StopB = wx.Button(self.cpanelb, label="Stop")
		self.StopB.SetBackgroundColour((255,127,127))
		self.StopB.Disable()
		self.StopB.Bind(wx.EVT_BUTTON, self.stopnsimage)
		self.NextB = wx.Button(self.cpanelb, label="Next")
		self.NextB.Bind(wx.EVT_BUTTON, self.nextnsimage)
		self.BackB = wx.Button(self.cpanelb, label="Back")
		self.BackB.Bind(wx.EVT_BUTTON, self.prevnsimage)
		self.BackB.Disable()
		self.Addr = wx.TextCtrl(self.cpanelb, value="127.0.0.1")
		self.Port = wx.TextCtrl(self.cpanelb, value="8808")
		self.Time = wx.TextCtrl(self.cpanelb, value="300")
		self.Preqint = wx.TextCtrl(self.cpanelb, value="0")
		self.RandBox = wx.CheckBox(self.cpanelb, label="Rand")
		self.RandBox.Bind(wx.EVT_CHECKBOX, self.OnCheckRand)
		self.ReqB = wx.Button(self.cpanelb, label="Request")
		self.ReqB.Bind(wx.EVT_BUTTON, self.OnReq)
		self.SaveB = wx.Button(self.cpanelb, label="Save Local Copy")
		self.SaveB.Bind(wx.EVT_BUTTON, self.OnSave)
		self.RandBox.SetValue(True)
		
		self.cpaneli = wx.Panel(self.cpanel)
		self.cpaneli.SetBackgroundColour((32,32,32))
		self.cpaneli.SetForegroundColour((255,255,255))
		self.StatusText = wx.StaticText(self.cpaneli, label="Status: Slideshow Inactive")
		self.IntText = wx.StaticText(self.cpaneli, label="Index: 0/0")
		self.TimeText = wx.StaticText(self.cpaneli, label="Next: NaN")
		self.FileText = wx.StaticText(self.cpaneli, label="Filename: No Image")
		self.SizeText = wx.StaticText(self.cpaneli, label="Size: 0x0")
		
		self.imgcontainer = wxsp.ScrolledPanel(self.panel)
		self.imgcontainer.SetBackgroundColour((0,0,0))
		self.imgdsp = wx.StaticBitmap(self.imgcontainer, wx.ID_ANY, wx.BitmapFromImage(currentimage))
		self.imgdsp.Bind(wx.EVT_SIZE, self.OnResize)
		self.imgdsp.Bind(wx.EVT_LEFT_UP, self.OnLeftClick)
		self.gifdsp = wx.animate.GIFAnimationCtrl(self.imgcontainer, wx.ID_ANY, "localgif")
		self.gifdsp.Hide()
		
		self.mainbox = wx.BoxSizer(wx.VERTICAL)
		self.imgbox = wx.BoxSizer(wx.VERTICAL)
		self.cbox = wx.BoxSizer(wx.VERTICAL)
		self.cboxb = wx.BoxSizer(wx.HORIZONTAL)
		self.cboxi = wx.BoxSizer(wx.HORIZONTAL)
		
		self.cboxb.Add(self.StartB, 4)
		self.cboxb.Add(self.StopB, 2)
		self.cboxb.Add(self.SaveB, 2)
		self.cboxb.Add(self.RandBox, 1)
		self.cboxb.Add(self.ReqB, 1)
		self.cboxb.Add(self.Preqint, 1)
		self.cboxb.Add(self.BackB, 1)
		self.cboxb.Add(self.NextB, 1)
		self.cboxb.Add(self.Addr, 2)
		self.cboxb.Add(self.Port, 1)
		self.cboxb.Add(self.Time, 1)
		
		self.cboxi.Add(self.StatusText, 4, wx.CENTER)
		self.cboxi.Add(self.IntText, 3, wx.CENTER)
		self.cboxi.Add(self.FileText, 12, wx.CENTER)
		self.cboxi.Add(self.SizeText, 4, wx.CENTER)
		self.cboxi.Add(self.TimeText, 2, wx.CENTER)
		
		self.cpanelb.SetSizer(self.cboxb)
		self.cpaneli.SetSizer(self.cboxi)
		self.cbox.Add(self.cpanelb, 1, wx.EXPAND)
		self.cbox.Add(self.cpaneli, 1, wx.EXPAND)
		
		self.cpanel.SetSizer(self.cbox)
		
		self.mainbox.Add(self.cpanel, 0, wx.EXPAND)
		self.mainbox.Add(self.imgcontainer, 1, wx.EXPAND)
		self.imgbox.Add(self.imgdsp, 1, wx.CENTER)
		self.imgbox.Add(self.gifdsp, 1, wx.CENTER)
		self.panel.SetSizer(self.mainbox)
		self.imgcontainer.SetSizer(self.imgbox)
		
		self.lastsize = (1280,720)
		self.frame.SetSize(self.lastsize)
		self.frame.SetMinSize((1280, 720))
		self.frame.SetTitle("NetSlideshow Client")
		self.frame.Centre()
		self.frame.Show()
		
	def nsimage(self, evt):
		if self._nsprocess_active == False:
			self.nsprocess = NSImage(self, self.Addr.GetValue(), self.Port.GetValue(), self.Time.GetValue(), self.RandBox.GetValue())
			self.nsprocess.start()
			self._nsprocess_active = True
		
	def stopnsimage(self, evt):
		self.nsprocess.abort()
		self.StopB.Disable()
		self.StartB.Enable()
		self._nsprocess_active = False
		self.StatusText.SetLabel("Status: Slideshow Inactive")
		self.StatusText.SetForegroundColour((255,255,255))
		self.TimeText.SetLabel("Next: NaN")
	
	def nextnsimage(self, evt):
		self.nsprocess.next(self.Time.GetValue())
		
	def prevnsimage(self, evt):
		self.nsprocess.prev()
		
	def OnNewImage(self, evt):
		val = evt.GetValue()
		self._i, self._imax = evt.GetIndex()
		self._filename = evt.GetFilename()
		self._width, self._height = evt.GetDimensions()
		self._size = evt.GetSize()
		self.IntText.SetLabel("Index: "+self._i+"/"+self._imax)
		self.FileText.SetLabel("Filename: "+self._filename)
		self.SizeText.SetLabel("Size: "+str(self._width)+"x"+str(self._height)+" "+self._size)
		
		if self._filename[-4:] == ".gif":
			self.imgdsp.Hide()
			self.gifdsp.Show()
			self.gifdsp.LoadFile("localimage")
			self.gifdsp.Play()
			self.imgbox.Layout()
			self.imgcontainer.Refresh()
			self.panel.Refresh()
		else:
			self.gifdsp.Stop()
			self.imgdsp.Show()
			self.gifdsp.Hide()
			self.fiximage(val)
		
		self.SaveB.Enable()
		
	def OnSave(self, evt):
		savename = self._filename.split("\\")
		if len(savename) < 2:
			savename = self._filename.split("/")
		savename = ''.join(savename[-1:])
		if platform == "Windows":
			savename = "Saved\\"+savename
		else:
			savename = "Saved/"+savename
		print savename
		if not os.path.exists("Saved"):
			os.makedirs("Saved")
		shutil.copyfile("localimage", savename)
		self.SaveB.Disable()
		
	def OnResize(self, evt):
		self.fiximage(val=0)
		
	def OnCount(self, evt):
		val = evt.GetValue()
		self.TimeText.SetLabel("Next: "+str(val))
		
	def OnCheckRand(self, evt):
		val = self.RandBox.GetValue()
		if val == True:
			self.BackB.Disable()
		else:
			self.BackB.Enable()
		try:
			self.nsprocess.crand(val)
		except:
			None
			
	def OnReq(self, evt):
		try:
			self.nsprocess.creq(self.Preqint.GetValue())
		except:
			None
			
	def OnLeftClick(self, evt):
		if self.csize != 1:
			self.csize = 1
		else:
			self.csize = "Full"
		self.fiximage("NEWIMG")

	def OnAttemptConnection(self, evt):
		self.StatusText.SetLabel("Status: Connecting...")
		self.StatusText.SetForegroundColour((255,255,0))
		self.TimeText.SetLabel("Next: NaN")
		
	def OnFailedConnection(self, evt):
		self.nsprocess.abort()
		self._nsprocess_active = False
		self.StatusText.SetLabel("Status: CONNECTION FAILED")
		self.StatusText.SetForegroundColour((255,0,0))
		self.TimeText.SetLabel("Next: NaN")
		self.StopB.Disable()
		self.StartB.Enable()
		
	def OnSuccessfulConnection(self, evt):
		self.StatusText.SetLabel("Status: Slideshow Active")
		self.StatusText.SetForegroundColour((0,255,0))
		self.StartB.Disable()
		self.StopB.Enable()
		
	def fiximage(self, val):
		MW = float(self.imgcontainer.GetSize().width)
		MH = float(self.imgcontainer.GetSize().height)
		if ((MW, MH) != self.lastsize) or (val == "NEWIMG"):
			if self.csize == "Full":
				self.imgdsp.SetBitmap(wx.BitmapFromImage(currentimage))
			else:
				try:
					imgscale = float(self.csize)
				except:
					print "CRITICAL: SCALE VALUE IS NOT A FLOAT"
				W = float(currentimage.GetWidth())
				H = float(currentimage.GetHeight())
				if W>H and W>MW:
					R = H/W
					SW = MW
					SH = MW * R
					if MH < SH:
						R = W/H
						SW = MH * R
						SH = MH	
				elif H>MH:
					R = W/H
					SW = MH * R
					SH = MH
					if MW < SW:
						R = H/W
						SW = MW
						SH = MW * R
				else:
					SW = W
					SH = H
				SW *= imgscale
				SH *= imgscale
				scaledimage = currentimage.Scale(SW, SH, wx.IMAGE_QUALITY_HIGH)
				self.imgdsp.SetBitmap(wx.BitmapFromImage(scaledimage))
			self.lastsize = (MW, MH)
			if val == "NEWIMG":
				self.imgbox.Layout()
			self.imgcontainer.SetAutoLayout(1)
			self.imgcontainer.SetupScrolling()
			self.imgcontainer.Refresh()
			self.panel.Refresh()
			
	def OnClose(self, evt):
		try:
			self.nsprocess.abort()
		except:
			None
		os._exit(1)
		sys.exit(1)
				
class NSImage(threading.Thread):
	def __init__(self, parent, addr="127.0.0.1", port=8808, time=300, rand=True):
		threading.Thread.__init__(self)

		self._parent = parent
		self._addr = addr
		self._rand = rand
		self._preqint = 0
		
		self.aborting = False
		self.wait = threading.Event()
		self.curdir = "FORWARD"
		self.maxtime = 10
		
		try:
			self._port = int(port)
		except:
			self._port = 8808
		try:
			self._time = int(time)
			if self._time < self.maxtime:
				self._time = self.maxtime
		except:
			self._time = 300
		self.nscounter = Counter(self, self._time)
		self.counter_isStarted = False
		
	def run(self):
		while 1:
			if self.aborting == True: break
			cli = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			evt = GenericEvent(myEVT_CONNECTION_ATTEMPT, -1)
			wx.PostEvent(self._parent, evt)
			try:
				cli.connect((str(self._addr), self._port))
			except:
				self.abort()
				evt = GenericEvent(myEVT_CONNECTION_FAILURE, -1, value="CONNECTION FAILED")
				wx.PostEvent(self._parent, evt)
				break
			evt = GenericEvent(myEVT_CONNECTION_SUCCESS, -1)
			wx.PostEvent(self._parent, evt)
			cli.send("listsize")
			cllist = cli.recv(1024)
			global currint
			if self._preqint != 0:
				currint = self._preqint - 1
				self._preqint = 0
			elif self._rand == True:
				random.seed(str(os.urandom(256)))
				currint = random.randint(0,int(cllist)-1)
			elif self.curdir == "BACKWARD":
				currint -= 1
				self.curdir = "FORWARD"
			else:
				currint += 1
			if currint < 0:
				currint = int(cllist) - 1
			elif currint > int(cllist) - 1:
				currint = 0
			reqint = currint
			reqfile = open("localimage",'wb')
			cli.send(str(reqint))
			self._filename = cli.recv(1024)
			cli.send("OK")
			while 1:
				istream = cli.recv(1024)
				if not istream: break
				reqfile.write(istream)
			reqfile.close()
			cli.close()
			global currentimage 
			currentimage = wx.Image("localimage")
			fsize = os.path.getsize("localimage")
			imgw = currentimage.GetWidth()
			imgh = currentimage.GetHeight()
			evt = NewImageEvent(myEVT_NEWIMG, -1, value="NEWIMG", index=reqint+1, indexmax=cllist, filename=self._filename, width=imgw, height=imgh, filesize=fsize)
			wx.PostEvent(self._parent, evt)
			if self.counter_isStarted == True:
				self.nscounter.next(self._time)
			else:
				self.nscounter.start()
				self.counter_isStarted = True
			self.wait.wait(self._time)
			self.nscounter.waitnew()
	def abort(self):
		self.aborting = True
		self.wait.set()
		self.wait.clear()
		try:
			self.nscounter.abort()
		except:
			None

	def next(self, time=300):
		self.wait.set()
		self.wait.clear()
		self.curdir = "FORWARD"
		try:
			self._time = int(time)
			if self._time < self.maxtime:
				self._time = self.maxtime
		except:
			self._time = 300
		
	def prev(self):
		self.wait.set()
		self.wait.clear()
		self.curdir = "BACKWARD"
		
	def crand(self, val):
		self._rand = val
	
	def creq(self, preqint):
		try:
			self._preqint = int(preqint)
		except:
			self._preqint = 0
		self.next(self._time)
		
class Counter(threading.Thread):
	def __init__(self, parent, time):
		threading.Thread.__init__(self)
		self._parent = parent
		self._time = time
		self.wait = threading.Event()
		self.aborting = False
		self.reset = False
		self.waiting = False
		
	def run(self):
		ctime = self._time
		while 1:
			if self.aborting == True: break
			if self.reset == True:
				ctime = self._time
				self.reset = False
				self.waiting = False
			if self.waiting == False:
				evt = GenericEvent(myEVT_COUNT, -1, value=ctime)
				wx.PostEvent(self._parent._parent, evt)
				ctime -= 1
			self.wait.wait(1)
		
	def abort(self):
		self.wait.set()
		self.wait.clear()
		self.aborting = True
		
	def next(self, time):
		self.waiting = False
		self.reset = True
		self._time = time
		self.wait.set()
		self.wait.clear()
		
	def waitnew(self):
		self.waiting = True
		self.wait.set()
		self.wait.clear()
		
		
		
app=GUI()
app.MainLoop()
