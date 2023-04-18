from flask_app.config.mysqlconnection import connectToMySQL 
from flask_app import DB, bcrypt
from flask import flash, request
from flask_app.models import recipe_model
import re

EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')

class User:
    def __init__( self , data ):
        self.id = data['id']
        self.first_name = data['first_name']
        self.last_name = data['last_name']
        self.email = data['email']
        self.password = data['password']
        self.created_at = data['created_at']
        self.updated_at = data['updated_at']
        self.favorite_recipes = []

# class methods

    @classmethod
    def save(cls, data ): 
        query = """
            INSERT INTO users ( first_name, last_name, email, password, created_at, updated_at ) 
            VALUES ( %(first_name)s, %(last_name)s, %(email)s, %(password)s, NOW(), NOW() );
            """
        data = {
            **data,
            'password': bcrypt.generate_password_hash(data['password'])
            }
        result = connectToMySQL(DB).query_db(query, data)
        return result

    @classmethod
    def get_one(cls, data):
        data = {
            'id': data
            }
        query = """
            SELECT *
            FROM users
            WHERE id = %(id)s;
            """
        result = connectToMySQL(DB).query_db(query, data)
        return cls( result[0] )

    @classmethod
    def get_all(cls):
        query = "SELECT * FROM users;"
        results = connectToMySQL(cls.DB).query_db(query)
        users = []
        for i in results:
            users.append( cls(i) )
        return users

    @classmethod
    def add_favorite_recipe(cls, data):
        query = """
            INSERT INTO favorites (user_id, recipe_id) 
            VALUES (%(user_id)s, %(recipe_id)s);
            """
        results = connectToMySQL(DB).query_db(query, data)
        return results

    @classmethod
    def remove_favorite(cls, data):
        query = """
            DELETE FROM favorites
            WHERE user_id = %(user_id)s 
            AND recipe_id = %(recipe_id)s;
            """
        results = connectToMySQL(DB).query_db(query, data)
        return results

    @classmethod
    def get_user_fav_recipes(cls, data):
        data = {
            'id': data.id
            }
        query  = """
            SELECT * 
            FROM users 
            LEFT JOIN favorites 
            ON favorites.user_id = users.id 
            LEFT JOIN recipes 
            ON favorites.recipe_id = recipes.id 
            WHERE users.id = %(id)s;
            """
        results = connectToMySQL(DB).query_db(query, data)
        user = cls(results[0])
        if results[0]['name'] != None:
            for row_from_db in results:
                recipe_data = {
                    'id': row_from_db["recipes.id"],
                    'name': row_from_db["name"],
                    'description': row_from_db["description"],
                    'instructions': row_from_db["instructions"],
                    'date_made': row_from_db["date_made"],
                    'under': row_from_db["under"],
                    'created_at': row_from_db["recipes.created_at"],
                    'updated_at': row_from_db["recipes.updated_at"],
                    'user_id': row_from_db["recipes.user_id"]
                }
                user.favorite_recipes.append( recipe_model.Recipe( recipe_data ) )
        return user

# static methods

    @staticmethod
    def validate_user(user):
        query = """
            SELECT *
            FROM users
            WHERE email = %(email)s;
            """
        result = connectToMySQL(DB).query_db(query,user)
        is_valid = True
        if len(user['first_name']) < 2:
            is_valid = False
            flash("First name must be at least 2 characters.")
        if not user['first_name'].isalpha():
            is_valid = False
            flash("First name can contain letters only.")
        if len(user['last_name']) < 2:
            is_valid = False
            flash("Last name must be at least 2 characters.")
        if not user['last_name'].isalpha():
            is_valid = False
            flash("Last name can contain letters only.")
        if len(user['email']) == 0:
            is_valid = False
            flash("Email is a required for registration.")
        if not EMAIL_REGEX.match(user['email']): 
            is_valid = False
            flash("Invalid email address!")
        if result:
            is_valid = False
            flash("Email already registered.")
        if len(user['password']) < 2:
            is_valid = False
            flash("Password must be at least 8 characters")
        if user['confirm_password'] != user['password']:
            is_valid = False
            flash("Password fields do not match")
        return is_valid

    @staticmethod
    def validate_login(data):
        query = """
            SELECT * 
            FROM users 
            WHERE email = %(email)s;
            """
        result = connectToMySQL(DB).query_db(query, data)
        user_id = User(result[0])
        if not EMAIL_REGEX.match(data['email']):
            flash('Email/Password not valid')
            return False
        if len(data['login_password']) < 8:
            flash('Email/Password not valid')
            return False
        if not result:
            flash('Email/Password not valid')
            return False
        if not bcrypt.check_password_hash(user_id.password, data['login_password']):
            flash('Email/Password not valid')
            return False
        return user_id