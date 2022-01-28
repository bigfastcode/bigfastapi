class qrcode(database.Base):
    __tablename__ = "qrcode"
    id = Column(String(255), primary_key=True, index=True, default=uuid4().hex)
    question = Column(String(255), index=True)
    answer = Column(Text(), index=True)
    created_by = Column(String(255), index=True)
    date_created = Column(DateTime, default=dt.datetime.utcnow)