# Java UPSS Implementation

This example demonstrates how to implement the Universal Prompt Security Standard (UPSS) in a Java application using Spring Boot.

## Structure

```
java/
├── src/
│   └── main/
│       ├── java/com/upss/
│       │   ├── UPSSLoader.java
│       │   ├── UPSSValidator.java
│       │   └── Application.java
│       └── resources/
│           ├── upss_config.yaml
│           └── prompts/
│               ├── system/
│               └── user/
├── pom.xml
└── README.md
```

## Prerequisites

- Java 11 or higher
- Maven 3.6 or higher

## Installation

```bash
mvn clean install
```

## Quick Start

### 1. Run the Application

```bash
mvn spring-boot:run
```

### 2. Access the API

```bash
curl http://localhost:8080/api/prompts
```

### 3. Validate Configuration

```bash
mvn exec:java -Dexec.mainClass="com.upss.UPSSValidator" -Dexec.args="src/main/resources/upss_config.yaml"
```

## Key Features

- **Spring Boot Integration**: RESTful API endpoints
- **YAML Configuration**: SnakeYAML for parsing
- **Validation Framework**: Comprehensive configuration validation
- **Caching**: In-memory caching with Caffeine
- **Audit Logging**: SLF4J logging integration
- **Maven Plugin**: Build-time validation

## Testing

```bash
mvn test
```

## Integration

Add to your `pom.xml`:

```xml
<dependency>
    <groupId>org.yaml</groupId>
    <artifactId>snakeyaml</artifactId>
    <version>2.0</version>
</dependency>
```

## License

See [LICENSE](../../LICENSE) for details.
