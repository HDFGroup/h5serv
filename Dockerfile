FROM hdfgroup/hdf5lib:1.8.16
MAINTAINER John Readey <jreadey@hdfgroup.org>
RUN cd /usr/local/src                                    ; \
    pip install --upgrade pip                            ; \
    pip install tornado                                  ; \
    pip install requests                                 ; \
    pip install pytz                                     ; \
    pip install watchdog                                 ; \
    pip install pymongo       
WORKDIR /usr/local/src         
RUN git clone https://github.com/HDFGroup/hdf5-json.git  ; \
    cd hdf5-json                                         ; \
    python setup.py install                              ; \
    cd ..                                                ; \
    mkdir h5serv       
WORKDIR /usr/local/src/h5serv                                                          
COPY server server                                       
COPY util util                                         
COPY test test                                        
COPY data /data                                         
RUN  ln -s /data 
                              
EXPOSE 5000 

COPY entrypoint.sh /

ENTRYPOINT ["/entrypoint.sh"]

