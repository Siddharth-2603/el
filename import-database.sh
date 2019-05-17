#!/bin/bash

# auto import mysql database
mysql -u admin -p gate_pass_system < database/gate-pass-system.sql
