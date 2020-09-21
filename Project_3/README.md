# Project 4: Data Lake with Apache Spark on AWS

## Introduction
This project is part of the Udacity Data Engineer Nano Degree Program. The music streaming startup "Sparkify" has grown steadily and now wants a cloud data lake to store and query their user and song data on Amazon Web Services (AWS). Their data are stored as JSON files in S3 buckets on AWS. Their particular interest lies on what songs their customers are listening to, which is why they need an easy to query database.

The task is to access the raw data on S3, execute an ELT process to transform the data into different tables with Apache Spark on Amazon Elatic MapReduce (EMR), and store the resulting tables as .parquet files on S3, separated by certain criteria.

## Datasets

The collected data consist of mainly two file types both given as JSON files:

1. Log data, which provide user activity logs from a music streaming app (generated by this [Event Simulator](https://github.com/Interana/eventsim))
2. Song data, which provide metadata about a song and its artist (subset of real data from the [Million Song Dataset](http://millionsongdataset.com/))

Log data are stored under: ``S3://udacity-dend/log_data/*/*/*.json``
<br>Song data are stored under: ``S3://udacity-dend/song_data/*/*/*/*.json``

### Schema for Song Play Analysis

To ingest the data into the data lake, data of the raw JSON files are read from S3 and stored in four dimension tables and one fact table using Apache Spark. From there on, the tables are written into .parquet files and stored on S3, partitioned by the criteria given below.

The schema of each table is determined by Apache Spark during the reading process (Schema-On-Read).

#### Fact Table

1. ``songplays``: holds log data associated with song plays filtered using ``'NextSong'`` for page
    - songplay_id
    - start_time
    - user_id
    - level
    - song_id
    - artist_id
    - session_id
    - location
    - user_agent
    - year
    - month

The ``songplays`` table is partitioned by year and month during the storage as .parquet files.

#### Dimension Tables

1. ``users``: holds user data in app
    - user_id
    - firt_name
    - last_name
    - gender
    - level

2. ``songs``: holds songs in music library
    - song_id
    - title
    - artist_id
    - year
    - duration

The ``songs`` table is partitioned by ``year`` and ``artist_id`` during the storage as .parquet files.

3. ``artists``: holds artists in music library
    - artist_id
    - name
    - location
    - latitude
    - longitude

4. ``time``: holds timestamps of song plays separated into specific units
    - start_time
    - hour
    - day
    - week
    - month
    - year
    - weekday

The ``time`` table is partitioned by ``year`` and ``month`` during the storage as .parquet files.

## Program Structure

The following files are included for this project:

  1. ``dl.cfg``, used to parse your AWS key and secret key
  2. ``etl.py``, main program to initialize the data lake and ELT process

Mandatory python modules to run the scripts:

- pyspark
- configparser
- datetime
- os

Note: The solution to the project has been developed locally using only the python files (``.py``) in Python 3.6.10.

#### Instructions to run the program

To run the program, start with the following first step:

1. Insert your AWS user credentials into ``dl.cfg`` at empty spaces:
    ```
    [AWS]
    key =
    secret =
    ```

Now, there are two options to run the program:

2. RUNNING THE SCRIPT: Run ``etl.py`` in the terminal using: ``python etl.py``

This method will use your local Spark installation or, if using an EMR notebook, the EMR clusters Spark installation. This may take some time to complete if run on your local machine!

2. SUBMIT TO EMR CLUSTER: Submit ``etl.py`` to the cluster by using the following in the master-node terminal: ``spark-submit etl.py --master yarn``

This method will use Spark on an EMR cluster. Make sure that the IAM role has read/write access to S3 and that the .py file is located on the master-node (SSH/SCP required). You might have to locate and adjust the spark-submit statement by using ``which spark-submit`` in the master-node terminal. Make sure the hadoop-aws.jar is present, otherwise there will be errors running the script.

Note: For successfully running the script, you may need to adjust the ``pwd`` of your terminal to the folder where both ``etl.py`` and ``dl.cfg`` are stored.