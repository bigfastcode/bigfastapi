class Organization(_database.Base):
    __tablename__ = "organizations"
    id = Column(String(255), primary_key=True, index=True, default=uuid4().hex)
    creator = Column(String(255), ForeignKey("users.id"))
    mission = Column(String(255), index=True)
    vision = Column(String(255), index=True)
    values = Column(String(255), index=True)
    name = Column(String(255),unique= True, index=True, default="")
    date_created = Column(DateTime, default=_dt.datetime.utcnow)
    last_updated = Column(DateTime, default=_dt.datetime.utcnow)

