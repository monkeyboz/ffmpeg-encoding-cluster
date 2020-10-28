#/bin/bash

while getopts P:u:h:p:k:f:d:host:user:port option
	do
	case  "${option}"
	in
		host)	mainhost=${OPTARG};;
		user)	mainuser=${OPTARG};;
		port)	mainport=${OPTARG};;
		P)	port=${OPTARG};;
		u)	user=${OPTARG};;
		h)	host=${OPTARG};;
		p)	pass=${OPTARG};;
		d)	directory=${OPTARG};;
		k)	key=${OPTARG};;
		f)	file=${OPTARG};;
	esac
done

	if [ -ne $mainport] && [ -ne $mainuser ] && [ -ne $mainhost ]; then
		hostconnect="scp -P $mainport $mainuser@$mainhost:$file -P $port $user@$host:$directory"
		exec $hostconnect
	fi
