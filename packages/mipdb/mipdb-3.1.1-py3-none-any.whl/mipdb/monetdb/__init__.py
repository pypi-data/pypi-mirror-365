from sqlalchemy.dialects import registry

from mipdb.monetdb.monetdb_patch import PatchedMonetDialect
registry.register("monetdb.patched", "mipdb.monetdb.monetdb_patch", "PatchedMonetDialect")
