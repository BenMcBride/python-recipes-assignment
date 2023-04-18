from flask_app.config.mysqlconnection import connectToMySQL 
from flask_app.models import user_model
from flask_app import DB
from flask import flash

class Recipe:
    def __init__( self , data ):
        self.id = data['id']
        self.name = data['name']
        self.description = data['description']
        self.instructions = data['instructions']
        self.date_made = data['date_made']
        self.under = data['under']
        self.user_id = data['user_id']
        self.created_at = data['created_at']
        self.updated_at = data['updated_at']
        self.favorited_by = []

    @property
    def created_by(self):
        return user_model.User.get_one(self.user_id)

# class methods

    @classmethod
    def save(cls, **data ):
        query = """
            INSERT INTO recipes ( name, description, instructions, date_made, under, user_id, created_at, updated_at ) 
            VALUES ( %(name)s, %(description)s, %(instructions)s, %(date_made)s, %(under)s, %(user_id)s, NOW(), NOW() );
            """
        result = connectToMySQL(DB).query_db(query, data)
        return result

    @classmethod
    def get_one(cls, data):
        query = """
            SELECT *
            FROM recipes
            WHERE id = %(id)s;
            """
        data = {
            'id': data
            }
        result = connectToMySQL(DB).query_db(query, data)
        return cls( result[0] )

    @classmethod
    def get_all(cls):
        query = "SELECT * FROM recipes;"
        results = connectToMySQL(DB).query_db(query)
        recipes = []
        for i in results:
            recipes.append( cls(i) )
        return recipes

    @classmethod
    def edit_recipe(cls, data):
        query = """
            UPDATE recipes SET 
            name = %(name)s, 
            description = %(description)s, 
            instructions = %(instructions)s, 
            date_made = %(date_made)s, 
            under = %(under)s, 
            updated_at = NOW() 
            WHERE id = %(id)s;
            """
        result = connectToMySQL(DB).query_db(query, data)
        return result

    @classmethod
    def get_recipe_favorited_by(cls, data):
        data = {
            'id': data
            }
        query  = """
            SELECT *
            FROM recipes
            LEFT JOIN favorites
            ON favorites.recipe_id = recipes.id
            LEFT JOIN users
            ON favorites.user_id = users.id
            WHERE recipes.id = %(id)s;
            """
        results = connectToMySQL(DB).query_db(query, data)
        recipe = cls(results[0])
        for row_from_db in results:
            user_data = {
                'id': row_from_db["users.id"],
                'first_name': row_from_db["first_name"],
                'last_name': row_from_db["last_name"],
                'email': row_from_db["email"],
                'password': row_from_db["password"],
                'created_at': row_from_db["users.created_at"],
                'updated_at': row_from_db["users.updated_at"]
            }
            recipe.favorited_by.append( user_model.User(user_data))
        return recipe

    @classmethod
    def get_other_recipes(cls, data):
        query = """
            SELECT * 
            FROM recipes 
            WHERE recipes.id NOT IN (
                SELECT recipes.id 
                FROM recipes 
                LEFT JOIN favorites 
                ON recipes.id = favorites.recipe_id 
                WHERE favorites.user_id = %(user_id)s);"""
        results = connectToMySQL(DB).query_db(query, data)
        other_recipes = []
        for i in results:
            other_recipes.append(i)
        return other_recipes

    @classmethod
    def delete(cls, data):
        query = """
            DELETE FROM recipes 
            WHERE id = %(id)s;"""
        result = connectToMySQL(DB).query_db(query, data)
        return result

# static methods

    @staticmethod
    def validate_recipe(data):
        err = {}
        if 'name' in data and len(data['name']) < 3:
            err['name'] = 'Recipe name must be 3 characters or longer.'
        if 'description' in data and len(data['description']) < 3:
            err['description'] = 'Recipe description must be 3 characters or longer.'
        if 'instructions' in data and len(data['instructions']) < 3:
            err['instructions'] = 'Recipe instructions must be 3 characters or longer.'
        if 'date_made' in data and (data['date_made']) == '':
            err['date_made'] = 'Please enter a date.'
        if 'under' not in data:
            err['under'] = 'Must check yes or no.'
        for category, message in err.items():
            flash(message, category)
        return len(err) == 0