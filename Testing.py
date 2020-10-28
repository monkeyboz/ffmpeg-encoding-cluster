from ServerCluster import ServerClusterClass

serverClusters = [
	{'host':'192.168.56.10','username':'monkeyboz','password':'ntisman1','port':'34','hostfiledir':'./testing/','remotefiledir':'~/files/'},
	{'host':'192.168.56.10','username':'monkeyboz','password':'ntisman1','port':'34','file':'somethingelse','hostfiledir':'./testing','remotefiledir':'~/'},
	{'host':'192.168.56.11','username':'monkeyboz','password':'ntisman1','port':'35','hostfiledir':'./testing','remotefiledir':'~/videos'}
]
server = ServerClusterClass(serverClusters);
server.serverClusterConnect();
