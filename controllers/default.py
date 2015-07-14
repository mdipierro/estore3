# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

#########################################################################
## This is a sample controller
## - index is the default action of any application
## - user is required for authentication and authorization
## - download is for downloading files uploaded in the db (does streaming)
#########################################################################

def index():
    return dict()

def search():
    keywords = request.vars.keywords.split() if request.vars.keywords else []
    price = request.vars.price
    page = int(request.vars.page or 0)
    queries = []
    if keywords:
        queries.append(reduce(lambda a,b:a&b,
                              [db.product.keywords.contains(k) for k in keywords]))
    if price:
        queries.append(db.product.unit_price<=float(price))
    if not queries: query = db.product
    else: query = reduce(lambda a,b: a&b, queries)    
    return db(query).select(limitby=(page*100,page*100+100)).as_json()

def submit_order():
    import json
    session.order = json.loads(request.vars.cart)
    return 'ok'

@auth.requires_login()
def order_info():
    form = SQLFORM(db.purchase_order).process()
    if form.accepted:
        pass    
    return dict(form=form)

@auth.requires_membership('manager')
def manage_products():
    return dict(grid=SQLFORM.grid(db.product))

@auth.requires_membership('manager')
def manage_orders():
    return dict(grid=SQLFORM.smartgrid(db.purchase_order))

def user():
    """
    exposes:
    http://..../[app]/default/user/login
    http://..../[app]/default/user/logout
    http://..../[app]/default/user/register
    http://..../[app]/default/user/profile
    http://..../[app]/default/user/retrieve_password
    http://..../[app]/default/user/change_password
    http://..../[app]/default/user/manage_users (requires membership in
    http://..../[app]/default/user/bulk_register
    use @auth.requires_login()
        @auth.requires_membership('group name')
        @auth.requires_permission('read','table name',record_id)
    to decorate functions that need access control
    """
    return dict(form=auth())


@cache.action()
def download():
    """
    allows downloading of uploaded files
    http://..../[app]/default/download/[filename]
    """
    return response.download(request, db)


def call():
    """
    exposes services. for example:
    http://..../[app]/default/call/jsonrpc
    decorate with @services.jsonrpc the functions to expose
    supports xml, json, xmlrpc, jsonrpc, amfrpc, rss, csv
    """
    return service()


