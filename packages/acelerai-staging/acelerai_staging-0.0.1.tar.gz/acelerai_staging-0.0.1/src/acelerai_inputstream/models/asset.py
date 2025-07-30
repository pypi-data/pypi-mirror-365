

class Asset:
    """
    Represents an asset in the AcelerAI.
    Attributes:
        id (str): Unique identifier for the asset.
        name (str): Name of the asset.
        created_on (str): Creation date of the asset.
    """
    id: str
    name: str
    created_at: str

    def __init__(self, id: str, name: str, created_at: str):
        """
        Initializes the Asset with id, name, and creation date.
        :param id: Unique identifier for the asset.
        :param name: Name of the asset.
        :param created_at: Creation date of the asset.
        """
        self.id = id
        self.name = name
        self.created_at = created_at