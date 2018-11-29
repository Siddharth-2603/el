from NonUI.src.config import *

import mysql.connector
import datetime
import re
import os
import xlsxwriter
import socket, fcntl, struct, io

class GatePassSystem:
    flagError = False
    errMessage = ""

    def __init__(self):
        self.db = self.connect_to_database()
        if self.flagError == False:
            self.db_cursor = self.db.cursor(buffered=True)

    def connect_to_database(self):
        try:
            db = mysql.connector.connect(
                host=host,
                user=username,
                passwd=password,
                database=db_name,
                unix_socket=unix_socket
            )
            return db
        except mysql.connector.Error as err:
            self.flagError = True
            self.errMessage = err
            return self.flagError

    def has_been_registered(self, uid):
        try:
            sql = "SELECT id FROM members WHERE uid = " + str(uid)
            self.db_cursor.execute(sql)
            member_id = self.db_cursor.fetchone()
            if member_id is not None:
                return True
            else:
                return False
        except mysql.connector.Error as err:
            self.flagError = True
            self.errMessage = err
            return self.flagError

    def get_current_datetime(self):
        return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def insert_data_to_database(self, uid, name, expired_dt):
        if self.flagError == False:
            try:
                # get Gate ID first
                gate_id = -1
                ip_address_device = self.get_ip_address()

                if ip_address_device != '':
                    sql = "SELECT id FROM gates WHERE ip_address = '" + str(ip_address_device) + "';"
                    self.db_cursor.execute(sql)
                    gate_id = self.db_cursor.fetchone()[0]

                if gate_id != -1:
                    # insert data into 'members' table
                    current_dt = self.get_current_datetime()
                    sql = "INSERT INTO members (uid, name, expired_dt, created, modified) VALUES (%s, %s, %s, %s, %s)"
                    value = (uid, name, expired_dt, current_dt, current_dt)
                    self.db_cursor.execute(sql, value)
                    self.db.commit()

                    # insert data into 'member_details' table
                    sql = "INSERT INTO member_details (member_id, gate_id, created, modified) VALUES (LAST_INSERT_ID(), %s, %s, %s)"
                    value = (gate_id, current_dt, current_dt)
                    self.db_cursor.execute(sql, value)
                    self.db.commit()

                    message = "Register Success."
                    print(message)
                    return message
                else:
                    message = "Error : Invalid Gate ID."
                    print(message)
                    return message
            except mysql.connector.Error as err:
                self.flagError = True
                self.errMessage = err
                print(err)
                return self.errMessage
        else:
            return "Error : cannot connect to database."

    def check_validity(self, code):
        try:
            # check if UID is registered
            sql = "SELECT id FROM members WHERE uid = '" + str(code) + "';"
            self.db_cursor.execute(sql)
            member_id = self.db_cursor.fetchone()

            # if UID registered, then check expired date
            if member_id is not None:
                member_id = member_id[0]
                sql = "SELECT id FROM members WHERE id = " + str(member_id) + " AND NOW() <= expired_dt;"
                self.db_cursor.execute(sql)
                member_id = self.db_cursor.fetchone()
                if member_id is not None and member_id != "":
                    message = "UID is valid"
                    print(message)
                    return message
                else:
                    self.errMessage = "UID is expired."
                    print(self.errMessage)
                    return self.errMessage
            else:
                self.errMessage = "UID is not registered yet."
                print(self.errMessage)
                return self.errMessage
        except mysql.connector.Error as err:
            self.flagError = True
            self.errMessage = err
            print(err)
            return self.errMessage

    def get_ip_address(self, ifname=''):
        if self.is_raspberry_pi():
            ifname = "eth0"
        else:
            ifname = "enp3s0"
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        ip_address = socket.inet_ntoa(fcntl.ioctl(
            s.fileno(),
            0x8915,  # SIOCGIFADDR
            struct.pack('256s', bytes(ifname[:15], 'utf-8'))
        )[20:24])
        return str(ip_address)

    def is_raspberry_pi(self, raise_on_errors=False):
        try:
            with io.open('/proc/cpuinfo', 'r') as cpuinfo:
                found = False
                for line in cpuinfo:
                    if line.startswith('Hardware'):
                        found = True
                        label, value = line.strip().split(':', 1)
                        value = value.strip()
                        if value not in (
                                'BCM2708',
                                'BCM2709',
                                'BCM2835',
                                'BCM2836'
                        ):
                            if raise_on_errors:
                                raise ValueError(
                                    'This system does not appear to be a '
                                    'Raspberry Pi.'
                                )
                            else:
                                return False
                if not found:
                    if raise_on_errors:
                        raise ValueError(
                            'Unable to determine if this system is a Raspberry Pi.'
                        )
                    else:
                        return False
        except IOError:
            if raise_on_errors:
                raise ValueError('Unable to open `/proc/cpuinfo`.')
            else:
                return False
        return True