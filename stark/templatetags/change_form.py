from django.template import Library
from django.urls import reverse
from stark.service.v1 import site

register = Library()
# 自定义标签
@register.inclusion_tag('stark/form.html')
def new_form(model_form_obj):
    new_form = []
    for bfield in model_form_obj:#model_form_obj是每一条记录
        temp = {'is_popup': False, 'item': bfield}
        # bfield.field是ModelForm读取对应的models.类，然后根据每一个数据库字段，生成Form的字段
        from django.forms.boundfield import BoundField
        from django.db.models.query import QuerySet
        from django.forms.models import ModelChoiceField
        if isinstance(bfield.field, ModelChoiceField):#是单选和多选————>外键字段
            related_class_name = bfield.field.queryset.model#得到字段的field
            if related_class_name in site._registry:#已注册
                app_model_name = related_class_name._meta.app_label, related_class_name._meta.model_name
                base_url = reverse("stark:%s_%s_add" % app_model_name)#应用名_类名_add，反向生成url
                #bfield.auto_id是内置方法，得到该input框的id
                popurl = "%s?_popbackid=%s" % (base_url, bfield.auto_id)#带有回调参数的url
                temp['is_popup'] = True
                temp['popup_url'] = popurl
        new_form.append(temp)#{'is_popup': True, 'item': bfield,'popup_url':popurl}
    return {'new_form':new_form}