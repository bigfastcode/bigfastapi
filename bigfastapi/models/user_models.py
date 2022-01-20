
class User(_database.Base):
    __tablename__ = "users"
    id = Column(String(255), primary_key=True, index=True, default=uuid4().hex)
    email = Column(String(255), unique=True, index=True)
    first_name = Column(String(255), index=True)
    last_name = Column(String(255), index=True)
    phone_number = Column(String(255), index=True, default="")
    password = Column(String(255))
    is_active = Column(Boolean)
    is_verified = Column(Boolean)
    is_superuser = Column(Boolean, default=False)
    organization = Column(String(255), default="")

    def verify_password(self, password: str):
        return _hash.bcrypt.verify(password, self.password)
