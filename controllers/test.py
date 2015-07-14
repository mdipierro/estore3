from gluon.tools import Service; service = Service(db)

@service.run
def mycall():
    if response:
        return 'true'
    return 'false'

def call():
    session.forget(response)
    return service()

def stripe():
    from gluon.contrib.stripe import StripeForm                                                       
    form = StripeForm(                                                                                
        pk="pico",
        sk="pallino",
        amount=150, # $1.5 (amount is in cents)                                                       
        description="Nothing").process()                                                              
    if form.accepted:                                                                                 
        payment_id = form.response['id']                                                              
        redirect(URL('thank_you'))                                                                    
    elif form.errors:                                                                                 
        redirect(URL('pay_error'))                                                                    
    return dict(form=form)  

@auth.requires_login()
def index():
    COLORS = ['red','blue','green']
    types = ['string','text','date','time','datetime','integer','double',
             'list:string','list:integer','upload']
    db.define_table('mytable',Field('color','list:string',widget=SQLFORM.widgets.checkboxes.widget,
                                    requires=IS_IN_SET(COLORS,multiple=True)),
                    *[Field('f_'+t.replace(':','_'),t,requires=IS_NOT_EMPTY()) 
                      for t in types])
    return dict(        
        form = SQLFORM(db.mytable).process(),
        grid = SQLFORM.grid(db.mytable),
        )
