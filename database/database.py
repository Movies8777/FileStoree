#Codeflix_Botz
#rohit_1888 on Tg

import motor, asyncio, time
import motor.motor_asyncio
import pymongo, os
from config import DB_URI, DB_NAME
import logging
from datetime import datetime, timedelta

dbclient = pymongo.MongoClient(DB_URI)
database = dbclient[DB_NAME]

logging.basicConfig(level=logging.INFO)

default_verify = {
    'is_verified': False,
    'verified_time': 0,
    'verify_token': "",
    'original_start': "",
    'link': ""
}

def new_user(id):
    return {
        '_id': id,
        'verify_status': {
            'is_verified': False,
            'verified_time': "",
            'verify_token': "",
            'link': ""
        }
    }

class Rohit:

    def __init__(self, DB_URI, DB_NAME):
        self.dbclient = motor.motor_asyncio.AsyncIOMotorClient(DB_URI)
        self.database = self.dbclient[DB_NAME]

        self.channel_data = self.database['channels']
        self.admins_data = self.database['admins']
        self.user_data = self.database['users']
        self.sex_data = self.database['sex']
        self.banned_user_data = self.database['banned_user']
        self.autho_user_data = self.database['autho_user']
        self.del_timer_data = self.database['del_timer']
        self.fsub_data = self.database['fsub']   
        self.rqst_fsub_data = self.database['request_forcesub']
        self.rqst_fsub_Channel_data = self.database['request_forcesub_channel']
        self.file_data = self.database['files']
        self.ongoing_data = self.database['ongoing']
        self.settings_data = self.database['settings']
        self.sched_queue_data = self.database['scheduled_queue']
        self.sched_config_data = self.database['scheduler_config']


    # USER DATA
    async def present_user(self, user_id: int):
        found = await self.user_data.find_one({'_id': user_id})
        return bool(found)

    async def add_user(self, user_id: int):
        await self.user_data.insert_one({'_id': user_id})
        return

    async def full_userbase(self):
        user_docs = await self.user_data.find().to_list(length=None)
        user_ids = [doc['_id'] for doc in user_docs]
        return user_ids

    async def total_users_count(self):
        return await self.user_data.count_documents({})

    async def del_user(self, user_id: int):
        await self.user_data.delete_one({'_id': user_id})
        return


    # ADMIN DATA
    async def admin_exist(self, admin_id: int):
        found = await self.admins_data.find_one({'_id': admin_id})
        return bool(found)

    async def add_admin(self, admin_id: int):
        if not await self.admin_exist(admin_id):
            await self.admins_data.insert_one({'_id': admin_id})
            return

    async def del_admin(self, admin_id: int):
        if await self.admin_exist(admin_id):
            await self.admins_data.delete_one({'_id': admin_id})
            return

    async def get_all_admins(self):
        users_docs = await self.admins_data.find().to_list(length=None)
        user_ids = [doc['_id'] for doc in users_docs]
        return user_ids


    # BAN USER DATA
    async def ban_user_exist(self, user_id: int):
        found = await self.banned_user_data.find_one({'_id': user_id})
        return bool(found)

    async def add_ban_user(self, user_id: int):
        if not await self.ban_user_exist(user_id):
            await self.banned_user_data.insert_one({'_id': user_id})
            return

    async def del_ban_user(self, user_id: int):
        if await self.ban_user_exist(user_id):
            await self.banned_user_data.delete_one({'_id': user_id})
            return

    async def get_ban_users(self):
        users_docs = await self.banned_user_data.find().to_list(length=None)
        user_ids = [doc['_id'] for doc in users_docs]
        return user_ids



    # AUTO DELETE TIMER SETTINGS
    async def set_del_timer(self, value: int):        
        existing = await self.del_timer_data.find_one({})
        if existing:
            await self.del_timer_data.update_one({}, {'$set': {'value': value}})
        else:
            await self.del_timer_data.insert_one({'value': value})

    async def get_del_timer(self):
        data = await self.del_timer_data.find_one({})
        if data:
            return data.get('value', 600)
        return 0


    # CHANNEL MANAGEMENT
    async def channel_exist(self, channel_id: int):
        found = await self.fsub_data.find_one({'_id': channel_id})
        return bool(found)

    async def add_channel(self, channel_id: int):
        if not await self.channel_exist(channel_id):
            await self.fsub_data.insert_one({'_id': channel_id})
            return

    async def rem_channel(self, channel_id: int):
        if await self.channel_exist(channel_id):
            await self.fsub_data.delete_one({'_id': channel_id})
            return

    async def show_channels(self):
        channel_docs = await self.fsub_data.find().to_list(length=None)
        channel_ids = [doc['_id'] for doc in channel_docs]
        return channel_ids

    
# Get current mode of a channel
    async def get_channel_mode(self, channel_id: int):
        data = await self.fsub_data.find_one({'_id': channel_id})
        return data.get("mode", "off") if data else "off"

    # Set mode of a channel
    async def set_channel_mode(self, channel_id: int, mode: str):
        await self.fsub_data.update_one(
            {'_id': channel_id},
            {'$set': {'mode': mode}},
            upsert=True
        )

    # REQUEST FORCE-SUB MANAGEMENT

    # Add the user to the set of users for a   specific channel
    async def req_user(self, channel_id: int, user_id: int):
        try:
            await self.rqst_fsub_Channel_data.update_one(
                {'_id': int(channel_id)},
                {'$addToSet': {'user_ids': int(user_id)}},
                upsert=True
            )
        except Exception as e:
            print(f"[DB ERROR] Failed to add user to request list: {e}")


    # Method 2: Remove a user from the channel set
    async def del_req_user(self, channel_id: int, user_id: int):
        # Remove the user from the set of users for the channel
        await self.rqst_fsub_Channel_data.update_one(
            {'_id': channel_id}, 
            {'$pull': {'user_ids': user_id}}
        )

    # Check if the user exists in the set of the channel's users
    async def req_user_exist(self, channel_id: int, user_id: int):
        try:
            found = await self.rqst_fsub_Channel_data.find_one({
                '_id': int(channel_id),
                'user_ids': int(user_id)
            })
            return bool(found)
        except Exception as e:
            print(f"[DB ERROR] Failed to check request list: {e}")
            return False  


    # Method to check if a channel exists using show_channels
    async def reqChannel_exist(self, channel_id: int):
    # Get the list of all channel IDs from the database
        channel_ids = await self.show_channels()
        #print(f"All channel IDs in the database: {channel_ids}")

    # Check if the given channel_id is in the list of channel IDs
        if channel_id in channel_ids:
            #print(f"Channel {channel_id} found in the database.")
            return True
        else:
            #print(f"Channel {channel_id} NOT found in the database.")
            return False



    # VERIFICATION MANAGEMENT
    async def db_verify_status(self, user_id):
        user = await self.user_data.find_one({'_id': user_id})
        if user:
            return user.get('verify_status', default_verify)
        return default_verify

    async def db_update_verify_status(self, user_id, verify):
        await self.user_data.update_one({'_id': user_id}, {'$set': {'verify_status': verify}})

    async def get_verify_status(self, user_id):
        verify = await self.db_verify_status(user_id)
        return verify

    async def update_verify_status(self, user_id, verify_token="", is_verified=False, verified_time=0, original_start="", link=""):
        current = await self.db_verify_status(user_id)
        current['verify_token'] = verify_token
        current['is_verified'] = is_verified
        current['verified_time'] = verified_time
        current['original_start'] = original_start
        current['link'] = link
        await self.db_update_verify_status(user_id, current)

    # Set verify count (overwrite with new value)
    async def set_verify_count(self, user_id: int, count: int):
        await self.sex_data.update_one({'_id': user_id}, {'$set': {'verify_count': count}}, upsert=True)

    # Get verify count (default to 0 if not found)
    async def get_verify_count(self, user_id: int):
        user = await self.sex_data.find_one({'_id': user_id})
        if user:
            return user.get('verify_count', 0)
        return 0

    # Reset all users' verify counts to 0
    async def reset_all_verify_counts(self):
        await self.sex_data.update_many(
            {},
            {'$set': {'verify_count': 0}} 
        )

    # Get total verify count across all users
    async def get_total_verify_count(self):
        pipeline = [
            {"$group": {"_id": None, "total": {"$sum": "$verify_count"}}}
        ]
        result = await self.sex_data.aggregate(pipeline).to_list(length=1)
        return result[0]["total"] if result else 0

    # FILE INDEXING
    async def add_file(self, file_name, file_size, file_type, file_id, msg_id, caption=None):
        file_dict = {
            'file_name': file_name,
            'file_size': file_size,
            'file_type': file_type,
            'file_id': file_id,
            'msg_id': msg_id,
            'caption': caption
        }
        try:
            await self.file_data.update_one(
                {'file_id': file_id},
                {'$set': file_dict},
                upsert=True
            )
        except Exception as e:
            logging.error(f"Failed to index {file_name}: {e}")

    async def find_file(self, query):
        import re
        # Split query into words and search for each word
        query_words = query.split()
        regex_pattern = "".join([f"(?=.*{re.escape(word)})" for word in query_words])

        # Search in filename and caption with word-agnostic matching
        cursor = self.file_data.find({
            '$or': [
                {'file_name': {'$regex': regex_pattern, '$options': 'i'}},
                {'caption': {'$regex': regex_pattern, '$options': 'i'}}
            ]
        })
        return await cursor.to_list(length=100)

    async def total_files(self):
        return await self.file_data.count_documents({})

    async def delete_all_files(self):
        return await self.file_data.delete_many({})

    async def delete_specific_files(self, query):
        import re
        query_words = query.split()
        regex_pattern = "".join([f"(?=.*{re.escape(word)})" for word in query_words])

        return await self.file_data.delete_many({
            '$or': [
                {'file_name': {'$regex': regex_pattern, '$options': 'i'}},
                {'caption': {'$regex': regex_pattern, '$options': 'i'}}
            ]
        })

    # ONGOING SERIES DATA
    async def add_ongoing(self, title, season, language, release_day, total_eps, current_ep, poster, qualities):
        data = {
            'title': title,
            'season': season,
            'language': language,
            'release_day': release_day,
            'total_eps': total_eps,
            'current_ep': current_ep,
            'poster': poster,
            'qualities': qualities
        }
        await self.ongoing_data.update_one({'title': title}, {'$set': data}, upsert=True)

    async def get_ongoing(self, title):
        return await self.ongoing_data.find_one({'title': title})

    async def update_ongoing_ep(self, title, new_ep):
        await self.ongoing_data.update_one({'title': title}, {'$set': {'current_ep': new_ep}})

    async def get_all_ongoing(self):
        return await self.ongoing_data.find().to_list(length=None)

    async def del_ongoing(self, title):
        await self.ongoing_data.delete_one({'title': title})

    async def total_ongoing_count(self):
        return await self.ongoing_data.count_documents({})

    # SETTINGS MANAGEMENT
    async def get_settings(self):
        from config import SHORTLINK_URL, SHORTLINK_API, PROTECT_CONTENT
        default_settings = {
            'shortlink_url': SHORTLINK_URL,
            'shortlink_api': SHORTLINK_API,
            'is_shortlink': True if (SHORTLINK_URL and SHORTLINK_API) else False,
            'protect_content': PROTECT_CONTENT
        }

        settings = await self.settings_data.find_one({'_id': 'global_settings'})
        if not settings:
            await self.settings_data.insert_one({'_id': 'global_settings', 'value': default_settings})
            return default_settings

        # Merge saved settings with defaults to ensure all keys exist
        saved_values = settings.get('value', {})
        for key, val in default_settings.items():
            if key not in saved_values:
                saved_values[key] = val
        return saved_values

    async def update_setting(self, key, value):
        settings = await self.get_settings()
        settings[key] = value
        await self.settings_data.update_one(
            {'_id': 'global_settings'},
            {'$set': {'value': settings}},
            upsert=True
        )

    # SCHEDULER DATA
    async def add_to_sched_queue(self, query):
        await self.sched_queue_data.insert_one({
            'query': query,
            'added_at': time.time(),
            'status': 'pending'
        })

    async def get_sched_queue(self):
        return await self.sched_queue_data.find({'status': 'pending'}).sort('added_at', 1).to_list(length=None)

    async def remove_from_sched_queue(self, query_id):
        from bson.objectid import ObjectId
        await self.sched_queue_data.delete_one({'_id': ObjectId(query_id)})

    async def clear_sched_queue(self):
        await self.sched_queue_data.delete_many({})

    async def get_next_sched_item(self):
        return await self.sched_queue_data.find_one_and_update(
            {'status': 'pending'},
            {'$set': {'status': 'processing'}},
            sort=[('added_at', 1)]
        )

    async def mark_sched_done(self, query_id):
        await self.sched_queue_data.update_one({'_id': query_id}, {'$set': {'status': 'done'}})

    async def get_sched_config(self):
        from config import POST_CHANNEL_ID
        config = await self.sched_config_data.find_one({'_id': 'sched_config'})
        if not config:
            default = {
                '_id': 'sched_config',
                'is_active': False,
                'interval': 10800, # 3 hours
                'last_post_time': 0,
                'target_channel': POST_CHANNEL_ID
            }
            await self.sched_config_data.insert_one(default)
            return default
        return config

    async def update_sched_config(self, key, value):
        await self.sched_config_data.update_one(
            {'_id': 'sched_config'},
            {'$set': {key: value}},
            upsert=True
        )


db = Rohit(DB_URI, DB_NAME)
