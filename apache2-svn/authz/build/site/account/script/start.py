# coding: utf8
import os
from flask import Flask
from flask import render_template
from flask import Response
from flask import request
import logging
import string
import time

import config

app = Flask(__name__)
handler = logging.FileHandler(config.LOGPATH, 'a')
formater = logging.Formatter('[%(asctime)s] %(levelname)s %(message)s','%Y-%m-%d %H:%M:%S',)
handler.setFormatter(formater)
app.logger.addHandler(handler)
app.logger.setLevel(logging.INFO)

CODE_OK = 0
CODE_USER_NOT_FOUND = 1
CODE_VERIFICATION_FAILED= 2
CODE_OTHER_ERROR = 3

@app.route("/reg", methods=['GET', 'POST'])
def reg():
	return handle("reg")

@app.route("/change", methods=['GET', 'POST'])
def change():
	return handle("change")

@app.route("/reset", methods=['GET', 'POST'])
def reset():
	return handle('reset')

@app.route("/admin", methods=['GET', 'POST'])
def admin():
	return handle('reset')


def handle(action):
	if request.method == 'GET':
		params = request.args.to_dict()
	elif request.method == 'POST':
		params = request.values.to_dict()
	else:
		params = {}

	params["ip"] = request.headers.get('X-Real-Ip', request.remote_addr)

	result = {}
	real_action = params.get("action")

	if real_action == "reg":
		ok, msg = do_reg(params)
	elif real_action == "change":
		ok, msg = do_change(params)
	elif real_action == 'reset':
		ok, msg = do_reset(params)
	else:
		ok = True
		msg = ""
	
	if ok and msg:
		result["title"] = msg
		result["username"] = params["username"]
		result["ip"] = params["ip"]
		result["opttime"] = time.strftime("%Y-%m-%d %H:%M:%S")
		result["oldurl"] = action
		templatefile = "result.html"
	else:
		result["msg"] = msg
		result["action"] = action
		titlemap = {"reset": u"重置SVN账号密码", "change":u"修改SVN账号密码", "reg": u"注册SVN账号"}
		result["title"] = titlemap.get(action, "")
		templatefile = "index.html"
	
	if msg:
		app.logger.info("action:%r ip:%r username:%r ok:%r"\
			%(action, params["ip"], params.get("username", ""), ok) )
	return Response(response=render_template(templatefile, **result))

def do_reg(params):
	ip = params.get("ip", "")
	username = params.get("username", "")
	pwd1 = params.get("pwd1", "")
	pwd2 = params.get("pwd2", "")
	
	ok, msg = check_param(username=username, pwdlist=[pwd1,pwd2], pwd1=pwd1, pwd2=pwd2)
	if ok:
		# 先检查帐号是否存在
		code = verify_password_api(username, "")
		if code == CODE_VERIFICATION_FAILED:
			msg = u"帐号 %s 已经存在"%username
			ok = False
		else:
			ok, msg = reset_pwd_api(username, pwd1, ip)
			if ok:
				msg = u"注册SVN帐号成功"
				
	return ok, msg

def do_change(params):
	ip = params.get("ip", "")
	username = params.get("username", "")
	pwdold = params.get("pwdold", "")
	pwd1 = params.get("pwd1", "")
	pwd2 = params.get("pwd2", "")

	ok, msg = check_param(username=username, pwdlist=[pwdold,pwd1,pwd2], pwd1=pwd1, pwd2=pwd2)
	if ok:
		code = verify_password_api(username, pwdold)
		if code == CODE_VERIFICATION_FAILED:
			msg = u"旧密码验证失败"
			ok = False
		elif code == CODE_USER_NOT_FOUND:
			msg = u"帐号 %s 不存在, 请先注册" % username
			ok = False
		elif code == CODE_OK:
			ok, msg = reset_pwd_api(username, pwd1, ip)
			if ok:
				msg = u"修改SVN密码成功"

	return ok, msg

def do_reset(params):
	ip = params.get("ip", "")
	admin_username = params.get("admin_username", "")
	admin_password = params.get("admin_password", "")
	# 检查admin的帐号和密码参数
	ok, msg = check_param(username=admin_username, pwdlist=[admin_password])
	if ok:
		# 检查是否有admin的权限
		if admin_username not in config.ADMIN_LIST:
			msg = u"管理员账号 %s 权限不足"%admin_username
			ok = False
		else:
			# 验证admin的密码
			code = verify_password_api(admin_username, admin_password)

			if code == CODE_OK:
				username = params.get("username", "")
				pwd1 = params.get("pwd1", "")
				pwd2 = params.get("pwd2", "")
				# 检查新设置的帐号的密码和用户名
				ok, msg = check_param(username=username, pwdlist=[pwd1,pwd2], pwd1=pwd1, pwd2=pwd2)
				if ok:
					# 重置
					code = verify_password_api(username, "")
					if code == CODE_USER_NOT_FOUND:
						ok = False
						msg = u"svn账号 %s 不存在, 请先注册"%username
					else:
						ok, msg = reset_pwd_api(username, pwd1, ip)
						if ok:
							msg = u"重置SVN密码成功"
			else:
				msg = u"管理员账号 %s 验证失败"%admin_username
				ok = False

	return ok, msg

def check_param(username="", pwdlist=[], pwd1=None, pwd2=None):
	if len(username)<=0:
		return False, u"用户名不能为空"
	if len(username) >= 32:
		return False, u"用户名不能超过32位"

	validstring = string.ascii_lowercase + string.digits
	for x in username:
		if x not in validstring:
			return False, u"用户名只能由数字和小写字母组成"
	
	for pwd in pwdlist:
		if len(pwd) <= 0 :
			return False, u"密码不能为空"
		if len(pwd) > 32:
			return False, u"密码不能超过32位"
	
	if pwd1 and pwd2 and pwd1!=pwd2:
		return False, u"2次输入的密码不一致"
	
	return True, "ok"
		
def verify_password_api_old(username, pwd):
	param = {"dbfile": config.DBFILE, "user": username, "pwd": pwd}
	cmd = """htpasswd -bv %(dbfile)s "%(user)s" "%(pwd)s" 2>&1 """%param
	fd = os.popen(cmd)
	data = fd.read().strip()
	#app.logger.debug("data:%r"%data)
	code = fd.close()
	if code is None and data.endswith(" correct."):
		return CODE_OK
	elif code == 1536 and data.endswith("not found"):
		return CODE_USER_NOT_FOUND
	elif code == 768 and data == "password verification failed":
		return CODE_VERIFICATION_FAILED
	app.logger.error("verify_password_api error:%r"%data)
	return CODE_OTHER_ERROR

def verify_password_api(username, pwd):
	found = False
	for line in open(config.DBFILE).xreadlines():
		if line.strip():
			name, value = line.split(":")
			if name == username:
				found = True
				oldpwd = value.strip()
				break
	
	if not found:
		return CODE_USER_NOT_FOUND

	try:
		if not pwd.strip():
			return CODE_VERIFICATION_FAILED

		if value.startswith("$apr1$"):
			items = value.split("$") # $apr1$eyP34xgp$/Ho9qOuO9maMFbM3k1olb0
			salt = items[2]
			cmd = "openssl passwd -apr1 -salt %s %s 2>&1"%(salt, pwd)
			fd = os.popen(cmd)
			data = fd.read().strip()
			#app.logger.info("cmd:%r"%cmd)
			#app.logger.info("data:%r"%data)
			#app.logger.info("oldpwd:%r"%oldpwd)
			code = fd.close()
			if data.strip() == oldpwd:
				return CODE_OK
			else:
				return CODE_VERIFICATION_FAILED
	except Exception, err:
		app.logger.error("exception :%r"%(err,))

	return CODE_OTHER_ERROR
		
def reset_pwd_api(username, pwd, ip):
	param = {"dbfile": config.DBFILE, "user": username, "pwd": pwd}
	cmd = """htpasswd -b %(dbfile)s "%(user)s" "%(pwd)s" 2>&1 """%param
	fd = os.popen(cmd)
	data = fd.read().strip()
	app.logger.debug("data:%r"%data)
	code = fd.close()
	if code is None:
		app.logger.debug("reset_pwd_api done. username:%r ip:%r"%(username, ip))
		return True, u"成功"
	else:
		return False, data
	
if __name__ == '__main__':
	app.run(host='0.0.0.0', port=8080, debug=True)

