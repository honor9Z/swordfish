print('我是stark')
from django.shortcuts import HttpResponse,render,redirect
from django.utils.safestring import mark_safe
from django.conf.urls import url
from stark.service import v1
from crm import models
from . permissions.base import BasePermission
# class BasePermission(object):
#     def get_show_add_btn(self):
#         code_list = self.request.permission_code_list
#         if "add" in code_list:
#             return True
#
#     def get_edit_link(self):
#         code_list = self.request.permission_code_list
#         if "edit" in code_list:
#             return super(BasePermission,self).get_edit_link()
#         else:
#             return []
#
#     def get_list_display(self):
#         code_list = self.request.permission_code_list
#         data = []
#         if self.list_display:
#             data.extend(self.list_display)
#             if 'del' in code_list:
#                 data.append(v1.StarkConfig.delete)
#             data.insert(0, v1.StarkConfig.checkbox)
#         return data


class SchoolConfig(BasePermission,v1.StarkConfig):
    list_display = ['id','title']
    def get_list_display(self):
        data = []
        if self.list_display:  # 派生类中定义的要显示的字段
            data.extend(self.list_display)  # 加入到data中
            data.append(v1.StarkConfig.delete)  # 加入删除td
            data.insert(0, v1.StarkConfig.checkbox)  # 在最前面插一个td
        return data
    edit_link = ['title']
v1.site.register(models.School,SchoolConfig)


class CourseConfig(BasePermission,v1.StarkConfig):
    list_display = ['id','name']
    def get_list_display(self):
        data = []
        if self.list_display:  # 派生类中定义的要显示的字段
            data.extend(self.list_display)  # 加入到data中
            data.append(v1.StarkConfig.delete)  # 加入删除td
            data.insert(0, v1.StarkConfig.checkbox)  # 在最前面插一个td
        return data
    edit_link = ['name']
v1.site.register(models.Course,CourseConfig)


class DepartmentConfig(BasePermission,v1.StarkConfig):
    list_display = ['id','title','code']
    def get_list_display(self):
        data = []
        if self.list_display:  # 派生类中定义的要显示的字段
            data.extend(self.list_display)  # 加入到data中
            data.append(v1.StarkConfig.delete)  # 加入删除td
            data.insert(0, v1.StarkConfig.checkbox)  # 在最前面插一个td
        return data
    edit_link=['title']
v1.site.register(models.Department,DepartmentConfig)


class UserInfoConfig(BasePermission,v1.StarkConfig):
    show_search_form = True  # 搜索框
    search_fields = ['name__contains', 'email__contains']  # 模糊搜索

    show_actions = True  # 批量操作框
    # 批量删除
    def multi_del(self, request):
        pk_list = request.POST.getlist('pk')  # 得到所有的勾选的项
        self.model_class.objects.filter(id__in=pk_list).delete()
        return HttpResponse('删除成功')
        # return redirect("http://www.baidu.com")

    multi_del.short_desc = "批量删除"  # 给函数内部加一个字段
    actions = [multi_del]  # 给actions加入定制的功能

    def display_depart(self,obj=None,is_header=False):
        if is_header:
            return '部门'
        return obj.depart.title#对象.字段

    list_display = ['id','name','username','email',display_depart]

    def get_list_display(self):
        data = []
        if self.list_display:  # 派生类中定义的要显示的字段
            data.extend(self.list_display)  # 加入到data中
            data.append(v1.StarkConfig.delete)  # 加入删除td
            data.insert(0, v1.StarkConfig.checkbox)  # 在最前面插一个td
        return data
    edit_link = ['name']
    #条件筛选
    show_comb_filter = True  # 搜索框
    comb_filter = [
        #  FilterOption('字段', 是否多选, 条件, 是否是choice),
        v1.FilterOption('depart',text_func_name=lambda obj: str(obj),val_func_name=lambda obj: obj.code,),#, condition={'id__gt': 3}
    ]
v1.site.register(models.UserInfo,UserInfoConfig)


class ClassListConfig(BasePermission,v1.StarkConfig):
    def course_semester(self,obj=None,is_header=False):
        if is_header:
            return '班级'
        return "%s(%s期)" %(obj.course.name,obj.semester,)

    def num(self,obj=None,is_header=False):
        if is_header:
            return '人数'

        student_count=obj.student_set.count()
        return student_count

    list_display = ['school',course_semester,num,'start_date']
    def get_list_display(self):
        data = []
        if self.list_display:  # 派生类中定义的要显示的字段
            data.extend(self.list_display)  # 加入到data中
            data.append(v1.StarkConfig.delete)  # 加入删除td
            data.insert(0, v1.StarkConfig.checkbox)  # 在最前面插一个td
        return data
    edit_link = [course_semester,]

    show_comb_filter = True  # 搜索框
    comb_filter = [
        #  FilterOption('字段', 是否多选, 条件, 是否是choice),
        v1.FilterOption('school'),
        v1.FilterOption('course' ),
    ]
v1.site.register(models.ClassList,ClassListConfig)





class ConsultRecordConfig(BasePermission,v1.StarkConfig):
    list_display = ['customer','consultant','date']
    def get_list_display(self):
        data = []
        if self.list_display:  # 派生类中定义的要显示的字段
            data.extend(self.list_display)  # 加入到data中
            data.append(v1.StarkConfig.delete)  # 加入删除td
            data.insert(0, v1.StarkConfig.checkbox)  # 在最前面插一个td
        return data

    comb_filter = [
        v1.FilterOption('customer')
    ]

    def changelist_view(self,request,*args,**kwargs):
        customer = request.GET.get('customer')
        # session中获取当前用户ID
        current_login_user_id = 1
        ct = models.Customer.objects.filter(consultant=current_login_user_id,id=customer).count()
        if not ct:
            return HttpResponse('别抢客户呀...')

        return super(ConsultRecordConfig,self).changelist_view(request,*args,**kwargs)
v1.site.register(models.ConsultRecord,ConsultRecordConfig)

#  老师上课记录
class CourseRecordConfig(BasePermission,v1.StarkConfig):
    def extra_url(self):
        app_model_name=(self.model_class._meta.app_label,self.model_class._meta.model_name)
        url_list=[
            url(r'^(\d+)/score_list/$',self.wrap(self.score_list),name='%s_%s_score_list'%app_model_name),

        ]
        return url_list
    #学生作业情况
    def score_list(self,request,record_id):
        if request.method == "GET":
            from django.forms import Form,fields,widgets
            study_record_list=models.StudyRecord.objects.filter(course_record_id=record_id)
            data=[]
            for obj in study_record_list:
                #Form组件
                # class TempForm(Form):
                #     score = fields.ChoiceField(choices=models.StudyRecord.score_choices)
                #     homework_note = fields.CharField(widget=widgets.Textarea())
                TempForm = type('TempForm', (Form,), {
                    'score_%s' % obj.pk: fields.ChoiceField(choices=models.StudyRecord.score_choices),
                    'homework_note_%s' % obj.pk: fields.CharField(widget=widgets.Textarea(attrs={'style': 'width: 200px;height: 80px'}))
                })
                data.append({'obj': obj, 'form': TempForm(
                    initial={'score_%s' % obj.pk: obj.score, 'homework_note_%s' % obj.pk: obj.homework_note})})
            return render(request, 'score_list.html',{'data': data})
        else:
            data_dict={}
            for key,value in request.POST.items():
                if key == "csrfmiddlewaretoken":
                    continue
                name,nid =key.rsplit('_',1)
                if nid in data_dict:
                    data_dict[nid][name]=value
                else:
                    data_dict[nid]={name:value}
            for nid,update_dict in data_dict.items():
                models.StudyRecord.objects.filter(id=nid).update(**update_dict)
            return redirect(request.path_info)

    def attendance(self,obj=None,is_header=False):
        if is_header:
            return '考勤'
        return mark_safe("<a href='/stark/crm/studyrecord/?course_record=%s'>考勤管理</a>" %obj.pk)

    def display_score_list(self,obj=None,is_header=False):
        if is_header:
            return '成绩录入'
        from django.urls import reverse
        rurl = reverse("stark:crm_courserecord_score_list",args=(obj.pk,))
        return mark_safe("<a href='%s'>成绩录入</a>" %rurl)

    list_display = ['class_obj','day_num',attendance,display_score_list]

    def multi_init(self,request):
        """
        自定义执行批量初始化方法
        """
        # 勾选的上课记录ID列表
        pk_list = request.POST.getlist('pk')

        # 上课记录对象
        record_list = models.CourseRecord.objects.filter(id__in=pk_list)
        for record in record_list:
            # day1,day2,day3
            # record.class_obj # 关联的班级
            exists = models.StudyRecord.objects.filter(course_record=record).exists()
            if exists:
                continue

            student_list = models.Student.objects.filter(class_list=record.class_obj)
            bulk_list = []
            for student in student_list:
                # 为每一个学生创建学习记录
                bulk_list.append(models.StudyRecord(student=student,course_record=record))
            models.StudyRecord.objects.bulk_create(bulk_list)
        return redirect('http://www.baidu.com')

    multi_init.short_desc = "学生初始化"
    actions = [multi_init,]
    show_actions = True
v1.site.register(models.CourseRecord,CourseRecordConfig)


#  学生学习记录
class StudyRecordConfig(BasePermission,v1.StarkConfig):
    def display_record(self,obj=None,is_header=False):
        if is_header:
            return '出勤情况'
        return obj.get_record_display()

    list_display = ['course_record','student',display_record]

    comb_filter = [
        v1.FilterOption('course_record')
    ]

    def action_checked(self,request):
        pk_list = request.POST.getlist('pk')
        models.StudyRecord.objects.filter(id__in=pk_list).update(record='checked')
        return redirect('/stark/crm/studyrecord/')

    action_checked.short_desc= "已签到"

    def action_vacate(self,request):
        pk_list = request.POST.getlist('pk')
        models.StudyRecord.objects.filter(id__in=pk_list).update(record='vacate')
        return redirect('/stark/crm/studyrecord/')

    action_vacate.short_desc= "请假"

    def action_late(self,request):
        pk_list = request.POST.getlist('pk')
        models.StudyRecord.objects.filter(id__in=pk_list).update(record='late')
        return redirect('/stark/crm/studyrecord/')

    action_late.short_desc= "迟到"

    def action_noshow(self,request):
        pk_list = request.POST.getlist('pk')
        models.StudyRecord.objects.filter(id__in=pk_list).update(record='noshow')
        return redirect('/stark/crm/studyrecord/')
    action_noshow.short_desc= "缺勤"

    def action_leave_early(self,request):
        pk_list = request.POST.getlist('pk')
        models.StudyRecord.objects.filter(id__in=pk_list).update(record='leave_early')
        return redirect('/stark/crm/studyrecord/')

    action_leave_early.short_desc= "早退"

    actions = [action_checked,action_vacate, action_late,action_noshow,action_leave_early]

    show_actions = True

    show_add_btn = False

v1.site.register(models.StudyRecord,StudyRecordConfig)




from crm.congfigs.student import StudentConfig
from crm.congfigs.customer import CustomerConfig

v1.site.register(models.Student,StudentConfig)
v1.site.register(models.Customer,CustomerConfig)

class SaleRankConfig(BasePermission,v1.StarkConfig):
    list_display = ['user','num','weight']
v1.site.register(models.SaleRank)
v1.site.register(models.CustomerDistribution)