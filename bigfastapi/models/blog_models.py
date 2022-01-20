class Blog(_database.Base):
    __tablename__ = "blogs"
    id = Column(String(255), primary_key=True, index=True, default=uuid4().hex)
    creator = Column(String(255), ForeignKey("users.id"))
    title = Column(String(50), index=True, unique=True)
    content = Column(String(255), index=True)
    date_created = Column(DateTime, default=_dt.datetime.utcnow)
    last_updated = Column(DateTime, default=_dt.datetime.utcnow)