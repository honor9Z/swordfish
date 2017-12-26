import copy
import json
from django.shortcuts import HttpResponse,render,redirect
from django.urls import reverse
from django.conf.urls import url, include
from django.utils.safestring import mark_safe
from django.http import QueryDict
from django.db.models import Q

#用于封装筛选条件的配置信息
class FilterOption(object):
    def __init__(self, field_name, multi=False, condition=None, is_choice=False,text_func_name=None, val_func_name=None):
        """
        :param field_name: 字段
        :param multi:  是否多选
        :param condition: 显示数据的筛选条件
        :param is_choice: 是否是choice
        """
        self.field_name = field_name
        self.multi = multi
        self.condition = condition
        self.is_choice = is_choice
        self.text_func_name = text_func_name#组合搜索时，页面上生成显示的文本的函数
        self.val_func_name = val_func_name#组合搜索时，页面上生成的a标签中的值的函数

    def get_queryset(self, _field):
        if self.condition:#是数据的筛选条件
            return _field.rel.to.objects.filter(**self.condition)#拿到筛选后的对象
        return _field.rel.to.objects.all()#默认“全部”按钮被选中，给出所有对象

    def get_choices(self, _field):#是choices
        return _field.choices

#可迭代对象，封装了筛选中的每一行数据。
class FilterRow(object):
    def __init__(self, option, data, request):
        self.option = option
        self.data = data#关联字段所关联的表的所有有关联的数据
        # request.GET
        self.request = request

    def __iter__(self):
        params = copy.deepcopy(self.request.GET)#深拷贝？后面的内容，得到QueryDict
        params._mutable = True#可修改
        current_id = params.get(self.option.field_name)  #params.get（字段），得到的是值
        current_id_list = params.getlist(self.option.field_name)  # [1,2,3]

        if self.option.field_name in params:#地址栏已存在筛选条件
            # del params[self.option.field_name]，先删除
            origin_list = params.pop(self.option.field_name)#删除，并得到删除内容
            url = "{0}?{1}".format(self.request.path_info, params.urlencode())
            yield mark_safe('<a href="{0}">全部</a>'.format(url))#“全部按钮”不被选中
            params.setlist(self.option.field_name, origin_list)#将本身已存在的筛选条件放入params中
        else:
            url = "{0}?{1}".format(self.request.path_info, params.urlencode())#地址栏不存在筛选条件
            yield mark_safe('<a class="active" href="{0}">全部</a>'.format(url))#默认“全部”按钮被选中

        for val in self.data:
            if self.option.is_choice:# ( (1,男),(2,女)  )
                pk, text = str(val[0]), val[1]
            else:#每个val都是对象
                # pk, text = str(val.pk), str(val)
                text = self.option.text_func_name(val) if self.option.text_func_name else str(val)
                pk = str(self.option.val_func_name(val)) if self.option.val_func_name else str(val.pk)
            # 当前URL？option.field_name
            # 当前URL？gender=pk
            #制定url的显示规则：
            # self.request.path_info # http://127.0.0.1:8005/arya/crm/customer/?gender=1&id=2
            # self.request.GET['gender'] = 1 # &id=2gender=1
            if not self.option.multi:
                # 单选
                params[self.option.field_name] = pk#1,2
                url = "{0}?{1}".format(self.request.path_info, params.urlencode())
                if current_id == pk:#当前url筛选条件中的值
                    yield mark_safe("<a class='active' href='{0}'>{1}</a>".format(url, text))#该筛选按钮被选中
                else:
                    yield mark_safe("<a href='{0}'>{1}</a>".format(url, text))#其余按钮，没被选中
            else:
                # 多选 current_id_list = ["1","2"]
                _params = copy.deepcopy(params)
                id_list = _params.getlist(self.option.field_name)#["1","2","3","4"]

                if pk in current_id_list:#值已存在，表示该按钮已被选中
                    id_list.remove(pk)#将该值从id_list中去除
                    _params.setlist(self.option.field_name, id_list)#["2","3","4"]
                    url = "{0}?{1}".format(self.request.path_info, _params.urlencode())
                    #该按钮被选中，但其a标签的href中跳转的链接即当前url去除本身按钮id的状态，即该按钮，被再次点击时，就会恢复未选中状态
                    yield mark_safe("<a class='active' href='{0}'>{1}</a>".format(url, text))

                else:#值未存在
                    id_list.append(pk)
                    # params中被重新赋值
                    _params.setlist(self.option.field_name, id_list)
                    # 创建URL，赋予其被点时，使其产生被选中
                    url = "{0}?{1}".format(self.request.path_info, _params.urlencode())
                    yield mark_safe("<a href='{0}'>{1}</a>".format(url, text))





class ChangeList(object):
    '''
    很牛逼的一个类，封装了所有视图函数想要往前端传的内容
    功能：使视图函数中的代码变的简洁
    '''
    def __init__(self,config,queryset):
        self.config=config#stark.py中写了派生类的话就是那个类，没写的话默认就是StarkConfig
        self.list_display=config.get_list_display()
        self.edit_link = config.get_edit_link()
        self.model_class=config.model_class#数据库的表
        self.request=config.request#StarkConfig中默认是None，不过程序运行后就会有
        self.show_add_btn=config.get_show_add_btn()
        # 搜索框
        self.show_search_form = config.get_show_search_form()
        self.search_form_val = config.request.GET.get(config.search_key, '')#搜索关键字“_q”,首次访问网页默认是空
        # 批量操作
        self.actions=config.get_actions()#得到派生类中写的actions的内容[]
        self.show_actions=config.get_show_actions()#操作框
        #组合搜索
        self.show_comb_filter=config.get_show_comb_filter()
        self.comb_filter=config.get_comb_filter()

        from utils.pager import Pagination
        #分页器
        current_page = self.request.GET.get('page', 1)#得到传入的page，没有默认为第一页
        total_count = queryset.count()#要显示的数据的量，queryset在视图函数中有数据库操作的赋值
        page_obj = Pagination(current_page, total_count, self.request.path_info, self.request.GET, per_page_count=5)
                            #当前页         数据量        当前url不带问号         ？后面的条件内容      设定的每页显示的数据量条数
        self.page_obj = page_obj#得到最终生成的分页器对象

        self.data_list = queryset[page_obj.start:page_obj.end]#得到分页后的数据，用于页面展示

    #批量操作
    def modify_actions(self):
        result = []#批量操作内容，默认为空，去派生类中定义
        for func in self.actions:#self.actions=config.get_actions()，默认为空
            temp = {'name':func.__name__,'text':func.short_desc}#name是函数名，text是自加的描述
            result.append(temp)
        return result

    def add_url(self):#添加操作的url
        query_str = self.request.GET.urlencode()
        if query_str:
            # 重新构造
            params = QueryDict(mutable=True)
            params[self.config._query_param_key] = query_str
            return self.config.get_add_url()+'?'+params.urlencode()
        return self.config.get_add_url()

    def head_list(self):
        #构造表头
        result = []
        # [checkbox,'id','name',edit,del]
        for field_name in self.list_display:
            if isinstance(field_name, str):
                # 根据类和字段名称，获取字段对象的verbose_name
                verbose_name = self.model_class._meta.get_field(field_name).verbose_name
            else:
                verbose_name = field_name(self.config, is_header=True)# 去派生类中执行
            result.append(verbose_name)
        return result

    def body_list(self):
        # 处理表中的数据
        data_list = self.data_list#self.data_list = queryset[page_obj.start:page_obj.end]
        new_data_list = []
        for row in data_list:
            # row是 每一条数据对象UserInfo(id=2,name='alex2',age=181)
            temp = []
            for field_name in self.list_display:
                if isinstance(field_name,str):#派生类中定义的显示字段
                    val = getattr(row,field_name)
                else:#每个td都拥有的功能，checkbox、edit、delete、
                    val = field_name(self.config,row)
                # 用于定制编辑列
                if field_name in self.edit_link:
                    val = self.edit_link_tag(row.pk, val)
                temp.append(val)
            new_data_list.append(temp)
        return new_data_list

    def gen_comb_filter(self):
        #生成器函数
        """
        [
             FilterRow(((1,'男'),(2,'女'),)),
             FilterRow([obj,obj,obj,obj ]),
             FilterRow([obj,obj,obj,obj ]),
        ]
        """
        '''
                comb_filter = [
                v1.FilterOption('gender', is_choice=True),#关键字传参，代表是choice
                v1.FilterOption('depart'),#, condition={'id__gt': 3}
                v1.FilterOption('roles', True),#True传入，代表是多选
            ]
                '''
        from django.db.models import ForeignKey,ManyToManyField
        for option in self.comb_filter:
            _field = self.model_class._meta.get_field(option.field_name)#字段
            if isinstance(_field,ForeignKey):
                # 获取当前字段depart，关联的表 Department表并获取其所有数据
                # print(field_name,_field.rel.to.objects.all())
                row = FilterRow(option, option.get_queryset(_field), self.request)
            elif isinstance(_field,ManyToManyField):
                # print(field_name, _field.rel.to.objects.all())
                # data_list.append(  FilterRow(_field.rel.to.objects.all()) )
                row = FilterRow(option,option.get_queryset(_field), self.request)

            else:
                # print(field_name,_field.choices)
                # data_list.append(  FilterRow(_field.choices) )
                row = FilterRow(option,option.get_choices(_field),self.request)
            # 可迭代对象，迭代详细在FilterRow的__iter__中
            yield row

    def edit_link_tag(self,pk,text):
        query_str = self.request.GET.urlencode()  # page=2&nid=1
        params = QueryDict(mutable=True)
        params[self.config._query_param_key] = query_str
        return mark_safe('<a href="%s?%s">%s</a>' % (self.config.get_change_url(pk), params.urlencode(),text,))  # /stark/app01/userinfo/







class StarkConfig(object):
    """
        用于为每个类（即每张表）生成url对应关系，并处理用户请求的基类
    """
    def __init__(self,model_class,site):
        self.model_class=model_class
        self.site=site
        self.request=None
        self._query_param_key='_listfilter'#？后面的条件内容
        self.search_key='_q'#搜索关键字

#####################################定制功能######################################
#########1 默认每个tr都会拥有的td
    def checkbox(self,obj=None,is_header=False):
        if is_header:
            return '选择'
        return mark_safe('<input type="checkbox" name="pk" value="%s" >' %(obj.id,))
    def edit(self,obj=None,is_header=False):
        if is_header:
            return '编辑操作'
        #url地址栏的搜索条件
        query_str=self.request.GET.urlencode()
        if query_str:
            #重新构造<button class="btn btn-primary"></button>
            params=QueryDict(mutable=True)
            params[self._query_param_key]=query_str
            return mark_safe('<button class="btn btn-primary"><a href="%s?%s" style="color:white;">编辑</a></button>' %(self.get_change_url(obj.id),params.urlencode(),))
        return mark_safe('<button class="btn btn-primary"><a href="%s" style="color:white;">编辑</a></button>' %(self.get_change_url(obj.id),))
    def delete(self,obj=None,is_header=False):
        if is_header:
            return '删除操作'
        query_str = self.request.GET.urlencode()
        if query_str:
            # 重新构造
            params = QueryDict(mutable=True)
            params[self._query_param_key] = query_str
            return mark_safe('<button class="btn btn-danger"><a href="%s?%s" style="color:white;">删除</a></button>' % (self.get_delete_url(obj.id), params.urlencode(),))

        return mark_safe('<button class="btn btn-danger"><a href="%s" style="color:white;">删除</a></button>'%(self.get_delete_url(obj.id),) )

    list_display=[]
    #得到派生类中自定义的list_display
    def get_list_display(self):
        data=[]
        if self.list_display:#派生类中定义的要显示的字段
            data.extend(self.list_display)#加入到data中
            data.append(StarkConfig.edit)#加入编辑td
            data.append(StarkConfig.delete)#加入删除td
            data.insert(0,StarkConfig.checkbox)#在最前面插一个td
        return data

    edit_link=[]
    def get_edit_link(self):
        result=[]
        if self.edit_link:
            result.extend(self.edit_link)
        return result


######### 2是否显示add按钮
    show_add_btn = True  # 默认显示
    def get_show_add_btn(self):
        return self.show_add_btn

#########3 关键字搜索
    show_search_form = False#默认不显示
    def get_show_search_form(self):
        return self.show_search_form
    search_fields = []#关键字默认为空
    def get_search_fields(self):
        result = []
        if self.search_fields:
            result.extend(self.search_fields)#派生类中自定义的关键字
        return result

    def get_search_condition(self):
        key_word = self.request.GET.get(self.search_key)#'_q'
        search_fields = self.get_search_fields()#关键字
        condition = Q()#创建Q对象用于与或
        condition.connector = 'or'#搜索条件之间用或连接
        if key_word and self.get_show_search_form():
            for field_name in search_fields:
                condition.children.append((field_name, key_word))
        return condition
#############4 actions
    show_actions = False#默认不显示
    def get_show_actions(self):
        return self.show_actions

    actions = []#默认批量操作内容为空
    def get_actions(self):
        result = []
        if self.actions:
            result.extend(self.actions)#加入派生类中自定制的批量操作
        return result


#############5 组合搜索
    show_comb_filter = False
    def get_show_comb_filter(self):
        return self.show_comb_filter

    comb_filter=[]#默认为空
    def get_comb_filter(self):
        result=[]
        if self.comb_filter:
            result.extend(self.comb_filter)#得到派生类中的条件删选
        return result







##################################访问相应网址时需要作数据处理的视图函数##########################
    # 默认列表页面
    def changelist_view(self, request,*args, **kwargs):
        #分页，已改写到类中
        # from utils.pager import Pagination
        # current_page=request.GET.get('page',1)
        # total_count=self.model_class.objects.all().count()
        # page_obj=Pagination(current_page,total_count,request.path_info,request.GET,per_page_count=4)

        if request.method=='GET':
            comb_condition = {}#筛选条件默认为空
            option_list = self.get_comb_filter()#拿到派生类中定制的筛选条件
            for key in request.GET.keys():#？后面的键
                value_list = request.GET.getlist(key)#拿到键对应的值[1,2,3]
                flag = False
                for option in option_list:#option是每一个删选条件
                    if option.field_name == key:#该条件已存在于地址栏
                        flag = True
                        break
                if flag:
                    #comb_condition = {"id__in":[1,2,3].......}
                    comb_condition["%s__in" % key] = value_list


            # 带搜索条件的数据，没有搜索条件的话就是全部数据。有筛选条件的话，还得处理成筛选后的数据
            queryset=self.model_class.objects.filter(self.get_search_condition()).filter(**comb_condition).distinct()

            the_list=ChangeList(self,queryset)#封装好要向前端传的值
            return render(request, 'stark/changelist.html', {'the_list':the_list})
        elif request.method=='POST' and self.get_show_actions():#批量操作
            func_name_str = request.POST.get('list_action')#前端传的操作name
            action_func = getattr(self, func_name_str)
            ret = action_func(request)
            if ret:
                return ret

    # 一劳永逸的modelform
    model_form_class = None
    def get_model_form_class(self):
        if self.model_form_class:
            return self.model_form_class
        from django.forms import ModelForm
        # class TestModelForm(ModelForm):
        #     class Meta:
        #         model = self.model_class
        #         fields = "__all__"
        #
        #         error_messages = {
        #             "__all__":{
        #
        #                   },
        #         'email': {
        #         'required': '',
        #         'invalid': '邮箱格式错误..',
        #         }
        #         }
        # type创建TestModelForm类
        meta = type('Meta', (object,), {'model': self.model_class, 'fields': '__all__'})
        TestModelForm = type('TestModelForm', (ModelForm,), {'Meta': meta})
        return TestModelForm

    #增
    def add_view(self, request, *args, **kwargs):
        # 添加页面
        model_form_class = self.get_model_form_class()#根据modelform生成input
        _popbackid = request.GET.get('_popbackid')#临时需要添加的外键字段所对应的输入框的id
        if request.method == 'GET':
            form = model_form_class()
        else:
            form = model_form_class(request.POST)
            if form.is_valid():
                new_obj=form.save()
                if _popbackid:
                    # 判断是否是来源于popup请求
                    # render一个页面，写自执行函数
                    # popUp('/stark/crm/userinfo/add/?_popbackid=id_consultant&model_name=customer&related_name=consultant')
                    from django.db.models.fields.reverse_related import ManyToOneRel, ManyToManyRel
                    result = {'status': False, 'id': None, 'text': None, 'popbackid': _popbackid}

                    model_name = request.GET.get('model_name')  # customer
                    related_name = request.GET.get('related_name')  # consultant, "None"
                    for related_object in new_obj._meta.related_objects:
                        _model_name = related_object.field.model._meta.model_name
                        _related_name = related_object.related_name
                        if (type(related_object) == ManyToOneRel):
                            _field_name = related_object.field_name
                        else:
                            _field_name = 'pk'
                        _limit_choices_to = related_object.limit_choices_to
                        if model_name == _model_name and related_name == str(_related_name):
                            is_exists = self.model_class.objects.filter(**_limit_choices_to, pk=new_obj.pk).exists()
                            if is_exists:
                                # 如果新创建的用户时，销售部的人，页面才增加
                                # 分门别类做判断：
                                result['status'] = True
                                result['text'] = str(new_obj)
                                result['id'] = getattr(new_obj, _field_name)
                                return render(request, 'stark/popup_response.html',
                                              {'json_result': json.dumps(result, ensure_ascii=False)})
                    return render(request, 'stark/popup_response.html',
                                  {'json_result': json.dumps(result, ensure_ascii=False)})
                else:
                    list_query_str = request.GET.get(self._query_param_key)
                    list_url = '%s?%s' % (self.get_list_url(), list_query_str,)

                    return redirect(list_url)
                    # return redirect(self.get_list_url())
        return render(request, 'stark/add_view.html', {'form': form, 'config': self})


    #删
    def delete_view(self, request, nid,*args, **kwargs):
        self.model_class.objects.filter(pk=nid).delete()
        list_query_str = request.GET.get(self._query_param_key)
        list_url = '%s?%s' % (self.get_list_url(), list_query_str,)
        return redirect(list_url)
    #改
    def change_view(self, request, nid,*args, **kwargs):
        # self.model_class.objects.filter(id=nid)
        obj = self.model_class.objects.filter(pk=nid).first()
        print(obj)
        if not obj:
            return redirect(self.get_list_url())
        model_form_class = self.get_model_form_class()
        _popbackid = request.GET.get('_popbackid')#临时需要添加的外键字段所对应的输入框的id
        # GET,显示标签+默认值
        if request.method == 'GET':
            form = model_form_class(instance=obj)
            return render(request, 'stark/change_view.html', {'form': form,'config': self})
        else:
            form = model_form_class(instance=obj, data=request.POST)
            if form.is_valid():
                form.save()
                list_query_str=request.GET.get(self._query_param_key)
                list_url='%s?%s'%(self.get_list_url(),list_query_str,)

                return redirect(list_url)
            return render(request, 'stark/change_view.html', {'form': form})



############################反向生成url##########################################
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
    #装饰器，为了传参数request
    def wrap(self,view_func):
        def inner(request,*args,**kwargs):
            self.request=request
            return view_func(request,*args,**kwargs)
        return inner

    def get_urls(self):#第五步
        app_model_name=(self.model_class._meta.app_label,self.model_class._meta.model_name,)#元祖（app名，表名）
        url_patterns=[
            url(r'^$',self.wrap(self.changelist_view),name='%s_%s_changelist'%app_model_name),
            url(r'^add/$',self.wrap(self.add_view),name='%s_%s_add'%app_model_name),
            url(r'^(\d+)/delete/$',self.wrap(self.delete_view),name='%s_%s_delete'%app_model_name),
            url(r'^(\d+)/change/$',self.wrap(self.change_view),name='%s_%s_change'%app_model_name),
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