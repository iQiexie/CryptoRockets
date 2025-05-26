from sqlalchemy.dialects.postgresql import dialect

stmt = ()

compiled_sql = stmt.compile(compile_kwargs={"literal_binds": True}, dialect=dialect())

print(str(compiled_sql))
