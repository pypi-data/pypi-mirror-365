class DbTable:
    def __init__(self, schema: str, name: str):
        self.qualified_name = f"{schema}.{name}"
        self.schema = schema
        self.name = name
