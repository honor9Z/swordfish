import importlib
from django.conf import settings

def send_message(to,name,subject,body):
    """
    短信、邮件、微信
    :param to: 接受者 
    :param name: 接受者姓名
    :param subject: 主题
    :param body: 内容
    :return: 
    """
    for cls_path in settings.MESSAGE_CLASSES:
        # cls_path是字符串
        module_path,class_name = cls_path.rsplit('.',maxsplit=1)#maxsplit：切的次数
        m = importlib.import_module(module_path)
        obj = getattr(m,class_name)()#反射，由字符串得到类对象
        obj.send(to,name,subject,body,)