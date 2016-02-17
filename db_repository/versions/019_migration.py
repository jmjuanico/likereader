from sqlalchemy import *
from migrate import *


from migrate.changeset import schema
pre_meta = MetaData()
post_meta = MetaData()
comment = Table('comment', pre_meta,
    Column('id', INTEGER, primary_key=True, nullable=False),
    Column('body', TEXT),
    Column('body_html', TEXT),
    Column('timestamp', DATETIME),
    Column('disabled', BOOLEAN),
    Column('author_id', INTEGER),
    Column('post_id', INTEGER),
)

comment = Table('comment', post_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('body', Text),
    Column('body_html', Text),
    Column('timestamp', DateTime),
    Column('disabled', Boolean),
    Column('user_id', Integer),
    Column('post_id', Integer),
)


def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    pre_meta.tables['comment'].columns['author_id'].drop()
    post_meta.tables['comment'].columns['user_id'].create()


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    pre_meta.tables['comment'].columns['author_id'].create()
    post_meta.tables['comment'].columns['user_id'].drop()
