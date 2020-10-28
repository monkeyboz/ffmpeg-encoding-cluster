import os
import json
import threading
from ServerCluster import ServerClusterClass
from getpass import getpass
from cryptography.fernet import Fernet

class CliOptions:
	servers = []
	currScreen = 0
	serverCluster = ServerClusterClass()
	menuValue = 0

	#CliOptions constructor
	def __init__(self):
		print('Welcome to the Encoding Sever Cluster CLI')
		self.options = [
			{'name':'Server Setup','submenu':[
				{'name':'Add Server','function':self.serverSetup},
				{'name':'Setup Jobs','function':self.setupJobForServer},
				{'name':'Start Server','function':self.startServers},
				{'name':'Delete Server','function':self.deleteServer},
				{'name':'List Severs','function':self.listServers}]},
			{'name':'Start Server(s)','function':self.startServers}
		]
		os.system('clear')
		if os.path.isfile('server_list'):
			r = self.decryptInformation('server_list')
			self.servers = json.loads(r.replace("\'","\""))
			self.serverCluster.serverList = self.servers
		self.optionScreen()

	#headerCli function
	def headerCli(self,screenTitle):
		print('Encoding Server Cluster System CLI ('+screenTitle+')')
	
	#create encrypted key file
	def createEncryptionKey(self):
		key = Fernet.generate_key()
		with open('file_key','wb') as mykey:
			mykey.write(key)

	#create encrypted information and write to file
	def encryptInformation(self,file,info):
		with open('file_key','rb') as filekey:
			key = filekey.read()
		
		f = Fernet(key)
		
		e_original = f.encrypt(bytes(str(info),'utf-8'))
		
		with open(file,'wb') as server_list:
			server_list.write(e_original)
	
	#decrypt information and return result
	def decryptInformation(self,file):
		with open('file_key','rb') as filekey:
			key = filekey.read()
		
		with open(file,'rb') as file:
			e_original = file.read()
		
		f = Fernet(key)
		return f.decrypt(e_original).decode()

	#optionScreen function
	def optionScreen(self):
		print('Choose from the options below')
		for a in range(len(self.options)):
			print(str(a+1)+') '+str(self.options[a]['name']))
		self.menuValue = self.inputReturn(':')
		if self.menuValue == 'exit':
			exit()
		self.currScreen = int(self.menuValue)-1
		os.system('clear')
		self.headerCli(self.options[self.currScreen]['name'])
		if 'function' in self.options[self.currScreen]:
			self.options[self.currScreen]['function']()
		if 'submenu' in self.options[self.currScreen]:
			for a in range(len(self.options[self.currScreen]['submenu'])):
				print(str(a+1)+')'+str(self.options[self.currScreen]['submenu'][a]['name']))
		self.menuValue = self.inputReturn(':')
		if self.menuValue == 'b':
			self.optionScreen()
		else:
			self.subScreen = int(self.menuValue)-1
			os.system('clear')
			if self.options[self.currScreen]['submenu'][self.subScreen]['function']() == 'error':
				print('testing')
			self.optionScreen()

	#inputReturn function
	def inputReturn(self,text,*args,**default):
		if default.get('password',False):
			value = getpass(text)
		else:
			value = input(text)
		tries = default.get('tries',1)
		default = default.get('default',None)
		if tries > 3:
			print('Sorry but the option failed')
		else:
			if (value.strip() == ''):
				if (default !=  None):
					return default
				else:
					print('Sorry invalid entry, please try again.')
					tries = tries+1
					return self.inputReturn(text,tries=tries)
			return value

	#serverSetup function
	def serverSetup(self):
		server = {}
		host = self.inputReturn('host: ')
		port = self.inputReturn('port(default 22): ',default='22')
		server['host'] = host
		server['port'] = port
		if('up' == self.inputReturn('Will you be using a keyfile(k) or username and password(up)? (default is up) (k,up,[default])',default="up")):
			username = self.inputReturn('Enter username: ')
			password = self.inputReturn('Enter password: ',password=True)
			server['password'] = password
			server['username'] = username
		server = {**server,**self.setupJobForServer()}
		self.serverCluster.serverList.append(server)
		if os.path.exists('file_key'):
			self.encryptInformation('server_list',self.serverCluster.serverList)
		else:
			self.createEncryptionKey()
			self.encryptInformation('server_list',self.serverCluster.serverList)

	#setupJobForServer function
	def setupJobForServer(self):
		job = {}
		hostdirectory = self.inputReturn('Host Directory (default ~/):[default]',default='~/')
		remotedirectory = self.inputReturn('Remote Directory (default ~/):[default]',default='~/')
		job['hostfiledir'] = hostdirectory.replace('~/','')
		job['remotefiledir'] = remotedirectory.replace('~/','')
		print(job['hostfiledir'])
		sendFile = self.inputReturn('Send a file(f) or entire directory(ed) (default ed):[default]',default='ed')
		if sendFile == 'f':
			sendFile = self.inputReturn('Type file being sent (include directory if needed): '+hostdirectory)
			job['file'] = sendFile
		elif sendFile == 'ed':
			directory = self.inputReturn('Type directory being send(default Host Directory): '+hostdirectory,default=hostdirectory)
			job['hostfiledir'] = directory
			print(job)
		else:
			print('unable to do command')
		return job

	#deleteServer function
	def deleteServer(self):
		size = len(self.serverCluster.serverList)
		if size < 1:
			return 'no servers available'
		else:
			print('Select which server you would like to delete')
			for a in range(size):
				print(str(a+1)+') '+self.serverCluster.serverList[a]['host'])
			selection = self.inputReturn(':')
			if selection != 'exit':
				selection = int(selection)-1
				print('Server '+self.serverCluster.serverList[selection]['host']+' is removed')
				self.serverCluster.serverList.remove(self.serverCluster.serverList[selection])
				
	#listServers function
	def listServers(self):
		self.headerCli('Server List')
		servers = self.serverCluster.serverList
		for a in range(len(self.serverCluster.serverList)):
			print(str(a+1)+') '+servers[a]['host']+':'+servers[a]['port']+'  '+servers[a]['username'])
		print('----------------')
	#startserver function
	def startServers(self):
		size = len(self.serverCluster.serverList)
		if size < 1:
			return 'no servers available'
		print('Select which server you would like to start')
		for a in range(size):
			print(str(a+1)+') '+str(self.serverCluster.serverList[a]['host']))
		print('a) Connect to all servers')
		serverSelect = self.inputReturn(':')
		if serverSelect == 'b':
			return ''
		elif serverSelect == 'a':
			print('Multi-server process started')
			thread = threading.Thread(target=self.serverCluster.serverClusterConnect)
			thread.start()
		else:
			print('Server process started')
			thread = threading.Thread(target=self.serverCluster.connectToServer,args=(self.serverCluster.serverList[int(serverSelect)-1],));
			thread.start()
cli = CliOptions()
