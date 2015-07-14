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
    session.cart = json.loads(request.vars.cart)
    return 'ok'

@auth.requires_login()
def order_info():
    if not session.cart:
        redirect(URL('index'))
    db.purchase_order.buyer_name.default = '%(first_name)s %(last_name)s' % auth.user
    form = SQLFORM(db.purchase_order).process()
    if form.accepted:
        total_balance = 0
        for item in session.cart:
            item['product'] = item['id']
            item['purchase_order'] = form.vars.id
            del item['id']
            db.purchase_item.insert(**item)
            total_balance += item['unit_price']*int(item['quantity_in_cart'])
        session.cart = None
        db(db.purchase_order.id==form.vars.id).update(total_balance=total_balance)
        redirect(URL('pay',args=form.vars.id, hmac_key=STRIPE_SECRET_KEY))
    return dict(form=form)

def pay():
    if not URL.verify(request, hmac_key=STRIPE_SECRET_KEY):
        redirect(URL('index'))
    from gluon.contrib.stripe import StripeForm
    response.flash = None # never show a response.flash
    order = db.purchase_order(request.args(0,cast=int))
    if not order or order.amount_paid:
        session.flash = 'you paid already!'
        redirect(URL('index'))
    amount = order.total_balance
    description ="..."
    form = StripeForm(
        pk=STRIPE_PUBLISHABLE_KEY,
        sk=STRIPE_SECRET_KEY,
        amount=int(100*amount),
        description=description).process()
    if form.accepted:
        code = '[%s/%s]' % (order.id,form.response['id'])
        auth.settings.mailer.send(
            to=auth.user.email,
            subject='...',
            message='Your payment of $%.2f has been processed %s' % (
                amount, code))
        order.update_record(total_balance=0,amount_paid=amount,
                            payment_id=form.response['id'],
                            paid_on=request.now)
        redirect(URL('thank_you', vars=dict(code=code), hmac_key=STRIPE_SECRET_KEY))
    elif form.errors:
        redirect(URL('pay_error'))
    return dict(form=form)

def thank_you():
    if not URL.verify(request, hmac_key=STRIPE_SECRET_KEY):
        redirect(URL('index'))
    return locals()

def pay_error():
    return locals()

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


