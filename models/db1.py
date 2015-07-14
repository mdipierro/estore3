NE = IS_NOT_EMPTY()
db.define_table(
    'product',
    Field('code',requires=NE),
    Field('name',requires=NE),
    Field('description',requires=NE),
    Field('qty_in_stock'),
    Field('unit_price','decimal(10,2)'),
    Field('image','upload'),
    Field('tags'),
    Field('popularity','integer',default=0),
    Field('featured','boolean',default=False),
    Field('on_sale','boolean',default=False),
    Field('tax','decimal(10,2)'),
    Field('keywords',required=True,
          compute=lambda r: "%(code)s %(name)s %(tags)s" % r),
    auth.signature)

db.define_table(
    'purchase_order',
    Field('buyer_name'),
    Field('shipping_address'),
    Field('shipping_city'),
    Field('shipping_zip'),
    Field('shipping_state'),
    Field('shipping_country'),
    Field('total_price','decimal(10,2)',readable=False,writable=False),
    Field('total_tax','decimal(10,2)',readable=False,writable=False),
    Field('total_balance','decimal(10,2)',readable=False,writable=False),
    Field('amount_paid','decimal(10,2)',readable=False,writable=False),
    Field('payment_id',readable=False,writable=False),
    Field('paid_on','datetime',readable=False,writable=False),
    Field('status',requires=IS_IN_SET(('submitted','shipped','received','returned')),
          default='submitted',readable=False,writable=False),
    Field('notes','text'),
    auth.signature)

db.define_table(
    'purchase_item',
    Field('purchase_order','reference purchase_order'),
    Field('product','reference product'),
    db.product, # yes we copy the product description at the moment of an order
    Field('quantity_in_cart','integer'),
    auth.signature)

#db(db.auth_user.id>1).delete()
#db(db.product).delete()
if db(db.product).count()==0:
    import random
    from gluon.contrib.populate import populate
    n = 10000
    for name in ['Table','Chair','Desk','Shelves','Pen','Robot','Pillow','Bed','Car']:
        for color in ['red','blue','greem','orange','yellow']:
            n = n+1
            db.product.insert(
                code="%.5i" % n,
                name=name,tags=name+' '+color,description='bla '*100,
                unit_price=random.randint(10,1000),tax=0.10,
                qty_in_stock=random.randint(0,100))
                             
