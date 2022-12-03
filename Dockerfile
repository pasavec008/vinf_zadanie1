FROM iisas/hadoop-spark-pig-hive:2.9.2

WORKDIR /vinf_recipes

RUN apt-get update &&\
    apt-get -y install python3-pip &&\
    export PYSPARK_PYTHON=python3 &&\
    export PYTHONIOENCODING=utf8 &&\
    ln -sf /usr/bin/python3 /usr/bin/python &&\
    printf "export SPARK_DIST_CLASSPATH=\$(/usr/local/hadoop/bin/hadoop classpath)\n\
export SPARK_WORKER_MEMORY=4096m\n\
export SPARK_DAEMON_MEMORY=4096m\n\
export SPARK_WORKER_INSTANCES=4\n\
export SPARK_WORKER_CORES=8" > '/usr/local/spark-2.4.3-bin-without-hadoop-scala-2.12/conf/spark-env.sh' &&\
    /usr/local/spark-2.4.3-bin-without-hadoop-scala-2.12/sbin/stop-slaves.sh &&\
    /usr/local/spark-2.4.3-bin-without-hadoop-scala-2.12/sbin/start-slaves.sh

COPY ./requirements.txt .
RUN pip3 install -r requirements.txt

WORKDIR /usr/local/spark/jars
RUN wget https://repo1.maven.org/maven2/com/databricks/spark-xml_2.11/0.9.0/spark-xml_2.11-0.9.0.jar