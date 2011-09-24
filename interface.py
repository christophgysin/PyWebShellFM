from pyjamas.ui.HTML import HTML
from pyjamas.ui.RootPanel import RootPanel
from pyjamas.ui.SimplePanel import SimplePanel
from pyjamas.ui.HorizontalPanel import HorizontalPanel
from pyjamas.ui.Label import Label
from pyjamas.ui.Button import Button
from pyjamas.ui.VerticalPanel import VerticalPanel
from pyjamas.HTTPRequest import HTTPRequest
from pyjamas.Timer import Timer
from pyjamas.ui.ListBox import ListBox
from pyjamas.ui.TextBox import TextBox
from pyjamas.ui.FlexTable import FlexTable
from pyjamas import DOM
from pyjamas import Window

class InfoHandler:
	def __init__(self, panel):
		self.panel = panel 
	
	def onError(self, text, code):
		self.panel.onError(text, code)

	def onTimeout(self, text):
		self.panel.onTimeout(text)
		
class NullInfoHandler(InfoHandler):
	def __init__(self, panel):
		InfoHandler.__init__(panel)
		self.panel = panel

	def onCompletion(self, text):
		pass	

class ButtonInfoHandler(InfoHandler):
	def __init__(self, panel,button):
		InfoHandler.__init__(panel)
		self.panel = panel
		self.button = button
		
	def onCompletion(self, text):
		self.button.setEnabled(True)

class TrackInfoHandler(InfoHandler):
	def __init__(self, panel):
		InfoHandler.__init__(panel)
		self.panel = panel

	def onCompletion(self, text):
		#return the text to the application for processing
		self.panel.process_track_info(text)

class Application:
	def __init__(self):
		#set some vars
		self.title = "PyWebShellFM"
		#this is where we build the ui
		self.statusPanel = VerticalPanel()
		self.statusPanel.setID('status_panel')
		#make a few Labels to hold artist, track, album info
		self.artistLabel = Label()
		self.trackLabel = Label()
		self.albumLabel = Label()
		self.timeLabel = Label()
		self.infoTable = FlexTable()
		i=0
		self.infoTable.setWidget(i,0,Label("Artist:") )
		self.infoTable.setWidget(i,1,self.artistLabel)
		i+=1
		self.infoTable.setWidget(i,0,Label("Track:") )
		self.infoTable.setWidget(i,1,self.trackLabel)
		i+=1
		self.infoTable.setWidget(i,0,Label("Album:") )
		self.infoTable.setWidget(i,1,self.albumLabel)
		
		self.statusPanel.add(self.infoTable)
		self.statusPanel.add(self.timeLabel)
		#make the time bar
		timebarWrapperPanel = SimplePanel()
		timebarWrapperPanel.setID("timebar_wrapper")
		#timebarWrapperPanel.setStyleName('timebar_wrapper')
		self.timebarPanel = SimplePanel()
		self.timebarPanel.setID("timebar")
		#self.timebarPanel.setStyleName('timebar')
		timebarWrapperPanel.add(self.timebarPanel)
		self.statusPanel.add(timebarWrapperPanel)
		#make some shit for buttons
		self.buttonHPanel = HorizontalPanel()
		self.skipButton = Button("Skip", self.clicked_skip )
		self.buttonHPanel.add(self.skipButton)
		loveButton = Button("Love", self.clicked_love )
		self.buttonHPanel.add(loveButton)
		pauseButton = Button("Pause", self.clicked_pause )
		self.buttonHPanel.add(pauseButton)
		banButton = Button("Ban", self.clicked_ban )
		self.buttonHPanel.add(banButton)

		#control the volume
		self.volumePanel = VerticalPanel()
		self.volumeLabel = Label("Volume:")
		self.volumePanel.add(self.volumeLabel)
		volupButton = Button("volume +", self.clicked_volume_up, 5)
		self.volumePanel.add(volupButton)
		voldownButton = Button("volume -", self.clicked_volume_down, 5)
		self.volumePanel.add(voldownButton)
		
		#make some stuff for station Identification
		self.stationInfoHPanel = HorizontalPanel()
		stationText = Label("Station: ")
		self.stationLabel = Label()
		self.stationInfoHPanel.add(stationText)
		self.stationInfoHPanel.add(self.stationLabel)
		
		#make buttons and shit to create a new station
		self.setStationHPanel = HorizontalPanel()
		self.setStationTypeListBox = ListBox()
		self.setStationTypeListBox.setVisibleItemCount(0)
		self.setStationTypeListBox.addItem("Artist","artist")
		self.setStationTypeListBox.addItem("Tags","globaltags")
		self.setStationHPanel.add(self.setStationTypeListBox)
		self.setStationTextBox = TextBox()
		self.setStationTextBox.setVisibleLength(10)
		self.setStationTextBox.setMaxLength(50)
		self.setStationHPanel.add(self.setStationTextBox)
		self.setStationButton = Button("Play", self.clicked_set_station)
		self.setStationHPanel.add(self.setStationButton)
		
		#make an error place to display data
		self.infoHTML = HTML()
		RootPanel().add(self.statusPanel)
		RootPanel().add(self.buttonHPanel)
		RootPanel().add(self.volumePanel)
		RootPanel().add(self.stationInfoHPanel)
		RootPanel().add(self.setStationHPanel)
		RootPanel().add(self.infoHTML)
		
	def run(self):
		self.get_track_info()

	def get_track_info(self):
		HTTPRequest().asyncGet("/track_info", TrackInfoHandler(self))
		Timer(5000,self.get_track_info)

	def clicked_skip(self):
		self.skipButton.setEnabled(False)	
		HTTPRequest().asyncGet("/skip",ButtonInfoHandler(self,self.skipButton) )

	def clicked_volume_down(self):
		HTTPRequest().asyncGet("/volume/down",NullInfoHandler(self)	)

	def clicked_volume_up(self):
		HTTPRequest().asyncGet("/volume/up",NullInfoHandler(self)	)

	def clicked_love(self):
		HTTPRequest().asyncGet("/love",NullInfoHandler(self) )

	def clicked_ban(self):
		result = Window.confirm("Really ban this song?")
		if result:
			HTTPRequest().asyncGet("/ban",NullInfoHandler(self) )

	def clicked_pause(self):
		HTTPRequest().asyncGet("/pause",NullInfoHandler(self) )


	def clicked_set_station(self):
		type = self.setStationTypeListBox.getSelectedValues()[0]
		text = self.setStationTextBox.getText().strip()
		if len(text) > 0 :
			#clear the text
			self.setStationTextBox.setText("")
			HTTPRequest().asyncGet("/station/%s/%s"% (type,text),NullInfoHandler(self) )

	def set_error(self, content):
		self.infoHTML.setHTML("<pre>%s</pre>" % content)
		
	def onTimeout(self,text):
		self.infoHTML.setHTML("timeout: "+text)
		
	def onError(self, text, code):
		self.infoHTML.setHTML(text + "<br />" + str(code))
		
	def process_track_info(self,text):
		#explode the text at :: 
		#%a::%t::%l::%d::%R::%s::%v::%r
		data = text.split("::")
		artist = data[0]
		track = data[1]
		album = data[2]
		duration = data[3]
		played = int(duration)-int(data[4])
		percent = int( played/int(duration)*100 )
		self.artistLabel.setText( artist )
		self.trackLabel.setText( track )
		self.albumLabel.setText( album )
		#format time
		t = "%s : %d	%d" % (duration,played,percent)
		self.timeLabel.setText(data[7])
		#update the timebarwidth
		self.timebarPanel.setWidth("%d%" % (percent) )
		#set the station
		self.stationLabel.setText(data[5])
		#display the volume
		self.volumeLabel.setText("Volume: "+data[6])
		Window.setTitle(self.title+": "+artist+" - "+track)
		
if __name__ == '__main__':
	app = Application()
	app.run()
