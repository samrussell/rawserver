docker stop $(docker ps -aq)
docker rm $(docker ps -aq)
docker run -v `pwd`:/rawserver -p 8080:8080/udp -it rawserver bash