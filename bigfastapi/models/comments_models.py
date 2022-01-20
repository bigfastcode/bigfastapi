class Comment(_database.Base):
    __tablename__ = "comments"
    id = Column(Integer, primary_key=True, autoincrement=True)
    model_type = Column(String) 
    rel_id = Column(String)
    
    email = Column(String(255))
    name = Column(String(255))
    text = Column(String())
    downvotes = Column(Integer, default=0, nullable=False)
    upvotes = Column(Integer, default=0, nullable=False)
    time_created = Column(DateTime(timezone=True), server_default=func.now())
    time_updated = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())

    p_id = Column(Integer, ForeignKey("comments.id", ondelete="cascade"))
    parent = _orm.relationship("Comment", backref=_orm.backref('replies',  cascade="all, delete-orphan"), remote_side=[id], post_update=True, single_parent=True, uselist=True)

    def __init__(self, *args, **kwargs):
        super().__init__()
        self.model_type = kwargs["model_name"] 
        self.rel_id = kwargs["rel_id"]
        self.email = kwargs["email"] 
        self.name = kwargs["name"] 
        self.text = kwargs["text"] 
        self.p_id = kwargs.get("p_id", None)

    @hybrid_method
    def upvote(self):
        self.upvotes += 1
    
    @hybrid_method
    def downvote(self):
        self.downvotes += 1
