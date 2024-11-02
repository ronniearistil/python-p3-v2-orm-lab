from __init__ import CURSOR, CONN
from department import Department
from employee import Employee

class Review:
    # Dictionary of all Review instances saved to the database
    all = {}

    def __init__(self, year, summary, employee_id, id=None):
        """Initialize Review attributes, with id defaulting to None."""
        self.id = id
        self.year = year
        self.summary = summary
        self.employee_id = employee_id

    def __repr__(self):
        """Return a formatted string representation of the Review instance."""
        return (
            f"<Review {self.id}: {self.year}, {self.summary}, "
            + f"Employee: {self.employee_id}>"
        )

    @classmethod
    def create_table(cls):
        """Create the 'reviews' table in the database if it does not already exist."""
        sql = """
            CREATE TABLE IF NOT EXISTS reviews (
            id INTEGER PRIMARY KEY,
            year INT,
            summary TEXT,
            employee_id INTEGER,
            FOREIGN KEY (employee_id) REFERENCES employees(id))
        """
        CURSOR.execute(sql)
        CONN.commit()

    @classmethod
    def drop_table(cls):
        """Drop the 'reviews' table from the database if it exists."""
        sql = """
            DROP TABLE IF EXISTS reviews;
        """
        CURSOR.execute(sql)
        CONN.commit()

    def save(self):
        """Insert a new row with the year, summary, and employee_id into the 'reviews' table.
        Update the object's id attribute and add it to the all dictionary.
        """
        sql = """
            INSERT INTO reviews (year, summary, employee_id)
            VALUES (?, ?, ?)
        """
        CURSOR.execute(sql, (self.year, self.summary, self.employee_id))
        CONN.commit()

        # Update the id with the primary key of the new row
        self.id = CURSOR.lastrowid
        type(self).all[self.id] = self  # Save the instance to the dictionary

    @classmethod
    def create(cls, year, summary, employee_id):
        """Create a new Review instance, save it to the database, and return the instance."""
        review = cls(year, summary, employee_id)  # Create new instance
        review.save()  # Save instance to database
        return review

    @classmethod
    def instance_from_db(cls, row):
        """Return a Review instance with attributes from a database row.
        Check the all dictionary to avoid duplicate instances for the same row.
        """
        review = cls.all.get(row[0])  # Check if instance is already in dictionary
        if review:
            # If found, update instance's attributes
            review.year, review.summary, review.employee_id = row[1], row[2], row[3]
        else:
            # If not found, create a new instance and add to dictionary
            review = cls(row[1], row[2], row[3])
            review.id = row[0]
            cls.all[review.id] = review
        return review

    @classmethod
    def find_by_id(cls, id):
        """Find a Review instance by its id in the database and return it."""
        sql = "SELECT * FROM reviews WHERE id = ?"
        row = CURSOR.execute(sql, (id,)).fetchone()  # Execute query with bound parameter
        return cls.instance_from_db(row) if row else None  # Return instance or None

    def update(self):
        """Update the current Review's row in the database."""
        sql = """
            UPDATE reviews
            SET year = ?, summary = ?, employee_id = ?
            WHERE id = ?
        """
        # Update row in the database with the current attribute values
        CURSOR.execute(sql, (self.year, self.summary, self.employee_id, self.id))
        CONN.commit()

    def delete(self):
        """Delete the Review's row from the database, remove from dictionary, and reset id."""
        sql = "DELETE FROM reviews WHERE id = ?"
        CURSOR.execute(sql, (self.id,))  # Delete row from database using id
        CONN.commit()

        # Remove instance from dictionary and reset id
        del type(self).all[self.id]
        self.id = None

    @classmethod
    def get_all(cls):
        """Return a list of all Review instances by querying all rows in the table."""
        sql = "SELECT * FROM reviews"
        rows = CURSOR.execute(sql).fetchall()  # Fetch all rows in reviews table
        return [cls.instance_from_db(row) for row in rows]  # Map rows to instances

    # Property Methods

    @property
    def year(self):
        """Get the year attribute."""
        return self._year

    @year.setter
    def year(self, year):
        """Set the year, ensuring it is an integer >= 2000."""
        if isinstance(year, int) and year >= 2000:
            self._year = year
        else:
            raise ValueError("Year must be an integer >= 2000")

    @property
    def summary(self):
        """Get the summary attribute."""
        return self._summary

    @summary.setter
    def summary(self, summary):
        """Set the summary, ensuring it is a non-empty string."""
        if isinstance(summary, str) and len(summary) > 0:
            self._summary = summary
        else:
            raise ValueError("Summary must be a non-empty string")

    @property
    def employee_id(self):
        """Get the employee_id attribute."""
        return self._employee_id

    @employee_id.setter
    def employee_id(self, employee_id):
        """Set the employee_id, ensuring it references an existing Employee."""
        # Check if employee_id is a valid int and references an existing employee
        if isinstance(employee_id, int) and Employee.find_by_id(employee_id):
            self._employee_id = employee_id
        else:
            raise ValueError("employee_id must reference an existing Employee id")