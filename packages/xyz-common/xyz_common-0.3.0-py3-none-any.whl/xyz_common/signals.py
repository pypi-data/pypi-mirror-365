# -*- coding:utf-8 -*- 
# author = 'denishuang'
from __future__ import unicode_literals

from django.dispatch import Signal

to_save_version = Signal()
to_add_event = Signal()
new_version_posted = Signal()
to_clear_expired_data = Signal()