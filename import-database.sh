#!/bin/bash

# auto import mysql database
mysqldump -u root -p gate_pass_system < database/gate-pass-system.sql
