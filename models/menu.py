# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

#########################################################################
## Customize your APP title, subtitle and menus here
#########################################################################

response.logo = A(B(SPAN('3',_class="flip"),SPAN('Store'),'3'),XML('&trade;&nbsp;'),
                  _class="navbar-brand",_href=URL('default','index'))
response.title = request.application.replace('_',' ').title()
response.subtitle = ''

## read more at http://dev.w3.org/html5/markup/meta.name.html
response.meta.author = 'Your Name <you@example.com>'
response.meta.description = 'a cool new app'
response.meta.keywords = 'web2py, python, framework'
response.meta.generator = 'Web2py Web Framework'

## your http://google.com/analytics id
response.google_analytics_id = None

response.menu = []
if auth.user:
    response.menu.append(('My Orders',None,URL('default','my_orders')))
    if auth.user.id==1 and not 'manager' in auth.user_groups.values():
        auth.add_membership(auth.add_group('manager'))
    if 'manager' in auth.user_groups.values():
        response.menu.append(('Manage Products',None,URL('default','manage_products')))
        response.menu.append(('Manage Orders',None,URL('default','manage_orders')))
