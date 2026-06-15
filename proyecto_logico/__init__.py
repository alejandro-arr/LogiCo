# Parche para saltar la validación de versión de MariaDB en XAMPP (que suele ser 10.4)
# Django exige 10.6+ pero la 10.4 funciona perfectamente para lo básico.
from django.db.backends.mysql.base import DatabaseWrapper
from django.db.backends.mysql.features import DatabaseFeatures

DatabaseWrapper.check_database_version_supported = lambda self: None

# Parche 2: MariaDB 10.4 NO soporta la cláusula RETURNING en los INSERTs.
# Le decimos a Django explícitamente que no intente usarla.
DatabaseFeatures.can_return_columns_from_insert = False
DatabaseFeatures.can_return_rows_from_bulk_insert = False
