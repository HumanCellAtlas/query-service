import psycopg2.extras

# http://initd.org/psycopg/docs/faq.html#faq-jsonb-adapt
psycopg2.extras.register_json(oid=3802, array_oid=3807, globally=True)
