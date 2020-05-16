import json
import apiai
import os
from flask import Flask, redirect, render_template, request, url_for
from twilio.rest import Client
from twilio.http.http_client import TwilioHttpClient

from flask import make_response, jsonify

# for encryption
from cryptography.fernet import Fernet
# import base64


# Twilio account info
account_sid = "AC4a47c64a6cc99b38f419073a3cf80a0b"
auth_token = "f8c108c338700a7a92b0e2d062cc6929"
account_num = "+12133206669"

proxy_client = TwilioHttpClient()
proxy_client.session.proxies = {'https': os.environ['https_proxy']}

client = Client(account_sid, auth_token, http_client=proxy_client)

# api.ai account info
CLIENT_ACCESS_TOKEN = "76eab3a1fa9e4a3497affdbc061e3bc5"
ai = apiai.ApiAI(CLIENT_ACCESS_TOKEN)

app = Flask(__name__)

app.config["DEBUG"] = True # added after adding template - to debug


# ----------------------------------------------------------------------------------------------database handling starts-----------------------------------------------------------------------------------------------------
# create a MySQL client connecting to your MySQL server
import mysql.connector
mydb = mysql.connector.connect(
  host="sanyasin.mysql.pythonanywhere-services.com",
  user="sanyasin",
  passwd="mysql_password",
  database="sanyasin$chatbot"
)
mycursor = mydb.cursor()

mycursor.execute("DROP TABLE IF EXISTS Patients")
mycursor.execute("drop view if exists user_pass_credentials")
mycursor.execute("drop view if exists Headache")
mycursor.execute("drop view if exists Medication")
mycursor.execute("drop view if exists Personal_view_details")
mycursor.execute("drop table if exists PatientDetails")
mycursor.execute("drop table if exists keysss")
mycursor.execute("drop table if exists save_entries")

mycursor.execute("drop table if exists WOW_before")
mycursor.execute("drop table if exists WOW_after")

# Patients - table - will store all the necessary values that are supposed to be recorded
mycursor.execute("CREATE TABLE Patients (id int primary key auto_increment, username varchar(1000), password varchar(1000), created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, headache_name varchar(200), wakeupornot varchar(200), durationofheadache varchar(200), recordseverity varchar(200), timeshappenedsinceyouwokeup varchar(200), if_female varchar(200), usc_facility varchar(200), medicinename varchar(200), totalpills varchar(200), severity_prior_to_medication varchar(200), email varchar(60), phone varchar(60), fname varchar(60), lname varchar(60), secondary_email varchar(60), gender varchar(60)) ENGINE=InnoDB")
mycursor.execute("create table save_entries (id int primary key auto_increment, username varchar(1000), password varchar(1000), created_at varchar(1000), headache_name varchar(1000), wakeupornot varchar(200), durationofheadache varchar(200), recordseverity varchar(200), timeshappenedsinceyouwokeup varchar(200), if_female varchar(200), usc_facility varchar(200), medicinename varchar(200), totalpills varchar(200), severity_prior_to_medication varchar(200), email varchar(60), phone varchar(60), fname varchar(60), lname varchar(60), secondary_email varchar(60), gender varchar(60))")



# TABLES FOR EXTRA CREDIT 3
mycursor.execute("drop table if exists Patients_Extra_Credit")
mycursor.execute("drop table if exists Headache_Extra_Credit")
mycursor.execute("drop table if exists Medication_Extra_Credit")
mycursor.execute("drop table if exists Systems_Extra_Credit")
mycursor.execute("drop table if exists Activities_Extra_Credit")
mycursor.execute("drop table if exists Chatbot_Extra_Credit")
mycursor.execute("drop table if exists Question_Extra_Credit")
mycursor.execute("drop table if exists TransitionTo_Extra_Credit")
mycursor.execute("drop table if exists ResponseTo_ExtraCredit")
mycursor.execute("drop table if exists MDerivedFrom_Extra_Credit")
mycursor.execute("drop table if exists HDerivedFrom_Extra_Credit")


mycursor.execute("create table Patients_Extra_Credit (Email varchar(100), Phone varchar(100), FName varchar(100), LName varchar(100), SecondaryEmail varchar(100), Password varchar(100), Gender varchar(100))")
mycursor.execute("create table Headache_Extra_Credit (HeadacheID int auto_increment primary key, PatientEmail varchar(100), HeadacheName varchar(100), Timestamp timestamp default current_timestamp, Doctor varchar(100), WokeupWith varchar(100), Severity varchar(100), Duration varchar(100), Facility varchar(100), MCycle varchar(100))")
mycursor.execute("create table Medication_Extra_Credit (MedicationID int auto_increment primary key, PatientEmail varchar(100), MedicationName varchar(100), Timestamp timestamp default current_timestamp, NumberOfPills int)")
mycursor.execute("create table Systems_Extra_Credit (PatientEmail varchar(100), ActivityName varchar(100), Description varchar(100))")
mycursor.execute("create table Activities_Extra_Credit (PatientEmail varchar(100), ActivityName varchar(100), Timestamp timestamp default current_timestamp)")
mycursor.execute("create table Chatbot_Extra_Credit (ChatbotName varchar(100), ChatbotVersionID varchar(100), PublicationDate varchar(100), StartQID int)")

mycursor.execute("create table Question_Extra_Credit (QID int, ChatbotName varchar(100), ChatbotVersionID varchar(100), Query varchar(1000))")
mycursor.execute("insert into Question_Extra_Credit values (1, 'Helix Chatbot', 'dialogflow v2.0', 'Do you have a headache?'), (2, 'Helix Chatbot', 'dialogflow v2.0', 'Are you reporting a headache you had?'), (3, 'Helix Chatbot', 'dialogflow v2.0', 'Are you reporting a medication you took?'), (4, 'Helix Chatbot', 'dialogflow v2.0', 'Have a wonderful day!'), (5, 'Helix Chatbot', 'dialogflow v2.0', 'What name do you give this headache?'), (6, 'Helix Chatbot', 'dialogflow v2.0', 'Did you wake up with this headache?'), (7, 'Helix Chatbot', 'dialogflow v2.0', 'What is/was the duration of your headache?'), (8, 'Helix Chatbot', 'dialogflow v2.0', 'How severe is your headache?'), (9, 'Helix Chatbot', 'dialogflow v2.0', 'How many times has it happened since you woke up?'), (10, 'Helix Chatbot', 'dialogflow v2.0', 'For this headache  did you take medication?'), (11, 'Helix Chatbot', 'dialogflow v2.0', 'What medication was it?'), (12, 'Helix Chatbot', 'dialogflow v2.0', 'How many pills?'), (13, 'Helix Chatbot', 'dialogflow v2.0', 'Did this medication help your headache?'), (14, 'Helix Chatbot', 'dialogflow v2.0', 'How severe was your headache prior to medication?'), (15, 'Helix Chatbot', 'dialogflow v2.0', 'Did you experience another form of headache?'), (16, 'Helix Chatbot', 'dialogflow v2.0', 'If female are you in the middle of or close to your menstruction cycle?'), (17, 'Helix Chatbot', 'dialogflow v2.0', 'Did you have to go to a physician for this headache?'), (18, 'Helix Chatbot', 'dialogflow v2.0', 'Was it a USC facility?'), (19, 'Helix Chatbot', 'dialogflow v2.0', 'Thank you for recording your headache. You may always review and edit your current or previous response.')")

mycursor.execute("create table TransitionTo_Extra_Credit (ChatbotName varchar(100), ChatbotVersionID varchar(100), QID1 int, QID2 int, Response varchar(100))")
mycursor.execute("create table ResponseTo_ExtraCredit (QID1 int, QID2 int, PatientEmail varchar(100), ActivityName varchar(100), Timestamp timestamp default current_timestamp, Response varchar(100))")
mycursor.execute("create table MDerivedFrom_Extra_Credit (QID1 int, QID2 int, PatientEmail varchar(100), ActivityName varchar(100), Timestamp timestamp default current_timestamp, MedicationID int)")
mycursor.execute("create table HDerivedFrom_Extra_Credit (QID1 int, QID2 int, PatientEmail varchar(100), ActivityName varchar(100), Timestamp timestamp default current_timestamp, HeadacheID int)")


Patients_ec_hashmap = {}
Headache_ec_hashmap = {}
Medication_ec_hashmap = {}
Systems_ec_hashmap = {}
Activities_ec_hashmap = {}
Chatbot_ec_hashmap = {}
TransitionTo_ec_hashmap = {}
ResponseTo_ec_hashmap = {}
MDerivedFrom_ec_hashmap = {}
HDerivedFrom_ec_hashmap = {}

Patients_ec_hashmap['Email'] = 'null'
Patients_ec_hashmap['Phone'] = 'null'
Patients_ec_hashmap['FName'] = 'null'
Patients_ec_hashmap['LName'] = 'null'
Patients_ec_hashmap['SecondaryEmail'] = 'null'
Patients_ec_hashmap['Password'] = 'null'
Patients_ec_hashmap['Gender'] = 'null'

Headache_ec_hashmap['PatientEmail'] = 'null'
Headache_ec_hashmap['HeadacheName'] = 'null'
Headache_ec_hashmap['Doctor'] = 'null'
Headache_ec_hashmap['WokeupWith'] = 'null'
Headache_ec_hashmap['Severity'] = 'null'
Headache_ec_hashmap['Duration'] = 'null'
Headache_ec_hashmap['Facility'] = 'null'
Headache_ec_hashmap['MCycle'] = 'null'

Medication_ec_hashmap['PatientEmail'] = 'null'
Medication_ec_hashmap['MedicationName'] = 'null'
Medication_ec_hashmap['NumberOfPills'] = 'null'

Systems_ec_hashmap['PatientEmail'] = 'null'
Systems_ec_hashmap['ActivityName'] = 'null'
Systems_ec_hashmap['Description'] = 'null'

Activities_ec_hashmap['PatientEmail'] = 'null'
Activities_ec_hashmap['ActivityName'] = 'null'

Chatbot_ec_hashmap['ChatbotName'] = 'null'
Chatbot_ec_hashmap['ChatbotVersionID'] = 'null'
Chatbot_ec_hashmap['PublicationDate'] = 'null'
Chatbot_ec_hashmap['StartQID'] = 'null'

TransitionTo_ec_hashmap['ChatbotName'] = 'null'
TransitionTo_ec_hashmap['ChatbotVersionID'] = 'null'
TransitionTo_ec_hashmap['QID1'] = 'null'
TransitionTo_ec_hashmap['QID2'] = 'null'
TransitionTo_ec_hashmap['Response'] = 'null'

ResponseTo_ec_hashmap['QID1'] = 'null'
ResponseTo_ec_hashmap['QID2'] = 'null'
ResponseTo_ec_hashmap['PatientEmail'] = 'null'
ResponseTo_ec_hashmap['ActivityName'] = 'null'
ResponseTo_ec_hashmap['Response'] = 'null'

MDerivedFrom_ec_hashmap['QID1'] = 'null'
MDerivedFrom_ec_hashmap['QID2'] = 'null'
MDerivedFrom_ec_hashmap['PatientEmail'] = 'null'
MDerivedFrom_ec_hashmap['ActivityName'] = 'null'
MDerivedFrom_ec_hashmap['MedicationID'] = 'null'

HDerivedFrom_ec_hashmap['QID1'] = 'null'
HDerivedFrom_ec_hashmap['QID2'] = 'null'
HDerivedFrom_ec_hashmap['PatientEmail'] = 'null'
HDerivedFrom_ec_hashmap['ActivityName'] = 'null'
HDerivedFrom_ec_hashmap['HeadacheID'] = 'null'


Systems_ec_hashmap['ActivityName'] = "Headache Query"
Systems_ec_hashmap['Description'] = "Insertion in system's table"
Activities_ec_hashmap['ActivityName'] = "Headache Query"
ResponseTo_ec_hashmap['ActivityName'] = "Headache Query"
HDerivedFrom_ec_hashmap['ActivityName'] = "Headache Query"
MDerivedFrom_ec_hashmap['ActivityName'] = "Headache Query"
Chatbot_ec_hashmap['ChatbotName'] = "Helix chatbot"
Chatbot_ec_hashmap['ChatbotVersionID'] = "dialogflow v2.0"
Chatbot_ec_hashmap['PublicationDate'] = "May 9th, 2020"
TransitionTo_ec_hashmap['ChatbotName'] = "Helix chatbot"
TransitionTo_ec_hashmap['ChatbotVersionID'] = "dialogflow v2.0"



# thread locks for storing the values in hashmap/dictionary while maintaining the concurrency
import threading
lock = threading.Lock()

hashmap = {} # values in 'Patients' table

# acquiring locks - hashmap's not gonna update
# maintaining atomicity, consistency, isolation and durability [acid properties]
lock.acquire()


contain_usernames_only = {} # username -> id
counting_id = 0
qid_counter = 0
startQueryNumber = 0
patient_details = {} # personal details
encrypted_hashmap = {} # username -> encrypted key [encryption]

admin_usernames = [] # admin_username -> admin_password [authenticated] -> only this person can log in to the admin portal - length will determine number of administrators
usernames_array = [] # have only usernames

id_hashmap_array = {} # id -> [----] contain hashmap values-an array-in sequence
admin_usernames.append("sanyasin")


#dictionaries for graphs
usernames_headaches_intensity = {} # {username -> {headache -> intensity}}
usernames_timestamp_intensity = {} # {username -> {timestamp -> internsity}}
usernames_timestamp_totalheads = {} # {username -> {timestamp -> totalheads}}





# ---------------------------------------------------------------------------------------------------webhook method calling----------------------------------------------------------------------------------------------
@app.route('/webhook', methods=['GET', 'POST']) # '/' - this is explained/used by action keyword from html code
def webhook():
    global counting_id # for maintaining the data of each user in the Patients table
    global qid_counter # for counting queries - sequential wise - as user was asked
    global startQueryNumber
    req = request.get_json(silent=True, force=True)
    action = req.get('queryResult').get('action')


    # -----------------------------------------------------------------------------------------configuring api.ai - EXTRA CREDIT - 3---------------------------------------------------------------------
    fft = req.get('queryResult').get('fulfillmentText')
    if fft == 'Thanks for logging in with your credentials. You can start reporting now! Do you have a headache?':
        startQueryNumber += 1
        TransitionTo_ec_hashmap['QID1'] = startQueryNumber
        ResponseTo_ec_hashmap['QID1'] = startQueryNumber
        MDerivedFrom_ec_hashmap['QID1'] = startQueryNumber
        HDerivedFrom_ec_hashmap['QID1'] = startQueryNumber

    if fft == 'What name do you give this headache?' or fft == 'Are you reporting a headache you had?' or fft == 'Are you reporting a medication you took?' or fft == 'Have a wonderful day!' or fft == 'Did you wake up with this headache?' or fft == 'What is/was the duration of your headache?' or fft == 'How severe is your headache?' or fft == 'How many times has it happened since you wokeup?' or fft == 'For this headache, did you take medication?' or fft == 'What medication was it?' or fft == 'How many pills?' or fft == 'Did this medication help your headache?' or fft == 'How severe was your headache prior to medication?' or fft == 'Did you experience another form of headache?' or fft == 'Enter anything to continue!!!' or fft == 'Are you in the middle or close to your menstruation cycle?' or fft == 'Did you have to go to a physician for this headache?' or fft == 'Was it a USC facility?' or fft == 'Thank you for recording your headache. You may always review and edit your current or previous response.':
        startQueryNumber += 1
        TransitionTo_ec_hashmap['QID2'] = startQueryNumber
        response_answer = req.get('queryResult').get('queryText')
        TransitionTo_ec_hashmap['Response'] = response_answer

        a1 =', '.join(['%s'] * len(TransitionTo_ec_hashmap))
        b1 = ', '.join(TransitionTo_ec_hashmap.keys())
        qry = "insert into TransitionTo_Extra_Credit ( %s ) values ( %s )" % (b1, a1)
        mycursor.execute(qry, list(TransitionTo_ec_hashmap.values()))

        TransitionTo_ec_hashmap['QID1'] = startQueryNumber


        ResponseTo_ec_hashmap['QID2'] = startQueryNumber
        ResponseTo_ec_hashmap['Response'] = response_answer

        a2 =', '.join(['%s'] * len(ResponseTo_ec_hashmap))
        b2 = ', '.join(ResponseTo_ec_hashmap.keys())
        qry = "insert into ResponseTo_ExtraCredit ( %s ) values ( %s )" % (b2, a2)
        mycursor.execute(qry, list(ResponseTo_ec_hashmap.values()))

        ResponseTo_ec_hashmap['QID1'] = startQueryNumber


        MDerivedFrom_ec_hashmap['QID2'] = startQueryNumber
        MDerivedFrom_ec_hashmap['MedicationID'] = counting_id

        a3 =', '.join(['%s'] * len(MDerivedFrom_ec_hashmap))
        b3 = ', '.join(MDerivedFrom_ec_hashmap.keys())
        qry = "insert into MDerivedFrom_Extra_Credit ( %s ) values ( %s )" % (b3, a3)
        mycursor.execute(qry, list(MDerivedFrom_ec_hashmap.values()))

        MDerivedFrom_ec_hashmap['QID1'] = startQueryNumber


        HDerivedFrom_ec_hashmap['QID2'] = startQueryNumber

        a4 =', '.join(['%s'] * len(HDerivedFrom_ec_hashmap))
        b4 = ', '.join(HDerivedFrom_ec_hashmap.keys())
        qry = "insert into HDerivedFrom_Extra_Credit ( %s ) values ( %s )" % (b4, a4)
        mycursor.execute(qry, list(HDerivedFrom_ec_hashmap.values()))

        HDerivedFrom_ec_hashmap['QID1'] = startQueryNumber


    # -----------------------------------------------------------------------------------------------basic action if statements-------------------------------------------------------------------------
    if action == 'saving_username':
        counting_id += 1    # getting last id number

        # starting transaction --- from here onwards ---
        # mycursor.execute("start transaction")

        # don't change the sequence - built array on this sequence
        hashmap['username'] = 'null'
        hashmap['password'] = 'null'
        hashmap['headache_name'] = 'null'
        hashmap['wakeupornot'] = 'null'
        hashmap['durationofheadache'] = 'null'
        hashmap['recordseverity'] = 'null'
        hashmap['timeshappenedsinceyouwokeup'] = 'null'
        hashmap['if_female'] = 'null'
        hashmap['usc_facility'] = 'null'
        hashmap['medicinename'] = 'null'
        hashmap['totalpills'] = 'null'
        hashmap['severity_prior_to_medication'] = 'null'
        hashmap['email'] = 'null'
        hashmap['phone'] = 'null'
        hashmap['fname'] = 'null'
        hashmap['lname'] = 'null'
        hashmap['secondary_email'] = 'null'
        hashmap['gender'] = 'null'

        p = req.get('queryResult').get('parameters').get('username')
        hashmap["username"] = p


        # for encryption - store in dictionaries - select that attribute that cannot be changed - "username"
        temp = p
        message = temp.encode()
        key = Fernet.generate_key()
        f = Fernet(key)
        encrypted = f.encrypt(message)
        encrypted_hashmap[p] = encrypted
        # decrypted = f.decrypt(encrypted)

        MDerivedFrom_ec_hashmap['MedicationID'] = counting_id
        HDerivedFrom_ec_hashmap['HeadacheID'] = counting_id

        # checking username - already present in the database or not
        if p in contain_usernames_only:

            # mycursor.execute("create table WOW_before (id int auto_increment primary key)")

            # copy and storing in table "save_entries" [copy & paste] - storing past username/headaches entries details
            cpystatement = "insert into save_entries (id, username, password, created_at, headache_name, wakeupornot, durationofheadache, recordseverity, timeshappenedsinceyouwokeup, if_female, usc_facility, medicinename, totalpills, severity_prior_to_medication, email, phone, fname, lname, secondary_email, gender) select id, username, password, created_at, headache_name, wakeupornot, durationofheadache, recordseverity, timeshappenedsinceyouwokeup, if_female, usc_facility, medicinename, totalpills, severity_prior_to_medication, email, phone, fname, lname, secondary_email, gender from Patients where id = %s"
            id_val = contain_usernames_only[p]
            mycursor.execute(cpystatement, (id_val,))

            # mycursor.execute("create table WOW_after (id int auto_increment primary key)")


            # modify - delete, generate new id
            a = contain_usernames_only[p]
            delstatmt = "DELETE FROM Patients WHERE id = %s"
            mycursor.execute(delstatmt, (a,))


            contain_usernames_only[p] = counting_id
            res = "This username already exists. Log in with your password to update the details"
            return make_response(jsonify({"fulfillmentText": res}))

        else:

            contain_usernames_only[p] = counting_id
            res = "This username is not in the database. Let's sign you up! Enter your password "
            return make_response(jsonify({"fulfillmentText": res}))


    if action == 'saving_password':
        p = req.get('queryResult').get('parameters').get('password')
        hashmap["password"] = p
        Patients_ec_hashmap['Password'] = p

    if action == 'checking_gender':
        p = hashmap['gender']

        # checking for the gender specific question
        if p in ['female', 'Female', 'f', 'fem', 'F', 'girl', 'Girl', 'FEMALE', 'lady', 'Fem', 'fe male']:
            res = "Are you in the middle or close to your menstruation cycle?"
            return make_response(jsonify({"fulfillmentText": res}))
        else:
            res = "Enter anything to continue!!!"
            return make_response(jsonify({"fulfillmentText": res}))


    if action == 'saving_gender':
        p = req.get('queryResult').get('parameters').get('gender')
        hashmap["gender"] = p
        Patients_ec_hashmap['Gender'] = p

    if action == 'saving_email':
        p = req.get('queryResult').get('parameters').get('email')
        hashmap["email"] = p
        Patients_ec_hashmap['Email'] = p
        Headache_ec_hashmap['PatientEmail'] = p
        Medication_ec_hashmap['PatientEmail'] = p
        Systems_ec_hashmap['PatientEmail'] = p
        Activities_ec_hashmap['PatientEmail'] = p
        ResponseTo_ec_hashmap['PatientEmail'] = p
        MDerivedFrom_ec_hashmap['PatientEmail'] = p
        HDerivedFrom_ec_hashmap['PatientEmail'] = p

    if action == 'saving_phone':
        p = req.get('queryResult').get('parameters').get('phone')
        hashmap["phone"] = p
        Patients_ec_hashmap['Phone'] = p

    if action == 'saving_fname':
        p = req.get('queryResult').get('parameters').get('fname')
        hashmap["fname"] = p
        Patients_ec_hashmap['FName'] = p

    if action == 'saving_lname':
        p = req.get('queryResult').get('parameters').get('lname')
        hashmap["lname"] = p
        Patients_ec_hashmap['LName'] = p

    if action == 'saving_secondary_email':
        p = req.get('queryResult').get('parameters').get('secondary_email')
        hashmap["secondary_email"] = p
        Patients_ec_hashmap['SecondaryEmail'] = p

    if action == 'saving_headache_name':
        p = req.get('queryResult').get('parameters').get('headache_name')
        hashmap["headache_name"] = p
        Headache_ec_hashmap['HeadacheName'] = p
        qid_counter += 1
        Chatbot_ec_hashmap['StartQID'] = qid_counter


    if action == 'saving_wakeupornot':
        p = req.get('queryResult').get('parameters').get('wakeupornot')
        hashmap["wakeupornot"] = p
        Headache_ec_hashmap['WokeupWith'] = p
        qid_counter += 1

    if action == 'saving_durationofheadache':
        p = req.get('queryResult').get('parameters').get('durationofheadache')
        hashmap["durationofheadache"] = p
        Headache_ec_hashmap['Duration'] = p
        qid_counter += 1

    if action == 'saving_recordseverity':
        p = req.get('queryResult').get('parameters').get('recordseverity')
        hashmap["recordseverity"] = p
        Headache_ec_hashmap['Severity'] = p
        qid_counter += 1

        headache_name_variable = hashmap["headache_name"]
        username_variable = hashmap["username"]

        temp = {}
        temp[headache_name_variable] = p

        if username_variable in usernames_headaches_intensity:
            usernames_headaches_intensity[username_variable].append(temp)
        else:
            usernames_headaches_intensity[username_variable] = [temp]

    if action == 'saving_timeshappenedsinceyouwokeup':
        p = req.get('queryResult').get('parameters').get('timeshappenedsinceyouwokeup')
        hashmap["timeshappenedsinceyouwokeup"] = p
        qid_counter += 1

    if action == 'saving_medicinename':
        p = req.get('queryResult').get('parameters').get('medicinename')
        hashmap["medicinename"] = p
        Medication_ec_hashmap['MedicationName'] = p
        qid_counter += 1

    if action == 'saving_totalpills':
        p = req.get('queryResult').get('parameters').get('totalpills')
        hashmap["totalpills"] = p
        Medication_ec_hashmap['NumberOfPills'] = p
        qid_counter += 1

    if action == 'saving_severity_prior_to_medication':
        p = req.get('queryResult').get('parameters').get('severity_prior_to_medication')
        hashmap["severity_prior_to_medication"] = p
        qid_counter += 1

    if action == 'saving_if_female':
        p = req.get('queryResult').get('parameters').get('if_female')
        hashmap["if_female"] = p
        Headache_ec_hashmap['MCycle'] = p
        qid_counter += 1

    if action == 'saving_usc_facility':
        p = req.get('queryResult').get('parameters').get('usc_facility')
        hashmap["usc_facility"] = p
        Headache_ec_hashmap['Doctor'] = p
        Headache_ec_hashmap['Facility'] = p
        qid_counter += 1

        p = hashmap['gender']
        if p not in ['female', 'Female', 'f', 'fem', 'F', 'girl', 'Girl', 'FEMALE', 'lady', 'Fem', 'female']:
            hashmap['if_female'] = 'no'
            Headache_ec_hashmap['MCycle'] = 'No'


        # for k,v in contain_usernames_only.items():
        #     usernames_array.append(k)
        usernames_array.append(hashmap['username'])

        temp_array = [] # store hashmap values in sequence

        temp_array.append(hashmap['username'])
        temp_array.append(hashmap['password'])
        temp_array.append(hashmap['headache_name'])
        temp_array.append(hashmap['wakeupornot'])
        temp_array.append(hashmap['durationofheadache'])
        temp_array.append(hashmap['recordseverity'])
        temp_array.append(hashmap['timeshappenedsinceyouwokeup'])
        temp_array.append(hashmap['if_female'])
        temp_array.append(hashmap['usc_facility'])
        temp_array.append(hashmap['medicinename'])
        temp_array.append(hashmap['totalpills'])
        temp_array.append(hashmap['severity_prior_to_medication'])
        temp_array.append(hashmap['email'])
        temp_array.append(hashmap['phone'])
        temp_array.append(hashmap['fname'])
        temp_array.append(hashmap['lname'])
        temp_array.append(hashmap['secondary_email'])
        temp_array.append(hashmap['gender'])

        id_hashmap_array[counting_id] = temp_array


        #Patients table - inserting everything in one row ------------------------------------------ INSERTION IN [Patients] TABLE--------------------------------------------------
        qmarks =', '.join(['%s'] * len(hashmap))
        cols = ', '.join(hashmap.keys())
        qry = "insert into Patients ( %s ) values ( %s )" % (cols, qmarks)
        mycursor.execute(qry, list(hashmap.values()))

        ec1 =', '.join(['%s'] * len(Patients_ec_hashmap))
        cols1 = ', '.join(Patients_ec_hashmap.keys())
        sql_qry = "insert into Patients_Extra_Credit ( %s ) values ( %s )" % (cols1, ec1)
        mycursor.execute(sql_qry, list(Patients_ec_hashmap.values()))

        ec2 =', '.join(['%s'] * len(Headache_ec_hashmap))
        cols2 = ', '.join(Headache_ec_hashmap.keys())
        sql_qry = "insert into Headache_Extra_Credit ( %s ) values ( %s )" % (cols2, ec2)
        mycursor.execute(sql_qry, list(Headache_ec_hashmap.values()))

        ec3 =', '.join(['%s'] * len(Medication_ec_hashmap))
        cols3 = ', '.join(Medication_ec_hashmap.keys())
        sql_qry = "insert into Medication_Extra_Credit ( %s ) values ( %s )" % (cols3, ec3)
        mycursor.execute(sql_qry, list(Medication_ec_hashmap.values()))

        ec4 =', '.join(['%s'] * len(Systems_ec_hashmap))
        cols4 = ', '.join(Systems_ec_hashmap.keys())
        sql_qry = "insert into Systems_Extra_Credit ( %s ) values ( %s )" % (cols4, ec4)
        mycursor.execute(sql_qry, list(Systems_ec_hashmap.values()))

        ec5 =', '.join(['%s'] * len(Activities_ec_hashmap))
        cols5 = ', '.join(Activities_ec_hashmap.keys())
        sql_qry = "insert into Activities_Extra_Credit ( %s ) values ( %s )" % (cols5, ec5)
        mycursor.execute(sql_qry, list(Activities_ec_hashmap.values()))

        ec6 =', '.join(['%s'] * len(Chatbot_ec_hashmap))
        cols6 = ', '.join(Chatbot_ec_hashmap.keys())
        sql_qry = "insert into Chatbot_Extra_Credit ( %s ) values ( %s )" % (cols6, ec6)
        mycursor.execute(sql_qry, list(Chatbot_ec_hashmap.values()))


        mycursor.execute("drop view if exists user_pass_credentials")
        mycursor.execute("drop view if exists Headache")
        mycursor.execute("drop view if exists Medication")
        mycursor.execute("drop view if exists Personal_view_details")

        mycursor.execute("create view user_pass_credentials as select id, username, password, created_at from Patients")
        mycursor.execute("create view Headache (HeadacheId, HeadacheName, WokeupWith, Severity, Duration, Timestamp, Facility, MCycle) as select id, headache_name, wakeupornot, recordseverity, durationofheadache, created_at, usc_facility, if_female from Patients")
        mycursor.execute("create view Medication (MedicationID, MedicationName, NumberOfPills, Timestamp) as select id, medicinename, totalpills, created_at from Patients")
        mycursor.execute("create view Personal_view_details (id, Email, Phone, FName, LName, Secondary_Email, Password, Gender) as select id, email, phone, fname, lname, secondary_email, password, gender from Patients")




        # maintaining final changes [transaction ends here]
        # lock.release

        # mycursor.commit()


    if action == 'saving_last_thing_to_say':
        last_thing_to_say_hashmap = {}
        p = req.get('queryResult').get('parameters').get('last_thing_to_say')
        # hashmap["last_thing_to_say"] = p
        last_thing_to_say_hashmap["last_thing_to_say"] = p


    # return make_response(jsonify({"speech": res}))






@app.route('/user_login', methods=['GET', 'POST'])
def user_login():
    user_userName = request.values.get("uname", None)

    if user_userName in usernames_array:
        import matplotlib.pyplot as plt

        # headache_name // intensity_severity [scatter plot] - function of h_name ----------------------------------------------------------FIRST GRAPH
        colors = list("rgbcmyk")

        # to handle rewriting not appending [making a new image from scratch in order to delete the previous graph]
        plt.ion()
        fig = plt.figure()

        dict_ = usernames_headaches_intensity[user_userName] # within this list we have dictionaries [{}, {}, {}]
        for k in dict_:
            for x,y in k.items():
                ax = plt.scatter(x,y, color=colors.pop())
                plt.xlabel('Headaches', fontsize=14)
                plt.ylabel('Intensity/Severity', fontsize=14)
                plt.suptitle('Intensity per headache', fontsize=18)


        ax.figure.savefig('/home/sanyasin/mysite/static/image.png')
        fig.canvas.draw()
        fig.canvas.flush_events()


        # timestamp // intensity_severity [bar graph] - function of time -------------------------------------------------------------------SECOND GRAPH
        sql_select_Query = "select username, created_at, recordseverity from Patients"
        mycursor.execute(sql_select_Query)
        records = mycursor.fetchall()

        for row in records:
            temp = {}
            temp[row[1]] = row[2]
            if row[0] in usernames_timestamp_intensity:
                usernames_timestamp_intensity[row[0]].append(temp)
            else:
                usernames_timestamp_intensity[row[0]] = [temp]

        sql_select_Query = "select username, created_at, recordseverity from save_entries"
        mycursor.execute(sql_select_Query)
        records = mycursor.fetchall()

        for row in records:
            temp = {}
            temp[row[1]] = row[2]
            if row[0] in usernames_timestamp_intensity:
                usernames_timestamp_intensity[row[0]].append(temp)
            else:
                usernames_timestamp_intensity[row[0]] = [temp]


        plt.ion()
        fig1 = plt.figure()
        key_value_dict = {}
        key_value_dict[str(0)] = str(0)
        dict_1 = usernames_timestamp_intensity[user_userName]
        for k in dict_1:
            for x,y in k.items():
                key_value_dict[str(x)] = y


        keys = key_value_dict.keys()
        values = key_value_dict.values()

        plt.bar(keys, values)
        plt.ylim(bottom=0)
        plt.xlabel('TimeStamp', fontsize=14)
        plt.ylabel('Intensity/Severity', fontsize=14)
        plt.suptitle('Headache intensity as a function of time', fontsize=18)

        plt.savefig('/home/sanyasin/mysite/static/image1.png')
        fig1.canvas.draw()
        fig1.canvas.flush_events()



        # timestamp // no. of headaches [line graph]--------------------------------------------------------------------------------------------------THIRD GRAPH
        # usernames_timestamp_totalheads   -> {'sanya': {'0': '0'}, {10AM: 1}, {1PM: 2}}
        # usernames_totalheadaches -> {'sanya': 3, 'abc': 5}
        # usernames_timestampArray -> {'sanya': [1,3], 'abc': [4,2]}
        usernames_totalheadaches = {}
        usernames_timestampArray = {}

        sql_select_Query = "select username, created_at, headache_name from save_entries"
        mycursor.execute(sql_select_Query)
        records = mycursor.fetchall()

        for r in records:
            if r[0] in usernames_totalheadaches:
                usernames_totalheadaches[r[0]] += 1
                usernames_timestampArray[r[0]].append(r[1])
            else:
                usernames_totalheadaches[r[0]] = 1
                usernames_timestampArray[r[0]] = [r[1]]



        sql_select_Query = "select username, created_at, headache_name from Patients"
        mycursor.execute(sql_select_Query)
        records = mycursor.fetchall()

        for r in records:
            if r[0] in usernames_totalheadaches:
                usernames_totalheadaches[r[0]] += 1
                usernames_timestampArray[r[0]].append(r[1])
            else:
                usernames_totalheadaches[r[0]] = 1
                usernames_timestampArray[r[0]] = [r[1]]

        total_headaches_known = usernames_totalheadaches[user_userName]
        timestamps = usernames_timestampArray[user_userName]

        time_heads = {}
        time_heads['0'] = 0
        i = 1
        while i <= total_headaches_known:
            a = timestamps.pop(0)
            time_heads[str(a)] = i
            i+=1

        # time_heads ->>> final dictionary [start graph now]
        plt.ion()
        fig2 = plt.figure()

        x = list(time_heads.keys())
        y = list(time_heads.values())
        plt.plot(x, y, '-')


        plt.xlabel('TimeStamp', fontsize=14)
        plt.ylabel('No. of headaches', fontsize=14)
        plt.suptitle('No. of headaches as a function of time', fontsize=18)

        plt.savefig('/home/sanyasin/mysite/static/image2.png')
        fig2.canvas.draw()
        fig2.canvas.flush_events()



        # wakeupornot [yes and No] [pie chart]--------------------------------------------------------------------------------------------------FOURTH GRAPH
        usernames_wakeup_yesorno = {} # {'sanya': [yes,no,yes,yes,no]}
        sql_select_Query = "select username, wakeupornot from Patients"
        mycursor.execute(sql_select_Query)
        records = mycursor.fetchall()

        for r in records:
            if r[0] in usernames_wakeup_yesorno:
                usernames_wakeup_yesorno[r[0]].append(r[1])

            else:
                usernames_wakeup_yesorno[r[0]] = [r[1]]


        sql_select_Query = "select username, wakeupornot from save_entries"
        mycursor.execute(sql_select_Query)
        records = mycursor.fetchall()

        for r in records:
            if r[0] in usernames_totalheadaches:
                usernames_wakeup_yesorno[r[0]].append(r[1])
            else:
                usernames_wakeup_yesorno[r[0]] = [r[1]]


        main_array = usernames_wakeup_yesorno[user_userName]
        count_yes = 0
        count_no = 0
        for m in main_array:
            if m == 'yes':
                count_yes += 1
            else:
                count_no += 1

        # scaling values to 100% scale
        scaled_yes = (count_yes/(count_yes + count_no)) * 100
        scaled_no = (count_no/(count_yes + count_no)) * 100

        plt.ion()
        fig3 = plt.figure()

        labels = ['Yes', 'No']
        sizes = [scaled_yes, scaled_no]
        explode = (0, 0.1)
        plt.subplots()
        plt.pie(sizes, explode=explode, labels = labels, autopct = '%1.1f%%', shadow=True, startangle = 90)
        plt.axis('equal')


        plt.suptitle('Did the user wake up from this headache or not?', fontsize=15)

        plt.savefig('/home/sanyasin/mysite/static/image3.png')
        fig3.canvas.draw()
        fig3.canvas.flush_events()



        # headache_name // timeshappenedsincewokeup [bar graph]--------------------------------------------------------------------------------------------FIFTH GRAPH
        usernames_headache_timeshappenedsincyouewokeup = {} # {'sanya': [{headache_name: timeshappenedsinceyouwokeup}, {}, {}]}
        sql_select_Query = "select username, headache_name, timeshappenedsinceyouwokeup from Patients"
        mycursor.execute(sql_select_Query)
        records = mycursor.fetchall()

        for r in records:
            dict_ = {}
            dict_[r[1]] = r[2] # headache_name -> times_happened

            if r[0] in usernames_headache_timeshappenedsincyouewokeup:
                usernames_headache_timeshappenedsincyouewokeup[r[0]].append(dict_)

            else:
                usernames_headache_timeshappenedsincyouewokeup[r[0]] = [dict_]


        sql_select_Query = "select username, headache_name, timeshappenedsinceyouwokeup from save_entries"
        mycursor.execute(sql_select_Query)
        records = mycursor.fetchall()

        for r in records:
            dict_ = {}
            dict_[r[1]] = r[2]
            if r[0] in usernames_headache_timeshappenedsincyouewokeup:
                usernames_headache_timeshappenedsincyouewokeup[r[0]].append(dict_)
            else:
                usernames_headache_timeshappenedsincyouewokeup[r[0]] = [dict_]


        plt.ion()
        fig4 = plt.figure()
        key_value_dict = {}
        key_value_dict[str(0)] = str(0)
        dict_1 = usernames_headache_timeshappenedsincyouewokeup[user_userName]
        for k in dict_1:
            for x,y in k.items():
                key_value_dict[str(x)] = y


        keys = key_value_dict.keys()
        values = key_value_dict.values()

        plt.bar(keys, values)
        plt.ylim(bottom=0)
        plt.xlabel('headache_name', fontsize=14)
        plt.ylabel('Time happened since you woke up', fontsize=14)
        plt.suptitle('Time happened since the user woke up per headache', fontsize=15)

        plt.savefig('/home/sanyasin/mysite/static/image4.png')
        fig4.canvas.draw()
        fig4.canvas.flush_events()



        # headache_name // durationofheadache [intensity_severity] [scatter plot]-----------------------------------------------------------------------------------SIXTH GRAPH
        usernames_headache_durationhead_intensity = {} # {'sanya': [{head: [duration, intensity]}, {}, {}]}
        sql_select_Query = "select username, headache_name, durationofheadache, recordseverity from Patients"
        mycursor.execute(sql_select_Query)
        records = mycursor.fetchall()

        for r in records:
            dict_ = {}
            dict_[r[1]] = [r[2], r[3]] # {head -> [duration, intensity]}

            if r[0] in usernames_headache_durationhead_intensity:
                usernames_headache_durationhead_intensity[r[0]].append(dict_)
            else:
                usernames_headache_durationhead_intensity[r[0]] = [dict_]


        sql_select_Query = "select username, headache_name, durationofheadache, recordseverity from save_entries"
        mycursor.execute(sql_select_Query)
        records = mycursor.fetchall()

        for r in records:
            dict_ = {}
            dict_[r[1]] = [r[2], r[3]] # {head -> [duration, intensity]}

            if r[0] in usernames_headache_durationhead_intensity:
                usernames_headache_durationhead_intensity[r[0]].append(dict_)
            else:
                usernames_headache_durationhead_intensity[r[0]] = [dict_]


        plt.ion()
        fig5 = plt.figure()
        x_arr = []
        y_arr = []
        z_arr = []

        main_array = usernames_headache_durationhead_intensity[user_userName]
        for k in main_array:
            # k === {'head': [duration, intensity]}
            for x,y in k.items():
                # x is headaches
                x_arr.append(x)
                y_arr.append(y[0])
                z_arr.append(y[1])

        # use the scatter function
        index = 0
        while index < len(x_arr):
            plt.scatter(x_arr[index], y_arr[index])

            index +=1


        plt.xlabel('headache_name', fontsize=14)
        plt.ylabel('Duration of headache', fontsize=14)
        plt.suptitle('Duration of each headache', fontsize=18)

        plt.savefig('/home/sanyasin/mysite/static/image5.png')
        fig5.canvas.draw()
        fig5.canvas.flush_events()



        # create this - main user portal
        return render_template('user_visual_portal.html', title='Visualise data', to_print = usernames_timestamp_intensity)
    else:
        # create this
        return render_template('no_such_user_found.html')



@app.route('/users', methods=['GET', 'POST'])
def users():
    return render_template('user_portal.html')



@app.route('/login', methods=['GET', 'POST'])
def login():
    userName = request.values.get("uname", None)

    if userName in admin_usernames:
        usernames_set = set(usernames_array)
        return render_template('radio.html', title='List of users', members=usernames_set)
    else:
        return render_template('noadmin.html')


@app.route('/displayuser', methods=['GET', 'POST'])
def displayuser():
    targetUser = request.values.get("patients", None)

    # contain_usernames_only : from this we will find out it's id and access the details from patients table or from diff views
    # idd = contain_usernames_only[targetUser]
    details_to_print_in_hashmap_form = id_hashmap_array[contain_usernames_only[targetUser]] # array

    # have to result out the details of user"patient"i.e. targetUser
    return render_template("personalized.html", current_user_details = details_to_print_in_hashmap_form, userName = targetUser)


@app.route("/index", methods=["GET", "POST"])
def index():
    if request.method == "GET":
        # return render_template("main_login_choice_page.html")
        return render_template("login.html")

    # If the request isn't a "GET" (and so, we know it's a "POST" -- someone's clicked the "Post comment" button) then the next bit is executed:
    # comments.append(request.form["contents"])
    return redirect(url_for('index'))


@app.route("/suspend", methods=["GET", "POST"])
def suspend():
    user_to_suspend = request.values.get("suspend_user", None)
    # user_to_suspend -> means remove user from database
    # finding out 'id' - contain_usernames_only[user_to_suspend]
    if user_to_suspend in contain_usernames_only:
        idd = contain_usernames_only[user_to_suspend]
        delete_statement = "DELETE FROM Patients WHERE id = %s"
        mycursor.execute(delete_statement, (idd,))

        mycursor.execute("drop view if exists user_pass_credentials")
        mycursor.execute("drop view if exists Headache")
        mycursor.execute("drop view if exists Medication")
        mycursor.execute("drop view if exists Personal_view_details")

        mycursor.execute("create view user_pass_credentials as select id, username, password, created_at from Patients")
        mycursor.execute("create view Headache (HeadacheId, HeadacheName, WokeupWith, Severity, Duration, Timestamp, Facility, MCycle) as select id, headache_name, wakeupornot, recordseverity, durationofheadache, created_at, usc_facility, if_female from Patients")
        mycursor.execute("create view Medication (MedicationID, MedicationName, NumberOfPills, Timestamp) as select id, medicinename, totalpills, created_at from Patients")
        mycursor.execute("create view Personal_view_details (id, Email, Phone, FName, LName, Secondary_Email, Password, Gender) as select id, email, phone, fname, lname, secondary_email, password, gender from Patients")
    return render_template("suspend_message.html")


@app.route("/makeadmin", methods=["GET", "POST"])
def make_admin():
    user_to_make_admin = request.values.get("make_user_admin", None)
    admin_usernames.append(user_to_make_admin)

    return render_template("make_admin_message.html", user=user_to_make_admin)


@app.route("/revokeadmin", methods=["GET", "POST"])
def revoke_admin():
    user_to_revoke_admin = request.values.get("revoke_user_admin", None)
    admin_usernames.remove(user_to_revoke_admin)

    return render_template("revoke_admin_message.html", user=user_to_revoke_admin)


@app.route("/", methods=['GET', 'POST'])
def server():
    from flask import request

    # get SMS metadata
    msg_from = request.values.get("From", None)
    msg = request.values.get("Body", None)

    # prepare API.ai request
    req = ai.text_request()
    req.lang = 'en'
    req.query = msg
    # req.session_id = msg_from

    # get response from API.ai
    api_response = req.getresponse()
    responsestr = api_response.read().decode('utf-8')
    response_obj = json.loads(responsestr)
    reply="Hello [reply from flask]"

    if 'result' in response_obj:
        response = response_obj["result"]["fulfillment"]["speech"]
        # send SMS response back via twilio
        reply=client.messages.create(to=msg_from, from_= account_num, body=response)
    if 'queryResult' in response_obj:
        respp = response_obj['queryResult']['fulfillmentText']
        reply = client.messages.create(to=msg_from, from_=account_num, body=respp)

    return str(reply)


if __name__ == "__main__":
    app.run(debug=True)


