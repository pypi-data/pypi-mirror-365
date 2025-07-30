# coding: utf-8
import django


if django.VERSION < (3, 2):
    default_app_config = __name__ + '.apps.AioClientConfig'
