import socket
import os
from paramiko import SSHClient

class SSHSocket:
	def __init__(self,addr,port,username,password):
		if ':' in addr:
			self.sshconnect = SSHClient()
		else:
			self.sshconnect = SSHClient()
