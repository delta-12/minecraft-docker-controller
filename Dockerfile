FROM openjdk:17-jdk-alpine
RUN apk update
RUN apk add wget git nodejs
RUN mkdir /minecraft
WORKDIR /minecraft
RUN wget https://hub.spigotmc.org/jenkins/job/BuildTools/lastSuccessfulBuild/artifact/target/BuildTools.jar
RUN java -jar BuildTools.jar --rev latest
RUN java -jar spigot-*.jar
RUN rm eula.txt && echo "eula=true" > eula.txt
RUN printf "#!/bin/ash\n" >> start_server
RUN printf "java -jar %s\n" $(ls | grep spigot-*.jar) >> start_server
RUN chmod +x start_server
RUN wget -P plugins https://github.com/delta-12/MinecraftMongoDB/releases/download/v1.0.0/MinecraftMongoDB.jar
COPY wrapper.js wrapper.js
ENTRYPOINT ["node", "wrapper.js"]