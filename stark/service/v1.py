from django.shortcuts import HttpResponse,render,redirect
from django.urls import reverse
from django.conf.urls import url, include
from django.utils.safestring import mark_safe
class StarkConfig(object):
    """
        用于为每个类（即每张表）生成url对应关系，并处理用户请求
    """
    def __init__(self,model_class,site):
        self.model_class=model_class
        self.site=site

#########################定制默认每个tr都会拥有的td##########################################
    def checkbox(self,obj=None,is_header=False):
        if is_header:
            return '选择'
        return mark_safe('<input type="checkbox" name="pk" value="%s" >' %(obj.id,))
    def edit(self,obj=None,is_header=False):
        if is_header:
            return '编辑操作'
        return mark_safe('<a href="%s">编辑</a>' %(self.get_change_url(obj.id),))
    def delete(self,obj=None,is_header=False):
        if is_header:
            return '删除操作'
        return mark_safe('<a href="%s">删除</a>'%(self.get_delete_url(obj.id),) )
    list_display=[]

    def get_list_display(self):
        data=[]
        if self.list_display:#派生类中定义的要显示的字段
            data.extend(self.list_display)#加入到data中
            data.append(StarkConfig.edit)#加入编辑td
            data.append(StarkConfig.delete)#加入删除td
            data.insert(0,StarkConfig.checkbox)#在最前面插一个td
        return data

######### 是否显示add按钮
    show_add_btn = True  # 默认显示
    def get_show_add_btn(self):
        return self.show_add_btn

##################################访问相应网址时需要作数据处理的视图函数##########################

    def changelist_view(self, request,*args, **kwargs):  # 默认列表页面
        # 列表页面要显示的表头
        head_list = []
        for field_name in self.get_list_display():
            if isinstance(field_name, str):  # 'id','name'...
                verbose_name = self.model_class._meta.get_field(field_name).verbose_name
            else:  # checkbox,edit...
                verbose_name = field_name(self, is_header=True)  # 去派生类中执行
            head_list.append(verbose_name)
        # tbody内容
        data_list = self.model_class.objects.all()
        new_data_list = []
        for row in data_list:
            # row是 每个对象

            temp = []
            for field_name in self.get_list_display():
                if isinstance(field_name, str):
                    val = getattr(row, field_name)  # # 2 alex2
                else:
                    val = field_name(self, row)  # 去派生类中执行
                temp.append(val)
            new_data_list.append(temp)

        return render(request, 'stark/changelist.html', {'data_list': new_data_list,  # tbody
                                                         'head_list': head_list,  # thead
                                                         'add_url': self.get_add_url(),  # 方法调用add按钮的url
                                                         'show_add_btn': self.get_show_add_btn()  # 是否显示add按钮
                                                         })

    model_form_class = None#一劳永逸的modelform
    def get_model_form_class(self):
        if self.model_form_class:
            return self.model_form_class
        from django.forms import ModelForm
        # class TestModelForm(ModelForm):
        #     class Meta:
        #         model = self.model_class
        #         fields = "__all__"
        # type创建TestModelForm类
        meta = type('Meta', (object,), {'model': self.model_class, 'fields': '__all__'})
        TestModelForm = type('TestModelForm', (ModelForm,), {'Meta': meta})
        return TestModelForm


    def add_view(self, request, *args, **kwargs):
        # 添加页面
        model_form_class = self.get_model_form_class()#根据modelform生成input
        if request.method == 'GET':
            form = model_form_class()
            return render(request, 'stark/add_view.html', {'form': form})
        else:
            form = model_form_class(request.POST)
            if form.is_valid():
                form.save()
                return redirect(self.get_list_url())
            return render(request, 'stark/add_view.html', {'form': form})

    def delete_view(self, request, nid,*args, **kwargs):
        self.model_class.objects.filter(pk=nid).delete()
        return redirect(self.get_list_url())

    def change_view(self, request, nid,*args, **kwargs):
        # self.model_class.objects.filter(id=nid)
        print('==========',nid)
        obj = self.model_class.objects.filter(id=nid).first()
        print('===============',obj)
        if not obj:
            return redirect(self.get_list_url())

        model_form_class = self.get_model_form_class()
        # GET,显示标签+默认值
        if request.method == 'GET':
            form = model_form_class(instance=obj)
            return render(request, 'stark/change_view.html', {'form': form})
        else:
            form = model_form_class(instance=obj, data=request.POST)
            if form.is_valid():
                form.save()
                return redirect(self.get_list_url())
            return render(request, 'stark/change_view.html', {'form': form})

#####################################反向生成url#############################
    def get_change_url(self, nid):
        print('---------', nid)
        name = 'stark:%s_%s_change' % (self.model_class._meta.app_label, self.model_class._meta.model_name)
        edit_url = reverse(name, args=(nid,))
        return edit_url

    def get_list_url(self):
        name = 'stark:%s_%s_changelist' % (self.model_class._meta.app_label, self.model_class._meta.model_name)
        edit_url = reverse(name)
        return edit_url

    def get_add_url(self):
        name = 'stark:%s_%s_add' % (self.model_class._meta.app_label, self.model_class._meta.model_name)
        edit_url = reverse(name)
        return edit_url

    def get_delete_url(self, nid):
        name = 'stark:%s_%s_delete' % (self.model_class._meta.app_label, self.model_class._meta.model_name)
        edit_url = reverse(name, args=(nid,))
        return edit_url
##########################################################################################################
    def get_urls(self):#第五步
        app_model_name=(self.model_class._meta.app_label,self.model_class._meta.model_name,)#元祖（app名，表名）
        url_patterns=[
            url(r'^$',self.changelist_view,name='%s_%s_changelist'%app_model_name),
            url(r'^add/$',self.add_view,name='%s_%s_add'%app_model_name),
            url(r'^(\d+)/delete/$',self.delete_view,name='%s_%s_delete'%app_model_name),
            url(r'^(\d+)/change/$',self.change_view,name='%s_%s_change'%app_model_name),
        ]
        url_patterns.extend(self.extra_url())#除增删改查外，想要自定义的新增的url
        return url_patterns#最后就得到了需要用到的一堆url
    def extra_url(self):
        return []
#############################################################################################
    @property
    def urls(self):#第四步
        return self.get_urls()


########传说中类与类之间的分界线############################################################################
class StarkSite(object):
    '''
    单例模式创建的对象的类,是一个容器，用于放置处理请求对应关系
    {model.UserInfo:StarkConfig(model.UserInfo,self)}
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