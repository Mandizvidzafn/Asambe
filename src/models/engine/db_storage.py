from src import db
from ...models.driver import Driver
from ...models.passenger import Passenger
from ...models.vehicle import Vehicle
from ...models.location import Location

# from ...models.admin import Admin

tables = {
    "driver": Driver,
    "passenger": Passenger,
    "location": Location,
    "vehicle": Vehicle,
    # "admin": Admin
}


class DB_Storage:
    """
    A class for interacting with the database and performing CRUD operations.
    """

    def create(self, item):
        """
        Create a new item in the specified table.

        Args:
            item: The item to be created.

        Returns:
            None
        """
        db.session.add(item)

    def save(self):
        """
        Save changes to the database.

        Returns:
            None
        """
        db.session.commit()

    def get_item(self, table, item_id):
        """
        Retrieve a specific item from the specified table.
        Args:
            table_name: The name of the table.
            item_id: The identifier of the item to retrieve.
        Returns:
            The retrieved item or None if not found.
        """
        table_name = table.lower()
        if table in tables:
            table_object = tables[table_name]
            result = table_object.query.get(item_id)
            return result

    def get_filtered_item(self, table, filter_by_item, item):
        """
        Retrieve a filtered item from the specified table.

        Args:
            table: The name of the table.
            filter_by_item: The column to filter by.
            item: The value to filter.

        Returns:
            The retrieved item or None if not found.
        """
        table_name = table.lower()
        if table_name in tables:
            table_object = tables[table_name]
            result = table_object.query.filter(
                getattr(table_object, filter_by_item) == item
            ).first()
            return result

    def get_all_filtered_item(self, table, filter_by_item, item):
        """
        Retrieve a filtered item from the specified table.
        Args:
            table: The name of the table.
            filter_by_item: The column to filter by.
            item: The value to filter.
        Returns:
            The retrieved item or None if not found.
        """
        table_name = table.lower()
        if table_name in tables:
            table_object = tables[table_name]
            result = table_object.query.filter(
                getattr(table_object, filter_by_item) == item
            ).all()
            return result

    def all(self, table):
        """
        Retrieve all items from the specified table.

        Args:
            table: The name of the table.

        Returns:
            A list of all items in the table.
        """
        table_name = table.lower()
        if table_name in tables.keys():
            result = tables[table_name].query.all()
            return result

    def delete_item(self, table, item):
        """
        Delete an item from the specified table.

        Args:
            table: The name of the table.
            item: The item to delete.

        Returns:
            None
        """
        table_name = table.lower()
        if table_name in tables:
            table_object = tables[table_name]
            result = table_object.query.get(item)
            if result:
                db.session.delete(result)
