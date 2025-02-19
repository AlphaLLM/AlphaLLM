import mysql.connector
import logging
import os
import discord
import asyncio
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger('AlphaLLM')

class DatabaseManager:
    def __init__(self):
        self.host = os.getenv("DB_HOST")
        self.user = os.getenv("DB_USER")
        self.password = os.getenv("DB_PASSWORD")
        self.database = os.getenv("DB_NAME")
        self.conn = None
        self.cursor = None
        self.connect()

    def connect(self):
        try:
            self.conn = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database
            )
            self.cursor = self.conn.cursor()
            logger.info("Connecté à la base de données !")
        except mysql.connector.Error as e:
            logger.error(f"Erreur de connexion : {e}")
            raise

    def disconnect(self):
        if self.conn:
            try:
                self.cursor.close()
                self.conn.close()
                logger.info("Déconnecté de la base de données !")
            except mysql.connector.Error as e:
                logger.error(f"Erreur de déconnexion : {e}")
            finally:
                self.conn = None
                self.cursor = None

    def execute(self, query, params=None):
        try:
            self.cursor.execute(query, params)
            self.conn.commit()
            return True
        except mysql.connector.Error as e:
            logger.error(f"Erreur durant la requête : {query} avec les paramètres suivants {params}. Erreur : {e}")
            self.conn.rollback()
            return False

    def fetchone(self, query, params=None):
        try:
            self.cursor.execute(query, params)
            return self.cursor.fetchone()
        except mysql.connector.Error as e:
            logger.error(f"Erreur durant la récupération unique : {e}")
            return None
        except Exception as e:
            logger.error(f"Erreur innatendue durant la récupération unique: {e}")
            return None

    def fetchall(self, query, params=None):
        try:
            self.cursor.execute(query, params)
            return self.cursor.fetchall()
        except mysql.connector.Error as e:
            logger.error(f"Erreur durant la récupération complète : {e}")
            return None
        except Exception as e:
            logger.error(f"Erreur innatendue durant la récupération complète : {e}")
            return None

async def get_models(db_manager: DatabaseManager = DatabaseManager()):
    logger.debug("Récupération des modèles depuis la base de données...")
    query = "SELECT * FROM models"
    try:
        models = db_manager.fetchall(query)
        logger.debug(f"Modèles récupérés : {models}")
        if models:
            columns = [column[0] if isinstance(column, tuple) else column.name for column in db_manager.cursor.description]
            models_list = [dict(zip(columns, model)) for model in models]
            logger.debug(f"Liste des modèles : {models_list}")
            return models_list
        else:
            logger.warning("Aucun modèle trouvé dans la base de données.")
            return []
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des modèles : {e}")
        return []

async def create_model_roles(bot, guild, models, db_manager: DatabaseManager):
    global role_model_mapping
    role_model_mapping = {}
    query = "SELECT id, name FROM roles"
    try:
        roles_db = db_manager.fetchall(query)
        logger.debug(f"Rôles récupérés depuis la base de données : {roles_db}")
        if roles_db:
            for role_id, role_name in roles_db:
                model = next((model for model in models if model["role_name"] == role_name), None)
                if model:
                    role_model_mapping[str(role_id)] = {"role_name": role_name, "model_name": model["name"]}
                    logger.debug(f"Role {role_name} mappé à l'ID {role_id} et au modèle {model['name']}")
                else:
                    logger.warning(f"Aucun modèle trouvé avec le role_name {role_name}. Suppression du rôle.")
                    try:
                        delete_query = "DELETE FROM roles WHERE id = %s"
                        if db_manager.execute(delete_query, (role_id,)):
                            logger.info(f"Rôle avec ID {role_id} supprimé de la base de données.")
                        else:
                            logger.error(f"Erreur lors de la suppression du rôle avec ID {role_id} depuis la base de données.")
                        try:
                            role = guild.get_role(int(role_id))
                            if role:
                                await role.delete(reason="Modèle inexistant")
                                logger.info(f"Rôle {role_name} (ID {role_id}) supprimé du serveur {guild.name}.")
                            else:
                                logger.warning(f"Rôle avec ID {role_id} non trouvé sur le serveur {guild.name}.")
                        except discord.Forbidden as e:
                            logger.error(f"Permissions insuffisantes pour supprimer {role_name} (ID {role_id}) du serveur {guild.name}: {e}")
                        except discord.HTTPException as e:
                            logger.error(f"Erreur HTTP pendant la suppression du rôle {role_name} (ID {role_id}) du serveur {guild.name}: {e}")


                    except Exception as e:
                        logger.error(f"Erreur lors de la suppression du rôle {role_name} (ID {role_id}) : {e}")
        else:
            logger.warning("Aucun rôle trouvé dans la base de données.")
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des rôles depuis la base de données : {e}")
        return

    existing_roles = guild.roles
    logger.debug(f"Rôles existants sur le serveur : {[role.name for role in existing_roles]}")
    bot_member = guild.me
    bot_roles = bot_member.roles
    logger.debug(f"Rôles attribués au bot : {[role.name for role in bot_roles]}")
    permissions = guild.me.guild_permissions
    if not permissions.manage_roles:
        logger.error(f"Le bot n'a pas la permission 'Manage Roles' sur le serveur {guild.name}")
        return

    for model in models:
        if 'role_name' not in model or 'name' not in model:
            logger.error(f"Modèle sans role_name ou name trouvé: {model}")
            continue

        role_name = model["role_name"]
        model_name = model["name"]
        existing_role = discord.utils.get(existing_roles, name=role_name)
        logger.debug(f"Vérification du rôle : {role_name} sur le serveur : {guild.name}")

        if existing_role:
            role_id = str(existing_role.id)
            logger.debug(f"Le rôle {role_name} existe déjà sur le serveur : {guild.name}")
            if role_id not in role_model_mapping:
                query = "INSERT INTO roles (id, name) VALUES (%s, %s) ON DUPLICATE KEY UPDATE name = %s"
                params = (existing_role.id, role_name, role_name)
                try:
                    if db_manager.execute(query, params):
                        role_model_mapping[role_id] = {"role_name": role_name, "model_name": model_name}
                        logger.debug(f"Rôle {role_name} mappé dans la base de données.")
                    else:
                        logger.error(f"Impossible de mapper le rôle {role_name} dans la base de données.")
                except Exception as e:
                    logger.error(f"Erreur lors de la mise à jour de la base de données pour le rôle {role_name} : {e}")
                continue
            else:
                role_model_mapping[role_id]["model_name"] = model_name

            if existing_role not in bot_roles:
                try:
                    await bot_member.add_roles(existing_role)
                    logger.info(f"Rôle {role_name} attribué au bot")
                except discord.Forbidden:
                    logger.error(f"Permissions insuffisantes pour ajouter le rôle {role_name} au bot sur le serveur {guild.name}. Ensure the bot's role is higher than the role being assigned.")
                except discord.HTTPException as e:
                    logger.error(f"Erreur HTTP pendant l'ajout du rôle {role_name} au bot sur le serveur {guild.name}: {e}")
        else:
            try:
                new_role = await guild.create_role(
                    name=role_name,
                    colour=discord.Colour(0xffffff),
                    mentionable=True
                )
                logger.info(f"Nouveau rôle créé : {role_name}")
                role_id = str(new_role.id)
                try:
                    await guild.me.add_roles(new_role)
                    logger.info(f"Rôle {role_name} attribué au bot")
                except discord.Forbidden:
                    logger.error(f"Permissions insuffisantes pour ajouter le rôle {role_name} au bot sur le serveur {guild.name}. Ensure the bot's role is higher than the role being assigned.")
                except discord.HTTPException as e:
                    logger.error(f"Erreur HTTP lors de l'ajout du rôle {role_name} au bot sur le serveur {guild.name}: {e}")


                query = "INSERT INTO roles (id, name) VALUES (%s, %s)"
                params = (new_role.id, role_name)
                try:
                    if db_manager.execute(query, params):
                        role_model_mapping[role_id] = {"role_name": role_name, "model_name": model_name}
                        logger.debug(f"Rôle {role_name} ajouté dans la base de données.")
                    else:
                        logger.error(f"Impossible d'ajouter le rôle {role_name} dans la base de données.")
                except Exception as e:
                    logger.error(f"Erreur lors de l'ajout du rôle {role_name} à la base de données : {e}")

                await asyncio.sleep(1)
            except discord.Forbidden:
                logger.error(f"Permission insuffisante pour créer le rôle {role_name}")
            except discord.HTTPException as e:
                logger.error(f"Erreur HTTP lors de la création du rôle {role_name}: {e}")

    logger.info(f"Vérification des rôles terminée pour {guild.name}")
