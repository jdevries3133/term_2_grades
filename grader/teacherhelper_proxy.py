"""Proxy module to ensure that the helper object is a singleton throughout
this module. This is critical so that overrides applied in __main__ propagate
throughout the module and are not wiped out every time a new helper is created
with `Helper.read_cache()`"""

from teacherhelper import Helper

helper = Helper.read_cache()
