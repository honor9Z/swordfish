class Foo(object):
    pass

class Bar(Foo):
    pass

obj = Foo()

# isinstance用于判断，对象是否是指定类的实例 （错误的）
# isinstance用于判断，对象是否是指定类或其派生类的实例
print(isinstance(obj,Foo))
print(isinstance(obj,Bar))


print(type(obj) == Bar)
print(type(obj) == Foo)








# 对象，判断是否是某个类型？ type，isinstance

from django.forms.models import ModelChoiceField
from django.forms.models import ModelMultipleChoiceField

isinstance(obj,ModelChoiceField)







