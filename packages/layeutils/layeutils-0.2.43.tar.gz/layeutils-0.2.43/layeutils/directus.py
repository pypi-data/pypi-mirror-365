
from datetime import datetime

from directus_sdk_py import DirectusClient, DirectusQueryBuilder, DOp


class TradingRecord():
    """Trading Record Class

    Attributes: id, open_time, close_time, symbol, direction, quality, filled_price, commission, comments

    """

    id: str
    daily_journal: str
    symbol: str
    trading_time: datetime
    direction: int
    quality: float
    filled_price: float
    commission: float
    comments: str

    def load_from_directus_obj(self, directus_obj: dict):
        """ Load TradingRecord instance from a Directus object.

        Args:
            directus_obj (dict): Directus object containing trading record data
        """
        self.id = directus_obj.get('id')
        self.daily_journal = directus_obj.get('daily_journal')
        self.symbol = directus_obj.get('symbol')
        self.trading_time = datetime.fromisoformat(directus_obj.get('trading_time'))
        self.direction = int(directus_obj.get('direction'))
        self.quality = float(directus_obj.get('quality'))
        self.filled_price = float(directus_obj.get('filled_price'))
        self.commission = float(directus_obj.get('commission'))
        self.comments = directus_obj.get('comments')

    def to_directus_obj(self):
        """ Convert the TradingRecord instance to a dictionary.

        Returns:
            _type_: _description_
        """
        result = {}
        if hasattr(self, 'id'):
            result['id'] = self.id
        if hasattr(self, 'daily_journal'):
            result['daily_journal'] = self.daily_journal
        if hasattr(self, 'symbol'):
            result['symbol'] = self.symbol
        if hasattr(self, 'trading_time'):
            result['trading_time'] = self.trading_time.isoformat()
        if hasattr(self, 'direction'):
            result['direction'] = str(self.direction)
        if hasattr(self, 'quality'):
            result['quality'] = str(self.quality)
        if hasattr(self, 'filled_price'):
            result['filled_price'] = str(self.filled_price)
        if hasattr(self, 'commission'):
            result['commission'] = str(self.commission)
        if hasattr(self, 'comments'):
            result['comments'] = self.comments
        return result


def get_directus_client(
        url: str = 'https://directus.laye.wang',
        access_token: str = 'CLo_fK9xZ2lovcaIPKnGpFqQMzX0WBH0') -> DirectusClient:
    """Get Directus Client

    Returns:
        DirectusClient: Directus Client instance
    """
    return DirectusClient(url=url, token=access_token)


def get_items_from_collection(
        client: DirectusClient,
        collection_name: str,
        query: dict = None):
    """Get items from a Directus collection.

    Args:
        client (DirectusClient): Directus Client instance
        collection_name (str): Name of the collection to fetch items from
        query (dict, optional): Query parameters to filter items. Defaults to None.
            for query build example, check method `build_query_by_datetime_range`

    Returns:
        List of items in the specified collection
    """
    items = client.get_items(collection_name, query)
    return items


def build_query_by_datetime_range(
        directus_collection_field: str,
        start_time: datetime,
        end_time: datetime) -> dict:
    """Build a query to filter items by a datetime range.
    Args:
        directus_collection_field (str): The field in the Directus collection to filter by datetime
        start_time (datetime): Start of the datetime range
        end_time (datetime): End of the datetime range
    Returns:
        dict: Query dictionary with the datetime range filter
    """
    builder = DirectusQueryBuilder()
    query = (builder.field(
        directus_collection_field,
        DOp.BETWEEN,
        [start_time.isoformat(), end_time.isoformat()])
        .build())
    return query


def create_trading_record(client: DirectusClient, trading_record: TradingRecord):
    """Create a new trading record in Directus.
    Args:
        client (DirectusClient): Directus Client instance
        trading_record (TradingRecord): TradingRecord instance to be created
    Returns:
        The created trading record item
    """
    return client.create_item(
        collection_name='trading_record',
        item_data=trading_record.to_directus_obj()
    )


def update_trading_record(client: DirectusClient, trading_record: TradingRecord):
    """Update an existing trading record in Directus.

    Args:
        client (DirectusClient): Directus Client instance
        trading_record (TradingRecord): TradingRecord instance to be updated
    Returns:
        The updated trading record item
    """
    return client.update_item(
        collection_name='trading_record',
        item_id=trading_record.id,
        item_data=trading_record.to_directus_obj()
    )


def delete_trading_record(client: DirectusClient, trading_record_id: str):
    """Delete a trading record from Directus.

    Args:
        client (DirectusClient): Directus Client instance
        trading_record_id (str): ID of the trading record to be deleted
    """
    client.delete_item(
        collection_name='trading_record',
        item_id=trading_record_id
    )
