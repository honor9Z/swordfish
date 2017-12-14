from django.shortcuts import HttpResponse,render
from django.conf.urls import url, include
class StarkConfig(object):
    list_display=[]
    def __init__(self,model_class,site):
        self.model_class=model_class
        self.site=site

    def get_urls(self):#第五步
        app_model_name=(self.model_class._meta.app_label,self.model_class._meta.model_name,)#元祖（app名，表名）
        url_patterns=[
            url(r'^$',self.changelist_view,name='%s_%s_changlist'%app_model_name),
            url(r'^add/$',self.add_view,name='%s_%s_add'%app_model_name),
            url(r'^(\d+)/delete/$',self.delete_view,name='%s_%s_delete'%app_model_name),
            url(r'^(\d+)/change/$',self.change_view,name='%s_%s_change'%app_model_name),
        ]
        return url_patterns
###############访问相应网址时需要作数据处理的视图函数#############
    def changelist_view(self,request):
        #列表页面要显示的表头
        head_list=[]
        for field_name in self.list_display:
            if isinstance(field_name,str):#'id','name'...
                verbose_name = self.model_class._meta.get_field(field_name).verbose_name
            else:#checkbox,edit...
                verbose_name=field_name(self,is_header=True)#去派生类中执行
            head_list.append(verbose_name)
        #tbody内容
        data_list = self.model_class.objects.all()
        new_data_list = []
        for row in data_list:
            # row是 每个对象

            temp = []
            for field_name in self.list_display:
                if isinstance(field_name,str):
                    val = getattr(row,field_name) # # 2 alex2
                else:
                    val = field_name(self,row)#去派生类中执行
                temp.append(val)
            new_data_list.append(temp)

        return render(request,'stark/changelist.html',{'data_list':new_data_list,'head_list':head_list})

    def add_view(self,request):
        return HttpResponse('添加')
    def delete_view(self,nid,request):
        return HttpResponse('删除')
    def change_view(self,nid,request):
        return HttpResponse('修改')

    @property
    def urls(self):#第四步
        return self.get_urls()



class StarkSite(object):
    '''
    单例模式创建的对象的类
    '''
    def __init__(self):
        self._registry = {}

    def register(self,model_class,stark_config_class=None):
        if not stark_config_class:
            #stark_config_class即29，没写那个派生类的时候默认给予StarkConfig
            stark_config_class=StarkConfig
        self._registry[model_class]=stark_config_class(model_class,self)
        #表名：stark_config_class（表名，self）

    def get_urls(self):#第三步，给url
        url_pattern=[]
        for model_class,stark_config_obj in self._registry.items():#去字典里取值
            app_name=model_class._meta.app_label#app名
            model_name=model_class._meta.model_name#表名
            curd_url=url(r'^%s/%s/'%(app_name,model_name),(stark_config_obj.urls,None,None))
            #拼接生成url，需执行stark_config_obj.urls———第四步
            url_pattern.append(curd_url)
        return url_pattern

    @property
    def urls(self):#第二步，要url
        return (self.get_urls(),None,'stark')

site=StarkSite()#第一步，单例模式