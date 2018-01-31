from subprocess import Popen, PIPE, check_output, CalledProcessError
import re

#getuser(user)
#getusers()
#getgroups()

def getuser(user=None):
	p1 = Popen(['getent', 'passwd',  user], stdout=PIPE, universal_newlines=True).communicate()[0]
	p2 = Popen(['groups',  'giuseppe'], stdout=PIPE, universal_newlines=True).communicate()[0]
	
	userinfo = p1.splitlines()
	userinfo = userinfo[0].split(':')

	usergroups = p2.splitlines()
	usergroups = re.sub('^.*: ', '', usergroups[0])
	usergroups = usergroups.split(' ')

	
	users = list()
	users.append({
		'uname': userinfo[0],
		'canlogin': 'yes' if userinfo[1]=='x' else 'no',
		'uid': userinfo[2],
		'gid': userinfo[3],
		'geco': userinfo[4].split(','),
		'home': userinfo[5],
		'shell': userinfo[6],
		'group': usergroups.pop(0),
		'groups': usergroups
	})
	
	return users

def getusers():
	p1 = Popen(["cat", "/etc/passwd"], stdout=PIPE)
	p2 = Popen(["cut", "-d:", "-f4-", "--complement"], stdin=p1.stdout, stdout=PIPE, universal_newlines=True).communicate()[0]
	p1.stdout.close()
	#universal newlines serve a restutuire l'output come stringa e non come bytes
	#p3 = Popen(["sed", "s/:.:/:/g"], stdin=p2.stdout, stdout=PIPE, universal_newlines=True).communicate()[0] #, stdout=outputfile)
	#p2.stdout.close()

	output = p2.splitlines()

	users = list()
	for i in output:
		actual = i.split(':')
		users.append({
			'uname': actual[0],
			'uid': actual[2]
	})

	return users


	#print(users)
	#print(*string, sep='\n')

	#for line in p1.stdout:
	#	print(line)
	#
	#p2.stdout.close()


def getgroups():
	p1 = Popen(["cat", "/etc/group"], stdout=PIPE, universal_newlines=True).communicate()[0]

	output = p1.splitlines()

	groups = list()
	for i in output:
		actual = i.split(':')
		groups.append({
			'gname': actual[0],
			'gid': actual[2],
			'members': actual[3].split(',')
		})

	return groups

def addusertogroup(user, group):

	try:
		check_output(['adduser', user, group])
	except CalledProcessError:
		print( 'Errore nell\'aggiunta dell\'utente %s al gruppo %s' % (user, group) )

def removeuserfromgroup(user, group):
	
	try:
		check_output(['gpasswd', '-d', user, group])
	except CalledProcessError:
		print( 'Errore nella rimozione dell\'utente %s dal gruppo %s' % (user, group) )
