import base64
import os
import time
from libs.db import DBSession, Conf, Account, Stu, Tch, Jn, Patent, Soft, Mono, Prog, Comp, Course, Honor, News, \
    Resource, Issues, People


class Admin(object):
    dbname = ''
    bpname = ''


    def __init__(self, dbname, bpname):
        self.dbname = dbname
        self.bpname = bpname

    # 所有数据({}...)

    def getAll(self):
        sessions = DBSession()
        info = sessions.query(self.dbname).order_by(self.dbname.id).all()
        # print(info)
        res = [dict(model) for model in info]
        sessions.close()
        return {'data': res, 'len': len(res)}

    # 某条数据(id)
    def getOne(self, id=0):
        sessions = DBSession()
        info = sessions.query(self.dbname).filter(self.dbname.id == id).first()
        sessions.close()
        if info is None:
            return info
        res = dict(info)
        
        # res['src']='http://127.0.0.1:5000/users/static/avatar/jinlu.jpg'
        return res

    # 删除某条数据
    def deleteOne(self, id):
        sessions = DBSession()
        sessions.query(self.dbname).filter(self.dbname.id == id).delete()
        sessions.commit()
        sessions.close()

    # 删除多条数据
    def deleteMany(self, idarray):
        for id in idarray:
            self.deleteOne(id)

    # 上传
    def upLoad(self, data):
        sessions = DBSession()
        new = self.dbname(data)
        sessions.add(new)
        sessions.flush()
        id = new.id
        # if data['files'][0]['title'][-3:]=='png' or data['files'][0]['title'][-3:]=='png'

        # print(data['files'][0]['title'])
        # local = time.strftime('%Y-%m-%d-%H_%M_%S')
        # picturesBase64 = data['files'][0]
        # filesBase64 = data['files'][1:]
        # pic_name = str(local)+picturesBase64['title']
        # save_Filebase64(self.bpname,base64.b64decode(handlebase64(picturesBase64['src'])),os.path.join(str(id),pic_name))
        # new.pic=pic_name
        # files_name=[]
        # for file in filesBase64:
        #     file_name = str(local)+file['title']
        #     save_Filebase64(self.bpname, base64.b64decode(handlebase64(picturesBase64['src'])),
        #               os.path.join(str(id), file_name))
        #     files_name.append(file_name)
        # new.file=files_name
        sessions.commit()
        sessions.close()
        return {'id': id}

    # 修改
    def modify(self, data, id):
        
        sessions = DBSession()
        sessions.query(self.dbname).filter(self.dbname.id == id).update(data)
        sessions.commit()
        sessions.close()
        return {'id': id}
