# klang-boda

مكتبة Python بسيطة للحصول على لغة الكيبورد الحالية على Windows.

## الاستخدام

```python
#import a main func
from src.__init__ import get_keyboard_language,get_language_name
#get a hex code of lang keyboard
lang_hex = get_keyboard_language()
#convert hex code of lang keyborad to EN lang easy to read
lang_name = get_language_name(lang_hex)
#print final result
print(lang_name)

```
## اصدار البايثون المطلوب 

python >> 3.7+