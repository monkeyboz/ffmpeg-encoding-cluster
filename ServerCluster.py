import sys
import os
import subprocess
import threading
import datetime
from multiprocessing.pool import ThreadPool
from paramiko import SSHClient,Transport,AutoAddPolicy

class EncodingClass:
	file = ''
	def __init__(self,file,settings='-c:v libxvcc'):
		self.file = file
		self.settings = settings
	def encodeFile(self,filename,settings):
		if settings == None:
			settings = self.settings
		command = self.encodeSettings(filename,settings)
		return command
	def encodeSettings(self,file,settings):
		return 'ffmpeg i- [intputfile] [options] [outputfile]'.replace('[inputfile]',file).replace('[options]',settings);

class ServerCommands:
	serverCommands = {'connect':'connect','transfer':'transfer','send':'send'}
	file = ''
	def __init__(self,server,client):
		self.server = server
		self.client = client
		for a in self.serverCommands:
			self.serverCommands[a] = self.serverCommands[a].replace('[username]',str(server.connection['username'])).replace('[localhost]',str(server.connection['host'])).replace('[port]',str(server.connection['port']))
	def runCommand(self,command):
		a = command.split(':')
		if len(a) > 1:
			command = self.serverCommands[a[0]]
			if a[0] == 'transfer':
				try:
					print('Transfering file '+a[1]+' to server: '+self.server.connection['host'])
					sftp = self.client.open_sftp()
					self.file = a[1]
					#print('changing to video directory')
					if self.server.connection['remotefiledir'] != '':
						sftp.chdir(self.server.connection['remotefiledir'])
					print('Beginning transfer')
					sftp.put('./'+self.server.connection['hostfiledir']+a[1],a[1],self.progress)
					#sftp.close()
					print('Transfer completed')
				except Exception as e:
					return {'status':'error','error':e}
				pass
			if a[0] == 'scp':
				print('scp')
			if a[0] == 'transcode':
				encode = EncodingClass()
				self.client.exec_command(a[1])
			if a[0] == 'send':
				self.client.exec_command(a[1])
			return {'status':'completed'}
		else:
			self.client.exec_command(command)
			return {'status':'completed'}

	def progress(self,progress,total):
		something = progress+total

class ServerConnection:
	connection = {}
	def __init__(self,connection):
		self.connection = connection
		self.client = SSHClient()
		self.connect()
		self.totalConnections = 0
		self.serverCommands = ServerCommands(self,self.client)
		self.hostFileDir = ''
	def setHostFileDir(self,hostFile):
		self.hostFileDir = hostFile.replace('~/','')
	def setRemoteFileDir(self,remoteFile):
		self.remoteFileDir = remoteFile.replace('~/','')
	def keyDigest(self,key):
		self.key = key
	def connect(self):
		try:
			self.client.set_missing_host_key_policy(AutoAddPolicy())
			if ('password' in self.connection) and ('username' in self.connection):
				self.client.connect(str(self.connection['host']),port=self.connection['port'],username=self.connection['username'],password=self.connection['password'])
			else:
				self.client.connect(str(self.connection['host']),port=self.connection['port'])
			self.totalConnections = self.totalConnections+1
			return {'status':'connected'}
		except Exception as e:
			return {'status':'error','error':e}
		pass
	def disconnect(self):
		self.client.close()
	def transferDirectory(self):
		if os.path.exists(self.hostFileDir):
			dirlist = os.listdir(self.hostFileDir)
			commands = []
			pool = ThreadPool(1)
			for a in dirlist:
				commands.append('transfer:'+a)
			pool.map(self.serverCommands.runCommand,commands)
			pool.close()
			pool.join()
			#self.disconnect()
			print('Disconnected from server - '+self.connection['host'])
		else:
			print('Directory '+self.hostFileDir+'does not exist')
	def transferFile(self,file):
		self.serverCommands.runCommand('transfer:'+file)
	def transferFileServer(self,file,receivingServer):
		self.serverCommands.runCommand('transfer:'+file)
	def sendCommand(self,command):
		self.serverCommands.runCommand(command)
	def setError(self,error):
		self.error = 'error'

class ServerClusterClass:
	serverList = []
	serverOrder = []
	totalConnections = 0
	def __init__(self,*args):
		if len(args) > 0:
			self.serverList = serverList
	def addServerList(self,servers):
		self.serverList.append(servers)
	def checkServerOrder(self):
		serverOrder = []
		count = 0
		for a in range(0..len(self.serverList)):
			if serverOrder.len < 0:
				serverOrder[0] = count
			else:
				print('testing')
	def serverClusterConnect(self):
		tefarray = {}
		count = len(tefarray)
		pool = ThreadPool(5)
		servers = []
		for a in self.serverList:
			servers.append(a)
		pool.map(self.connectToServer,servers)
		pool.close()
		pool.join()
	def doJob(self,server,serverConnect):
		print('Running server job '+server['host'])
		if 'hostfiledir' in server:
			serverConnect.setHostFileDir(server['hostfiledir'])
		else:
			serverConnect.setHostFileDir('~/')
		if 'remotefiledir' in server:
			serverConnect.setRemoteFileDir(server['remotefiledir'])
		else:
			serverConnect.setRemoteFileDir('')
		if 'file' in server:
			return serverConnect.transferFile(server['file'])
		else:
			if serverConnect.hostFileDir != '~/':
				return serverConnect.transferDirectory()
		return ''
	def connectToServer(self,server):
		serverConnect = ServerConnection(server)
		print('Connecting to server - '+server['host'])
		status = serverConnect.connect()
		if(status['status'] != 'error'):
			print('Connected to server - '+server['host'])
			self.totalConnections = self.totalConnections+1
			self.doJob(server,serverConnect)
			server['job_completed'] = str(datetime.datetime.now())
		else:
			print('Error connecting to server - '+server['host'])
			server['error'] = status['error']
			server['job_completed'] = datetime.datetime.now()
