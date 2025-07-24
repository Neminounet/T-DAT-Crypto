FROM maven:3.9.9-eclipse-temurin-17 AS build
WORKDIR /app

# Copier le fichier pom.xml et télécharger les dépendances
COPY pom.xml .
RUN mvn dependency:go-offline

# Copier le reste du code source
COPY src ./src

# Construire l'application (en skippant les tests)
RUN mvn package -DskipTests

# Étape d'exécution
FROM eclipse-temurin:17-jre-jammy
WORKDIR /app

# Copier le fichier JAR depuis l'étape de construction
COPY --from=build /app/target/*.jar app.jar

# Exposer le port 8080
EXPOSE 8080

# Définir les variables d'environnement pour Java
ENV JAVA_OPTS=""

# Démarrer l'application
ENTRYPOINT ["sh", "-c", "java $JAVA_OPTS -jar app.jar"]
