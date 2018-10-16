#! /usr/bin/python2
import sys
import os
import time
import shell

HOME = '/var/lib/svn/repos'
BACKUP = '/var/lib/backup'

if 0:
	HOME = '/home/data/lib/svn/repos'
	BACKUP = '/home/skywind/tmp/backup'

SCRIPT = os.path.join(os.path.dirname(__file__), 'svnback.py')
SCRIPT = os.path.abspath(SCRIPT)
LOGFILE = None

def mlog(*argv):
	global LOGFILE
	if not LOGFILE:
		LOGFILE = open(os.path.join(BACKUP, 'backup.log'), 'a')
	head = time.strftime('[%Y-%m-%d %H:%M:%S]')
	text = ' '.join([ str(n) for n in argv ])
	text = head + ' ' + str(text) + '\n'
	LOGFILE.write(text)
	LOGFILE.flush()
	sys.stdout.write(text)
	sys.stdout.flush()
	return 0

def backup(method, passwd):
	names = []

	for name in os.listdir(HOME):
		path = os.path.join(HOME, name)
		if not os.path.isdir(path):
			continue
		names.append(name)

	mlog('backup %s for %s'%(method, names))

	for name in names:
		home = os.path.join(HOME, name)
		backup = os.path.join(BACKUP, name)
		if not os.path.isdir(backup):
			try:
				os.makedirs(backup)
			except:
				pass
		if method in ('dump', 'full'):
			shell.execute(['python', SCRIPT, 'dump', home, backup, passwd])
			shell.execute(['python', SCRIPT, 'reserve', home, backup, '4'])
		else:
			shell.execute(['python', SCRIPT, 'inc', home, backup, passwd])
	return 0

def main(argv = None):
	argv = argv is None and sys.argv or argv
	argv = [ n for n in argv ]
	if len(argv) < 3:
		print 'python backup.py [dump|inc] PASSWORD'
		return 0
	method = argv[1].lower()
	passwd = argv[2]
	if method not in ('dump', 'full', 'inc'):
		print 'bad method'
		return 0
	backup(method, passwd)
	return 0

if __name__ == '__main__':
	def test1():
		argv = [__file__, 'dump', 'nopasswd']
		main(argv)
		return 0

	# test1()
	main()


