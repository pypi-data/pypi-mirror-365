import xmlrpc.client

class OdooConnector:
    """
    A simple XML-RPC client wrapper for interacting with the Odoo backend.

    Example:
        connector = OdooConnector(
            url='https://my-odoo.com',
            db='my_db',
            username='user@example.com',
            password='securepassword'
        )

        partners = connector.read('res.partner', fields=['name', 'email'], limit=10)
    """

    def __init__(self, url: str, db: str, username: str, password: str):
        """
        Initialize the connector and authenticate to the Odoo server.

        Args:
            url (str): Base URL of your Odoo instance (e.g. 'https://my-odoo.com')
            db (str): Name of the Odoo database
            username (str): Login email or username
            password (str): Password for the account

        Raises:
            Exception: If authentication fails
        """
        self.url = url
        self.db = db
        self.username = username
        self.password = password

        self.common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
        self.uid = self.common.authenticate(db, username, password, {})
        if not self.uid:
            raise Exception("❌ Authentication failed: please check your credentials.")

        self.models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')

    def search(self, model: str, domain: list, limit: int = 0) -> list:
        """
        Search records based on a domain filter.

        Args:
            model (str): Name of the model (e.g. 'res.partner')
            domain (list): Domain filters (e.g. [['is_company', '=', True]])
            limit (int): Maximum number of records to return

        Returns:
            list: List of matching record IDs
        """
        return self.models.execute_kw(
            self.db, self.uid, self.password,
            model, 'search',
            [domain], {'limit': limit}
        )

    def read(self, model: str, domain: list = [], fields: list = None, limit: int = 0) -> list:
        """
        Search and read records in one call.

        Args:
            model (str): Model name (e.g. 'res.partner')
            domain (list): Domain filter (optional)
            fields (list): List of fields to retrieve (e.g. ['name', 'email'])
            limit (int): Maximum number of results

        Returns:
            list: List of dictionaries representing each record

        Example:
            connector.read('res.partner', fields=['name', 'email'], limit=5)
        """
        return self.models.execute_kw(
            self.db, self.uid, self.password,
            model, 'search_read',
            [domain],
            {'fields': fields or [], 'limit': limit}
        )

    def create(self, model: str, data: dict) -> int:
        """
        Create a new record.

        Args:
            model (str): Model name (e.g. 'res.partner')
            data (dict): Dictionary of field values

        Returns:
            int: ID of the newly created record

        Example:
            connector.create('res.partner', {'name': 'Luffy', 'email': 'luffy@onepiece.com'})
        """
        return self.models.execute_kw(
            self.db, self.uid, self.password,
            model, 'create',
            [data]
        )

    def write(self, model: str, ids: list, data: dict) -> bool:
        """
        Update existing records.

        Args:
            model (str): Model name (e.g. 'res.partner')
            ids (list): List of record IDs to update
            data (dict): Dictionary of field values to update

        Returns:
            bool: True if the update was successful

        Example:
            connector.write('res.partner', [1], {'phone': '0123456789'})
        """
        return self.models.execute_kw(
            self.db, self.uid, self.password,
            model, 'write',
            [ids, data]
        )

    def unlink(self, model: str, ids: list) -> bool:
        """
        Delete records by ID.

        Args:
            model (str): Model name (e.g. 'res.partner')
            ids (list): List of record IDs to delete

        Returns:
            bool: True if the records were deleted

        Example:
            connector.unlink('res.partner', [3])
        """
        return self.models.execute_kw(
            self.db, self.uid, self.password,
            model, 'unlink',
            [ids]
        )

    def call_method(self, model: str, method: str, args: list = [], kwargs: dict = {}) -> any:
        """
        Call any custom method on a model.

        Args:
            model (str): Model name (e.g. 'res.partner')
            method (str): Method to call (e.g. 'check_access_rights')
            args (list): Positional arguments
            kwargs (dict): Keyword arguments

        Returns:
            any: The method's return value

        Example:
            connector.call_method('res.partner', 'check_access_rights', ['read'], {'raise_exception': False})
        """
        return self.models.execute_kw(
            self.db, self.uid, self.password,
            model, method,
            args, kwargs
        )

    def get_version(self) -> dict:
        """
        Get the version of the connected Odoo instance.

        Returns:
            dict: Dictionary with version details (e.g. {'server_version': '17.0'})
        """
        return self.common.version()
