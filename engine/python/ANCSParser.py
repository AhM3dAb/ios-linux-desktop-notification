import struct
from bisturi.packet import Packet
from bisturi.field  import Int, Data, Bits
import requests
import json
import sqlite3
import base64

NOTIFICATION_CATEGORIES = (
    "Other",
    "IncomingCall",
    "MissedCall",
    "Voicemail",
    "Social",
    "Schedule",
    "Email",
    "News",
    "HealthAndFitness",
    "BusinessAndFinance",
    "Location",
    "Entertainment",
)
# App Name	| Bundle ID
# ---------------------------------
# Activity	| com.apple.Fitness
# App Store	| com.apple.AppStore
# Apple Store 	| com.apple.store.Jolly
# Books		| com.apple.iBooks
# Calculator	| com.apple.calculator
# Calendar	| com.apple.mobilecal
# Camera		| com.apple.camera
# Clips		| com.apple.clips
# Clock		| com.apple.mobiletimer
# Compass		| com.apple.compass
# Contacts	| com.apple.MobileAddressBook
# FaceTime	| com.apple.facetime
# Files 	    	| com.apple.DocumentsApp
# Find My		| com.apple.findmy
# GarageBand	| com.apple.mobilegarageband
# Health		| com.apple.Health
# Home		| com.apple.Home
# iCloud Drive	| com.apple.iCloudDriveApp
# iMovie		| com.apple.iMovie
# iTunes Store	| com.apple.MobileStore
# iTunes U	| com.apple.itunesu
# Mail		| com.apple.mobilemail
# Maps		| com.apple.Maps
# Messages	| com.apple.MobileSMS
# Measure		| com.apple.measure
# Music		| com.apple.Music
# News		| com.apple.news
# Notes		| com.apple.mobilenotes
# Phone		| com.apple.mobilephone
# Photos		| com.apple.mobileslideshow
# Photo Booth 	| com.apple.Photo-Booth
# Podcasts	| com.apple.podcasts
# Reminders	| com.apple.reminders
# Safari		| com.apple.mobilesafari
# Settings	| com.apple.Preferences
# Shortcuts	| com.apple.shortcuts
# Stocks		| com.apple.stocks
# Tips		| com.apple.tips
# TV		| com.apple.tv
# Videos		| com.apple.videos
# Voice Memos	| com.apple.VoiceMemos
# Wallet		| com.apple.Passbook
# Watch		| com.apple.Bridge
# Weather		| com.apple.weather
SYSTEM_BUNDLEID = {
    "com.apple.Fitness":"Activity",
    "com.apple.AppStore":"App Store",
    "com.apple.store.Jolly":"Apple Store",
    "com.apple.iBooks":"Books",
    "com.apple.calculator":"Calculator",
    "com.apple.mobilecal":"Calendar",
    "com.apple.camera":"Camera",
    "com.apple.clips":"Clips",
    "com.apple.mobiletimer":"Clock",
    "com.apple.compass":"Compass",
    "com.apple.MobileAddressBook":"Contacts",
    "com.apple.facetime":"FaceTime",
    "com.apple.DocumentsApp":"Files",
    "com.apple.findmy":"Find My",
    "com.apple.mobilegarageband":"GarageBand",
    "com.apple.Health":"Health",
    "com.apple.Home":"Home",
    "com.apple.iCloudDriveApp":"iCloud Drive",
    "com.apple.iMovie":"iMovie",
    "com.apple.MobileStore":"iTunes Store",
    "com.apple.itunesu":"iTunes U",
    "com.apple.mobilemail":"Mail",
    "com.apple.Maps":"Maps",
    "com.apple.MobileSMS":"Messages",
    "com.apple.measure":"Measure",
    "com.apple.Music":"Music",
    "com.apple.news":"News",
    "com.apple.mobilenotes":"Notes",
    "com.apple.mobilephone":"Phone",
    "com.apple.mobileslideshow":"Photos",
    "com.apple.Photo-Booth":"Photo Booth",
    "com.apple.podcasts":"Podcasts",
    "com.apple.reminders":"Reminders",
    "com.apple.mobilesafari":"Safari",
    "com.apple.Preferences":"Settings",
    "com.apple.shortcuts":"Shortcuts",
    "com.apple.stocks":"Stocks",
    "com.apple.tips":"Tips",
    "com.apple.tv":"TV",
    "com.apple.videos":"Videos",
    "com.apple.VoiceMemos":"Voice Memos",
    "com.apple.Passbook":"Wallet",
    "com.apple.Bridge":"Watch",
    "com.apple.weatherpp":"Weather"
}
def readSqliteTable(bundleId):
    try:
        sqliteConnection = sqlite3.connect('cache.db')
        cursor = sqliteConnection.cursor()

        sqlite_select_query = "SELECT * from cachemeta WHERE bundleId=?"
        cursor.execute(sqlite_select_query,(bundleId,))
        records = cursor.fetchall()
        if len(records) < 1:
            cursor.close()
            return False
        cursor.close()
        return records

    except sqlite3.Error as error:
        print("Failed to read data from sqlite table", error)
    finally:
        if (sqliteConnection):
            sqliteConnection.close()

def get_app_metadata(bundleId):
    exist = readSqliteTable(bundleId)
    if exist is False:
        url_string = "http://itunes.apple.com/lookup?bundleId=" + bundleId
        response = requests.get(url_string)
        return response.content
    else:
        return exist

def name_from_bundle_id(metadata):
    if type(metadata) is list:
        return metadata[0][1]
    data = json.loads(metadata)
    return data["results"][0]["trackName"]

def icon_from_bundle_id(metadata):
    if type(metadata) is list:
        return metadata[0][2], metadata[0][3]
    data = json.loads(metadata)
    url = data["results"][0]["artworkUrl60"]
    r = requests.get(url, allow_redirects=True)
    content_type = r.headers["content-type"]
    encoded_body = base64.b64encode(r.content)
    base64_img = "data:{};base64,{}".format(content_type, encoded_body.decode())
    base64_img_x = encoded_body.decode()
    ext = content_type.split("/")
    filename = data["results"][0]["trackName"] + "." + ext[1]
    return base64_img_x, filename

def save_to_cache(bundleId, appname, filename, base64_img):
    try:
        sqliteConnection = sqlite3.connect('cache.db')
        cursor = sqliteConnection.cursor()

        sqlite_insert_query = "INSERT INTO cachemeta (bundleId, appname, base64img, filename) VALUES (?, ?, ?, ?)"

        count = cursor.execute(sqlite_insert_query,(bundleId, appname, base64_img, filename))
        sqliteConnection.commit()
        cursor.close()

    except sqlite3.Error as error:
        print("Failed to insert data into sqlite table", error)
    finally:
        if (sqliteConnection):
            sqliteConnection.close()


class TypeLengthValue(Packet):
    type   = Int(1)
    length = Int(2, endianness='little')
    value  = Data(length)

class Notification:
    id = 0
    removed = False
    """True when the notification has been cleared on the iOS device."""
    silent = False
    important = False
    preexisting = False
    """True if the notification existed before we connected to the iOS device."""
    positive_action = False
    """True if the notification has a positive action to respond with. For example, this could
       be answering a phone call."""
    negative_action = False
    """True if the notification has a negative action to respond with. For example, this could
       be declining a phone call."""
    category_count = 0
    """Number of other notifications with the same category."""
    category_id = 0
    #EventID: This field informs the accessory whether the given iOS notification was added, modified, or removed.
    #The enumerated values for this field are defined in EventID Values.
    event_id = None #1 byte
    #A bitmask whose set bits inform an NC of specificities with the iOS notification.
    #The enumerated bits for this field are defined in EventFlags.
    event_flags = None #1 byte
    flags = []
    #A numerical value providing a category in which the iOS notification can be classified.
    #The NP will make a best effort to provide an accurate category for each iOS notification.
    #The enumerated values for this field are defined in CategoryID Values.
    category_id = None #1 byte
    category = None
    #The current number of active iOS notifications in the given category.
    #For example, if two unread emails are sitting in a user’s email inbox, and a new email is pushed to the user’s iOS device, the value of CategoryCount is 3.
    category_count = None #1 byte
    #A 32-bit numerical value that is the unique identifier (UID) for the iOS notification.
    #This value can be used as a handle in commands sent to the Control Point characteristic to interact with the iOS notification.
    notification_id = None #4 byte (int)
    notification_src_id = None #4 byte (int) from response

    notification_attributes_cache = {}
    application_name = None
    application_icon = None
    application_icon_base64 = None
    app_id = None
    """String id of the app that generated the notification. It is not the name of the app. For
       example, Slack is "com.tinyspeck.chatlyio" and Twitter is "com.atebits.Tweetie2"."""

    title = None
    """Title of the notification. Varies per app."""

    subtitle = None
    """Subtitle of the notification. Varies per app."""

    message = None
    """Message body of the notification. Varies per app."""

    message_size = None
    """Total length of the message string."""

    _raw_date = None
    positive_action_label = None
    """Human readable label of the positive action."""

    negative_action_label = None
    """Human readable label of the negative action."""

    def __init__(
        self,
        #the ANCS exposes three characteristics:
        #Notification Source: UUID 9FBF120D-6301-42D9-8C58-25E699A21DBD (notifiable)
        #Control Point: UUID 69D1D8F3-45E1-49A8-9821-9BBDFDAAD9D9 (writeable with response)
        #Data Source: UUID 22EAC6E9-24D6-4BB5-BE44-B36ACE7C7BFB (notifiable)

        #GATT notification delivered through a Notification Source characteristic
        value,
        Source,
    ):
        self.value = value
        self.dataSource = Source

        if self.dataSource is False:
            # Notification from NS
            self.event_id, self.event_flags, self.category_id, self.category_count, self.notification_id = struct.unpack("<BBBBI", self.value)
            self.update(self.event_flags, self.category_id, self.category_count)
            if self.event_id  == 2:
                del self.notification_attributes_cache[str(self.notification_id)]
            else:
                self.notification_attributes_cache.update({str(self.notification_id) : {'event_id': self.event_id, 'event_flags': self.flags, 'category':self.category, 'category_count': self.category_count, 'data':[]}})
        else:
            self.notification_src_id, self.application_name, self.application_icon, self.application_icon_base64, self.app_id, self.title, self.subtitle, self.message, self.message_size, self._raw_date, self.positive_action_label, self.negative_action_label = self.notificationAttribute(self.value)
            self.notification_src_id = struct.unpack("<I", self.notification_src_id)[0]
            self.notification_attributes_cache[str(self.notification_src_id)]['data'].append({'app_id':self.app_id.decode("utf-8"), 'app_name':self.application_name, 'app_icon_name':self.application_icon, 'app_icon_base64': self.application_icon_base64, 'title':self.title.decode("utf-8"), 'subtitle':self.subtitle.decode("utf-8"), 'message':self.message.decode("utf-8"), 'message_size':self.message_size.decode("utf-8"), 'date':self._raw_date.decode("utf-8"), 'positive_action_label':self.positive_action_label.decode("utf-8"), 'negative_action_label':self.negative_action_label.decode("utf-8")})


    def update(self, ev_flags, cat_id, cat_count):
        """Update the notification and clear the attribute cache."""
        self.category_id = cat_id
        self.event_flags = ev_flags
        self.category_count = cat_count

        self.silent = (self.event_flags & (1 << 0)) != 0
        self.important = (self.event_flags & (1 << 1)) != 0
        self.preexisting = (self.event_flags & (1 << 2)) != 0
        self.positive_action = (self.event_flags & (1 << 3)) != 0
        self.negative_action = (self.event_flags & (1 << 4)) != 0
        if self.category_id < len(NOTIFICATION_CATEGORIES):
            self.category = NOTIFICATION_CATEGORIES[self.category_id]
        else:
            self.category = "Reserved"
        self.flags = []
        if self.silent:
            self.flags.append("silent")
        if self.important:
            self.flags.append("important")
        if self.preexisting:
            self.flags.append("preexisting")
        if self.positive_action:
            self.flags.append("positive_action")
        if self.negative_action:
            self.flags.append("negative_action")

    def getNotificationAttributes(self):
        return  self.notification_id, self.flags

    def getEventId(self):
        return self.event_id

    def getNotificationSourceAttributes(self):
        return self.notification_attributes_cache

    def notificationAttribute(self, value):
        mutable_bytes = bytearray(value)
        self.notification_src_id = bytes(mutable_bytes[1:5])
        del mutable_bytes[0:5]
        tlv = TypeLengthValue.unpack(bytes(mutable_bytes))
        self.app_id = tlv.value
        del mutable_bytes[0:3+tlv.length]
        tlv = TypeLengthValue.unpack(bytes(mutable_bytes))
        self.title = tlv.value
        del mutable_bytes[0:3+tlv.length]
        tlv = TypeLengthValue.unpack(bytes(mutable_bytes))
        self.subtitle = tlv.value
        del mutable_bytes[0:3+tlv.length]
        tlv = TypeLengthValue.unpack(bytes(mutable_bytes))
        self.message = tlv.value
        del mutable_bytes[0:3+tlv.length]
        tlv = TypeLengthValue.unpack(bytes(mutable_bytes))
        self.message_size = tlv.value
        del mutable_bytes[0:3+tlv.length]
        tlv = TypeLengthValue.unpack(bytes(mutable_bytes))
        self._raw_date = tlv.value
        del mutable_bytes[0:3+tlv.length]
        tlv = TypeLengthValue.unpack(bytes(mutable_bytes))
        self.positive_action_label = tlv.value
        del mutable_bytes[0:3+tlv.length]
        tlv = TypeLengthValue.unpack(bytes(mutable_bytes))
        self.negative_action_label = tlv.value
        application_metadata = get_app_metadata(self.app_id.decode("utf-8"))
        self.application_name = name_from_bundle_id(application_metadata)
        self.application_icon_base64, self.application_icon = icon_from_bundle_id(application_metadata)
        if type(application_metadata) is not list:
            save_to_cache(self.app_id.decode("utf-8"), self.application_name, self.application_icon, self.application_icon_base64)

        return self.notification_src_id, self.application_name, self.application_icon, self.application_icon_base64, self.app_id, self.title, self.subtitle, self.message, self.message_size, self._raw_date, self.positive_action_label, self.negative_action_label
