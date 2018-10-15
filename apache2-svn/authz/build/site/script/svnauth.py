import sys, os, time, shutil
import shell
import json


#----------------------------------------------------------------------
# AuthzSvn
#----------------------------------------------------------------------
class AuthzSvn (object):

	def __init__ (self):
		self.reset()
	
	def reset (self):
		self.config = {}
		self.names = []
	
	def append (self, name, content):
		if type(content) == type(u''):
			content = content.encode('utf-8')
		if content[:3] == '\xef\xbb\xbf':	# remove BOM+
			content = content[3:]
		import ConfigParser
		import StringIO
		fp = StringIO.StringIO(content)
		cp = ConfigParser.ConfigParser()
		cp.readfp(fp)
		self.config[name] = cp
		self.names.append(name)
		return 0

	def generate (self):
		import cStringIO
		fp = cStringIO.StringIO()
		fp.write('[groups]\n')
		names = [ n for n in self.names ]
		for name in names:
			cp = self.config[name]
			if not cp.has_section('groups'):
				continue
			for key, val in cp.items('groups'):
				key = key.strip('\r\n\t ')
				users = []
				for user in val.split(','):
					user = user.strip('\r\n\t ')
					if user[:1] == '@':
						users.append('@%s_%s'%(name, user[1:]))
					else:
						users.append(user)
				val = ', '.join(users)
				fp.write('%s_%s = %s\n'%(name, key, val))
		fp.write('\n\n')
		for name in names:
			cp = self.config[name]
			fp.write('# authz for %s\n'%name)
			for sect in cp.sections():
				#print '%s:%s'%(name, sect)
				if sect == 'groups':
					continue
				utfsect = sect.decode('utf-8')
				fp.write(('[%s:%s]\n'%(name, utfsect)).encode('utf-8'))
				for key, val in cp.items(sect):
					key = key.strip('\r\n\t ')
					if key[:1] != '@':
						fp.write('%s = %s\n'%(key, val))
					else:
						fp.write('@%s_%s = %s\n'%(name, key[1:], val))
				fp.write('\n')
			fp.write('\n')
		fp.write('\n')
		return fp.getvalue()
	
	


#----------------------------------------------------------------------
# AuthzMerge
#----------------------------------------------------------------------
def AuthzMerge(jsoncfg):
	authz = AuthzSvn()
	import json
	config = json.loads(jsoncfg)
	if type(config) != type({}):
		return -1
	if not 'out' in config:
		return -2
	outname = config['out']
	history = config.get('history', None)
	sources = []
	source = config.get('source', None)
	if isinstance(source, list):
		sources = [ n for n in source ]
	elif isinstance(source, str) or isinstance(source, unicode):
		if os.path.exists(source):
			for fn in os.listdir(source):
				path = os.path.join(source, fn)
				if not os.path.isdir(path):
					continue
				sources.append({'name': fn, 'repos': path, 'path': '/authz/access.ini'})
	footer = config.get('footer', None)
	admins = config.get('admin', None)
	if type(sources) != type([]):
		return -3
	for item in sources:
		if type(item) != type({}):
			return -4
		name = item.get('name', None)
		if not name:
			return -5
		repos = item.get('repos', None)
		if not repos:
			return -6
		filepath = item.get('path', None)
		if not filepath:
			return -7
		text = shell.svnlook_cat(repos, filepath)
		if text is not None:
			authz.append(name, text)
		else:
			print 'failed to read %s in %s'%(filepath, repos)
	output = authz.generate()
	if footer:
		output += '\n# footer\n%s\n\n'%str(footer)
	if admins:
		output += '\n# admins\n'
		for source in sources:
			name = source['name']
			for admin in admins:
				output += '[%s:/]\n%s = rw\n'%(name, admin)
			output += '\n'
		output += '\n'
	write = False
	if not os.path.exists(outname):
		write = True
	else:
		fp = open(outname)
		text = fp.read()
		fp.close()
		if text != output:
			write = True
	#write = True
	if not write:
		print 'skip', outname
		return 0
	import tempfile
	fd, tmpname = tempfile.mkstemp('.authz.tmp', '.svn-')
	fp = os.fdopen(fd, 'w+')
	fp.write(output)
	fp.close()
	if history:
		name = time.strftime('authz.%Y%m%d%H%M%S.ini')
		name = os.path.join(history, name)
		shutil.copyfile(tmpname, name)
		print 'write history', name
	shutil.move(tmpname, outname)
	if sys.platform[:3] != 'win':
		import stat
		mode = stat.S_IRUSR | stat.S_IWUSR 
		mode |= stat.S_IRGRP | stat.S_IWGRP 
		mode |= stat.S_IROTH 
		os.chmod(outname, mode)
	print 'update', outname
	return 0


#----------------------------------------------------------------------
# main
#----------------------------------------------------------------------
def main(args = None):
	if not args:
		args = sys.argv
	args = [ n for n in args ]
	if len(args) < 2:
		print 'usage: %s config'%args[0]
		return -1
	name = args[1]
	if not os.path.exists(name):
		print 'can not read %s'%name
		return -2
	AuthzMerge(open(name).read())
	return 0


#----------------------------------------------------------------------
# testing case
#----------------------------------------------------------------------
if __name__ == '__main__':

	def test1():
		auth = AuthzSvn()
		auth.append('corp', open('svn1.auth').read())
		auth.append('svn', open('svn2.auth').read())
		text = auth.generate()
		import ConfigParser, StringIO
		cp = ConfigParser.ConfigParser()
		cp.readfp(StringIO.StringIO(text))
		#print cp.sections()
		print text.decode('utf-8')
		return 0

	def test2():
		repos = 'd:/local/svn'
		rev = shell.svnlook_youngest(repos)
		print shell.svnlook_cat(repos, '/works/work/COPYRIGHT', rev)
		return 0

	def test3():
		text = shell.svn_cat('https://192.168.0.20/svn/authz/access.svn.ini')
		print text.decode('utf-8')[3:]
		return 0
	
	def test4():
		cfg = '''
		{
			"out":"svnout.auth",
			"history":".",
			"source": [
				{"name":"svn1", "repos":"/home/skywind/tmp/repos/svn1", "path":"/authz/access.ini"},
				{"name":"svn2", "repos":"/home/skywind/tmp/repos/svn2", "path":"/authz/access.ini"},
				{"name":"svn3", "repos":"/home/skywind/tmp/repos/svn3", "path":"/authz/access.ini"}
			],
			"footer":"# footer\\n"
		}
		'''
		AuthzMerge(cfg)
		return 0

	def test5():
		cfg = '''
		{
			"out":"svnout.auth",
			"history":".",
			"source": "/home/skywind/tmp/repos",
			"admin": ["svnadmin", "skywind"],
			"footer":"# footer\\n"
		}
		'''
		AuthzMerge(cfg)
		return 0

	#test5()
	main()

