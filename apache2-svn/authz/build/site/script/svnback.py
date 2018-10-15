#! /usr/bin/env python
import sys, time, os
import shell


#----------------------------------------------------------------------
# main program 
#----------------------------------------------------------------------
def main(argv):
	if len(argv) < 4:
		print 'usage: svnback.py COMMAND REPOS_PATH BACKUP_PATH [passwd]'
		print 'available commands:'
		print '    dump - full dump svn to BACKUP_PATH'
		print '    inc  - increamental dump to BACKUP_PATH'
		print '    reserve - reserve how many full dumps in BACKUP_PATH'
		return 0
	CMD = argv[1].strip('\r\n\t ').lower()
	REPOS = argv[2].strip('\r\n\t')
	BACKUP = argv[3].strip('\r\n\t')
	PASSWD = len(argv) > 4 and argv[4].strip('\r\n\t ') or ''
	if not os.path.exists(REPOS):
		sys.stderr.write('can not find: %s\n'%REPOS)
		return -1
	if not os.path.exists(BACKUP):
		shell.mkdir(BACKUP)
	REPOS = os.path.abspath(REPOS)
	BACKUP = os.path.abspath(BACKUP)
	if not os.path.exists(BACKUP):
		sys.stderr.write('can not open: %s\n'%BACKUP)
		return -1
	ts = shell.timestamp(None)
	CFG = os.path.join(BACKUP, '.backup_cfg')
	config = shell.load_config(CFG)
	if not config:
		config = {}
	revision = int(config.get('revision', 0))
	youngest = shell.execute(['svnlook', 'youngest', REPOS], False, True)
	youngest = int(youngest.strip('\r\n\t '))
	name7z = '7z'
	if not shell.UNIX:
		name7z = '7za.exe'
	if CMD == 'dump':
		name = '%s.%s.full'%(ts, youngest)
		print 'dump %s to %d'%(name, youngest)
		args = ['svnadmin', 'dump', REPOS, '|', name7z, 'a', '-bd']
		args += [ '-si%s'%name ]
		if PASSWD: 
			args += [ '-p' + PASSWD ]
		args += [ os.path.join(BACKUP, name + '.7z') ]
		shell.execute(args, True)
		shell.save_config(CFG, {'revision': youngest})
	elif CMD == 'inc':
		first = revision + 1
		name = '%s.%s.%s.inc'%(ts, first, youngest)
		if revision == youngest:
			print 'nothing to backup'
			return 1
		print 'inc %s from %d to %d'%(name, first, youngest)
		args = ['svnadmin', 'dump', '--incremental', REPOS ]
		args += ['--revision', '%d:%d'%(first, youngest)]
		args += ['|', name7z, 'a', '-bd', '-si%s'%name]
		if PASSWD:
			args += ['-p' + PASSWD]
		args += [ os.path.join(BACKUP, name + '.7z') ]
		shell.execute(args, True)
		shell.save_config(CFG, {'revision': youngest})
	elif CMD == 'reserve':
		if not PASSWD:
			print 'usage: svnback.up reserve REPOS_PATH BACKUP_PATH N'
			print 'use N to indicate how many full dump are you going to reserve' 
			return 0
		N = int(PASSWD)
		if N < 1:
			print 'N must greater than zero'
			return 0
		FULL = []
		INC = []
		for n in os.listdir(BACKUP):
			filepath = os.path.join(BACKUP, n)
			if n[-8:].lower() == '.full.7z':
				t = n.split('.')
				if len(t) != 4: continue
				DATE = t[0]
				REV = int(t[1])
				FULL.append((REV, DATE, filepath))
			elif n[-7:].lower() == '.inc.7z':
				t = n.split('.')
				if len(t) != 5: continue
				DATE = t[0]
				REV = int(t[2])
				INC.append((REV, DATE, filepath))
		DELETE = []
		FULL.sort()
		if not FULL:
			print 'not find any full dump'
			return 0
		if len(FULL) < N:
			print 'no need to remove'
			return 0
		X = len(FULL) - N
		reserve_rev = FULL[X][0]
		reserve_date = FULL[X][1]
		for REV, DATE, FN in FULL + INC:
			if (REV, DATE) < (reserve_rev, reserve_date):
				DELETE.append(FN)
		DELETE.sort()
		for fn in DELETE:
			os.remove(fn)
			#print fn
	return 0


#----------------------------------------------------------------------
# testing case
#----------------------------------------------------------------------
if __name__ == '__main__':
	argv = [ '', 'inc', 'd:/local/svn', 'k:/temp/svnback', 'kiss' ]
	argv = [ '', 'reserve', 'd:/local/svn', 'k:/temp/svnback', '4' ]
	#main(argv)
	main(sys.argv)

