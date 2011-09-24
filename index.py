#import the web module
import web
import socket

#define our url mapping
urls = (
  '/', 'index',
  '/track_info','get_track_info',
  '/skip','skip',
  '/love','love',
  '/pause','pause',
  '/station/(.*)/(.*)','station',
  '/volume/(.*)','volume',
  '/ban','ban'
)
#create a renderer
template_dir = 'templates'
render = web.template.render(template_dir)

#create the app
app = web.application(urls, globals(),False)

def process_socket(command,get_return=False):
  sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
  sock.settimeout(3)
  #connect to the socket
  try:  
    sock.connect('/home/YOUR_NAME/.shell-fm/unix_file')  
    #format and send data
    sock.sendall( command )
  except:
    #probably no socket, behave accordingly
    return "could not connect to socket"
    
  #get some data back
  if get_return:
    try:
      (string, address)=sock.recvfrom(512)
      sock.close()
      return string
    except:
      return "error"

#we need to send commands to 
class index:
	def GET(self):
		return render.index()

class get_track_info:
  def GET(self):
    command ="info %a::%t::%l::%d::%R::%s::%v::%r\n"
    data = process_socket(command,True)
    return data
    
class skip:
    def GET(self):
      process_socket("skip\n")
      return "OK"

class love:
    def GET(self):
      process_socket("love\n")
      
class ban:
    def GET(self):
      process_socket("ban\n")
      
class pause:
  def GET(self):
    process_socket("pause\n")
    
class volume:
  def GET(self,direction):
    for i in range(3):
      process_socket("volume-%s\n" % (direction) )

class station:
  def GET(self,type,text):
    command = "play lastfm://%s/%s\n" % (type,text)
    data = process_socket(command)
    return data
      
if __name__ == "__main__":
  app.run()
else:
	application = app.wsgifunc()
