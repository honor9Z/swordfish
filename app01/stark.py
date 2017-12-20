print('我是stark')
from django.shortcuts import HttpResponse,render,redirect
from django.utils.safestring import mark_safe
from django.conf.urls import url
from stark.service import v1
from app01 import models
from django.forms import ModelForm
class UserInfoModelForm(ModelForm):
    class Meta:
        model = models.UserInfo
        fields = '__all__'
        error_messages = {
            'name':{
                'required':'用户名不能为空'
            }
        }

class UserinfoConfig(v1.StarkConfig):
    '''
    自己定义的派生类，可以有29种额外的显示方式，效果与admin相同
    '''

    list_display=['id','name','pwd','email']
    def extra_url(self):
        url_list=[
            #除增删改查外，想要新增的url
        ]
        return url_list
    show_add_btn = True
    model_form_class = UserInfoModelForm
    show_search_form = True#搜索框
    search_fields = ['name__contains', 'email__contains']#模糊搜索
    show_actions = True#批量操作框
    #批量删除
    def multi_del(self,request):
        pk_list = request.POST.getlist('pk')#得到所有的勾选的项
        self.model_class.objects.filter(id__in=pk_list).delete()
        return HttpResponse('删除成功')
        # return redirect("http://www.baidu.com")
    multi_del.desc_text = "批量删除"#给函数内部加一个字段

    def multi_init(self,request):
        pk_list = request.POST.getlist('pk')
        #self.model_class.objects.filter(id__in=pk_list).delete()
        # return HttpResponse('删除成功')
        #return redirect("http://www.baidu.com")
    multi_init.desc_text = "初始化"

    actions = [multi_del, multi_init]#给actions加入定制的功能



class HostModelForm(ModelForm):
    class Meta:
        model = models.Host
        fields = ['id','hostname','ip','port']
        error_messages = {
            'hostname':{
                'required':'主机名不能为空',
            },
            'ip':{
                'required': 'IP不能为空',
                'invalid': 'IP格式错误',
            }

        }




class HostConfig(v1.StarkConfig):
    def ip_port(self,obj=None,is_header=False):
        if is_header:
            return '自定义列'
        return "%s:%s" %(obj.ip,obj.port,)

    list_display = ['id','hostname','ip','port',ip_port]
    # get_list_display

    show_add_btn = True
    # get_show_add_btn

    model_form_class = HostModelForm
    # get_model_form_class
    def extra_url(self):
        urls = [
            url('^report/$',self.report_view)
        ]
        return urls

    def report_view(self,request):
        return HttpResponse('自定义报表')

    def delete_view(self,request,nid,*args,**kwargs):
        if request.method == "GET":
            return render(request,'my_delete.html')
        else:
            self.model_class.objects.filter(pk=nid).delete()
            return redirect(self.get_list_url())




#相应的注册
#第二个参数传入自己写的类时，可以拥有自己写的类中的额外的方法
v1.site.register(models.UserInfo,UserinfoConfig)
v1.site.register(models.Role)
v1.site.register(models.Type)
v1.site.register(models.Host,HostConfig)